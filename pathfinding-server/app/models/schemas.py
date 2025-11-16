"""
Pydantic 스키마 정의 (API 요청/응답용)
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
from .enums import MapType, MapStatus, PathDifficulty


# ===== 지도 관련 스키마 =====
class MapUploadRequest(BaseModel):
    """지도 업로드 요청"""
    name: str = Field(..., description="지도 이름")
    description: Optional[str] = Field(None, description="지도 설명")
    map_type: MapType = Field(MapType.OTHER, description="지도 유형")
    scale_meters_per_pixel: float = Field(1.0, description="1픽셀당 실제 거리(미터)")


class MapResponse(BaseModel):
    """지도 응답"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str]
    map_type: str
    width: int
    height: int
    scale_meters_per_pixel: float
    preprocessing_status: str
    original_image_url: Optional[str] = None
    processed_image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class MapPreprocessingRequest(BaseModel):
    """지도 전처리 요청"""
    force_reprocess: bool = Field(False, description="기존 전처리 데이터 무시하고 재처리")
    algorithm: str = Field("auto", description="사용할 알고리즘 (auto, manual)")
    options: Dict[str, Any] = Field(default_factory=dict, description="알고리즘별 옵션")


class MapPreprocessingResponse(BaseModel):
    """지도 전처리 응답"""
    map_id: str
    status: str
    processing_time: float
    walkable_area_percentage: float
    detected_obstacles: int
    detected_entrances: int
    message: str


# ===== 길찾기 관련 스키마 =====
class PathfindingRequest(BaseModel):
    """길찾기 요청"""
    map_id: str = Field(..., description="지도 ID")
    start: Tuple[float, float] = Field(..., description="시작 위치 (정규화된 좌표 0-1)")
    end: Tuple[float, float] = Field(..., description="종료 위치 (정규화된 좌표 0-1)")
    waypoints: Optional[List[Tuple[float, float]]] = Field(None, description="경유지 리스트")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="추가 옵션")


class PathMetadata(BaseModel):
    """경로 메타데이터"""
    distance_pixels: float
    distance_meters: float
    estimated_time_seconds: float
    difficulty: PathDifficulty
    accessibility_score: float
    turn_count: int


class PathfindingResponse(BaseModel):
    """길찾기 응답"""
    path_id: str
    map_id: str
    polyline: List[Tuple[float, float]] = Field(..., description="정규화된 좌표 리스트")
    svg_path: str = Field(..., description="SVG 경로 문자열")
    metadata: PathMetadata
    alternatives: Optional[List['PathfindingResponse']] = None
    cached: bool = False
    processing_time: float


class MultiPathfindingRequest(BaseModel):
    """다중 경로 요청 (여러 경유지)"""
    map_id: str
    points: List[Tuple[float, float]] = Field(..., min_length=2, description="방문할 지점들")
    optimize_order: bool = Field(False, description="최적 순서로 재정렬")
    return_to_start: bool = Field(False, description="시작점으로 복귀")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)


# ===== 장애물/편집 관련 스키마 =====
class ObstacleUpdate(BaseModel):
    """장애물 업데이트"""
    add_obstacles: Optional[List[Dict[str, Any]]] = Field(None, description="추가할 장애물")
    remove_obstacles: Optional[List[str]] = Field(None, description="제거할 장애물 ID")
    clear_all: bool = Field(False, description="모든 장애물 제거")


class WalkableAreaUpdate(BaseModel):
    """보행 가능 영역 업데이트"""
    polygons: List[List[Tuple[float, float]]] = Field(..., description="보행 가능 영역 폴리곤")
    mode: str = Field("add", description="add, replace, remove")


# ===== 상태/헬스체크 스키마 =====
class HealthResponse(BaseModel):
    """헬스체크 응답"""
    status: str
    version: str
    database: str
    redis: str
    storage: str
    ml_models_loaded: bool