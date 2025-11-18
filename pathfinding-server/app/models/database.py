"""
데이터베이스 모델 정의
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class Map(Base):
    """지도 정보를 저장하는 테이블"""
    __tablename__ = "maps"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    map_type = Column(String(50), nullable=False, default="other")

    # 이미지 정보
    original_image_path = Column(String(500), nullable=False)
    processed_image_path = Column(String(500), nullable=True)
    thumbnail_path = Column(String(500), nullable=True)

    # 이미지 메타데이터
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    scale_meters_per_pixel = Column(Float, default=1.0)  # 1픽셀당 실제 거리(미터)

    # 전처리 정보
    preprocessing_status = Column(String(50), default="uploaded")
    preprocessing_metadata = Column(JSON, nullable=True)  # 전처리 관련 추가 정보
    walkable_areas = Column(JSON, nullable=True)  # 보행 가능 영역 정보
    obstacles = Column(JSON, nullable=True)  # 장애물 정보

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    pathfinding_requests = relationship("PathfindingRequest", back_populates="map")
    preprocessed_data = relationship("PreprocessedMapData", back_populates="map", uselist=False)


class PreprocessedMapData(Base):
    """전처리된 맵 데이터 (Phase 1의 핵심)"""
    __tablename__ = "preprocessed_map_data"

    id = Column(String, primary_key=True, default=generate_uuid)
    map_id = Column(String, ForeignKey("maps.id"), nullable=False)

    # 전처리된 이미지 경로들
    binary_image_path = Column(String(500), nullable=True)  # 이진화된 이미지
    edge_image_path = Column(String(500), nullable=True)  # 엣지 검출 이미지
    segmented_image_path = Column(String(500), nullable=True)  # 세그멘테이션된 이미지

    # 그래프 데이터 (길찾기용)
    graph_data = Column(JSON, nullable=True)  # 노드와 엣지 정보
    walkable_grid = Column(JSON, nullable=True)  # 2D 그리드 (0: 장애물, 1: 보행가능)

    # 특징점 정보
    entrance_points = Column(JSON, nullable=True)  # 입구 위치들
    poi_points = Column(JSON, nullable=True)  # 주요 관심 지점들

    # 처리 정보
    processing_time = Column(Float, nullable=True)  # 처리 시간(초)
    algorithm_used = Column(String(100), nullable=True)  # 사용된 알고리즘

    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계
    map = relationship("Map", back_populates="preprocessed_data")


class PathfindingRequest(Base):
    """길찾기 요청 기록"""
    __tablename__ = "pathfinding_requests"

    id = Column(String, primary_key=True, default=generate_uuid)
    map_id = Column(String, ForeignKey("maps.id"), nullable=False)

    # 요청 정보
    start_x = Column(Float, nullable=False)  # 정규화된 좌표 (0-1)
    start_y = Column(Float, nullable=False)
    end_x = Column(Float, nullable=False)
    end_y = Column(Float, nullable=False)

    waypoints = Column(JSON, nullable=True)  # 경유지 리스트
    options = Column(JSON, nullable=True)  # 추가 옵션

    # 결과
    result_path = Column(JSON, nullable=True)  # 계산된 경로
    svg_path = Column(Text, nullable=True)  # SVG 경로 문자열
    distance_pixels = Column(Float, nullable=True)
    distance_meters = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)

    # 캐싱
    cache_key = Column(String(255), nullable=True)
    is_cached = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계
    map = relationship("Map", back_populates="pathfinding_requests")


class ApiKey(Base):
    """API 키 관리 테이블"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(6), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    usage_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)

    # 관계
    api_usage = relationship("ApiUsage", back_populates="api_key", cascade="all, delete-orphan")
    user_images = relationship("UserImage", back_populates="api_key", cascade="all, delete-orphan")


class ApiUsage(Base):
    """API 사용량 추적 테이블"""
    __tablename__ = "api_usage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint = Column(String(255), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    request_data = Column(JSON, nullable=True)
    user_agent = Column(String(255), nullable=True)

    # 관계
    api_key = relationship("ApiKey", back_populates="api_usage")


class UserImage(Base):
    """사용자 업로드 이미지 관리 테이블"""
    __tablename__ = "user_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id", ondelete="CASCADE"), nullable=False, index=True)
    map_id = Column(String, ForeignKey("maps.id", ondelete="CASCADE"), nullable=False, index=True)
    upload_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)

    # 관계
    api_key = relationship("ApiKey", back_populates="user_images")
    map = relationship("Map")