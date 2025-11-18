"""
길찾기 관련 API 엔드포인트
Phase 2의 핵심 기능 - A* 알고리즘 기반 경로 찾기
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import (
    PathfindingRequest,
    PathfindingResponse,
    MultiPathfindingRequest,
    PathMetadata,
    ValidatePointRequest,
    ValidatePointResponse
)
from app.models.enums import PathDifficulty
from app.services.pathfinding_service import PathfindingService
from app.api.dependencies import get_db
from app.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pathfinding", tags=["pathfinding"])

# 서비스 인스턴스 생성
pathfinding_service = PathfindingService(storage_path=settings.storage_path)


@router.post("/route", response_model=PathfindingResponse)
async def find_route(
    request: PathfindingRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    두 지점 사이의 최적 경로 찾기

    A* 알고리즘을 사용하여 시작점과 종료점 사이의 최적 경로를 계산합니다.

    **입력:**
    - map_id: 지도 ID
    - start: 시작 좌표 (0-1 정규화)
    - end: 종료 좌표 (0-1 정규화)
    - options: 추가 옵션

    **출력:**
    - polyline: 경로 좌표 리스트
    - svg_path: SVG 경로 문자열
    - distance: 거리 정보
    - estimated_time: 예상 시간
    """
    try:
        print(request)
        # 좌표 검증
        if not (0 <= request.start[0] <= 1 and 0 <= request.start[1] <= 1):
            raise ValueError("시작 좌표는 0-1 범위여야 합니다")
        if not (0 <= request.end[0] <= 1 and 0 <= request.end[1] <= 1):
            raise ValueError("종료 좌표는 0-1 범위여야 합니다")

        # 경로 찾기
        result = await pathfinding_service.find_route(
            db=db,
            map_id=request.map_id,
            start=request.start,
            end=request.end,
            options=request.options
        )

        if not result.get('success'):
            raise HTTPException(
                status_code=404,
                detail=result.get('error', '경로를 찾을 수 없습니다')
            )

        # 응답 생성
        metadata = PathMetadata(
            distance_pixels=result['distance_pixels'],
            distance_meters=result['distance_meters'],
            estimated_time_seconds=result['estimated_time_seconds'],
            difficulty=PathDifficulty(result['difficulty']),
            accessibility_score=result['accessibility_score'],
            turn_count=result['turn_count']
        )

        return PathfindingResponse(
            path_id=result['path_id'],
            map_id=result['map_id'],
            polyline=result['polyline'],
            svg_path=result['svg_path'],
            metadata=metadata,
            cached=result.get('cached', False),
            processing_time=result['processing_time']
        )

    except ValueError as e:
        logger.error(f"입력 검증 오류: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"경로 찾기 오류: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"경로 찾기 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/multi-route")
async def find_multi_route(
    request: MultiPathfindingRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    여러 지점을 경유하는 경로 찾기

    여러 웨이포인트를 순서대로 방문하는 경로를 계산합니다.

    **입력:**
    - map_id: 지도 ID
    - points: 방문할 지점들 (최소 2개)
    - optimize_order: 경유 순서 최적화 여부
    - return_to_start: 시작점으로 복귀 여부

    **출력:**
    - segments: 각 구간별 경로 정보
    - combined_polyline: 전체 경로
    - total_distance: 총 거리
    - total_time: 총 예상 시간
    """
    try:
        # 좌표 검증
        for i, point in enumerate(request.points):
            if not (0 <= point[0] <= 1 and 0 <= point[1] <= 1):
                raise ValueError(f"지점 {i+1}의 좌표는 0-1 범위여야 합니다")

        # 다중 경로 찾기
        result = await pathfinding_service.find_multi_route(
            db=db,
            map_id=request.map_id,
            points=request.points,
            options={
                'optimize_order': request.optimize_order,
                'return_to_start': request.return_to_start,
                **request.options
            }
        )

        if not result.get('success'):
            raise HTTPException(
                status_code=404,
                detail=result.get('error', '경로를 찾을 수 없습니다')
            )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"다중 경로 찾기 오류: {e}")
        raise HTTPException(status_code=500, detail="경로 찾기 중 오류가 발생했습니다")


@router.get("/alternatives")
async def find_alternative_routes(
    map_id: str,
    start_x: float = Query(..., ge=0, le=1, description="시작 X 좌표 (0-1)"),
    start_y: float = Query(..., ge=0, le=1, description="시작 Y 좌표 (0-1)"),
    end_x: float = Query(..., ge=0, le=1, description="종료 X 좌표 (0-1)"),
    end_y: float = Query(..., ge=0, le=1, description="종료 Y 좌표 (0-1)"),
    max_alternatives: int = Query(3, ge=1, le=5, description="최대 대체 경로 수"),
    db: AsyncSession = Depends(get_db)
):
    """
    대체 경로 찾기

    메인 경로와 함께 여러 대체 경로를 제공합니다.

    **쿼리 파라미터:**
    - map_id: 지도 ID
    - start_x, start_y: 시작 좌표
    - end_x, end_y: 종료 좌표
    - max_alternatives: 최대 대체 경로 수 (1-5)

    **출력:**
    - main_route: 최적 경로
    - alternatives: 대체 경로 리스트
    """
    try:
        result = await pathfinding_service.find_alternative_routes(
            db=db,
            map_id=map_id,
            start=(start_x, start_y),
            end=(end_x, end_y),
            max_alternatives=max_alternatives
        )

        if not result.get('success'):
            raise HTTPException(
                status_code=404,
                detail="대체 경로를 찾을 수 없습니다"
            )

        return result

    except Exception as e:
        logger.error(f"대체 경로 찾기 오류: {e}")
        raise HTTPException(status_code=500, detail="경로 찾기 중 오류가 발생했습니다")


@router.get("/history/{map_id}")
async def get_pathfinding_history(
    map_id: str,
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    특정 지도의 길찾기 기록 조회

    **경로 파라미터:**
    - map_id: 지도 ID

    **쿼리 파라미터:**
    - limit: 조회할 최대 기록 수

    **출력:**
    - 최근 길찾기 요청 기록
    """
    try:
        from sqlalchemy import select
        from app.models.database import PathfindingRequest as PathfindingRequestModel

        result = await db.execute(
            select(PathfindingRequestModel)
            .where(PathfindingRequestModel.map_id == map_id)
            .order_by(PathfindingRequestModel.created_at.desc())
            .limit(limit)
        )

        history = result.scalars().all()

        return {
            'map_id': map_id,
            'total': len(history),
            'history': [
                {
                    'id': h.id,
                    'start': (h.start_x, h.start_y),
                    'end': (h.end_x, h.end_y),
                    'distance_meters': h.distance_meters,
                    'processing_time': h.processing_time,
                    'cached': h.is_cached,
                    'created_at': h.created_at
                }
                for h in history
            ]
        }

    except Exception as e:
        logger.error(f"기록 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="기록 조회 중 오류가 발생했습니다")


@router.delete("/cache/{map_id}")
async def clear_cache(
    map_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    특정 지도의 경로 캐시 삭제

    **경로 파라미터:**
    - map_id: 지도 ID

    **출력:**
    - 삭제된 캐시 항목 수
    """
    try:
        # 메모리 캐시 삭제 (실제로는 Redis 사용 권장)
        cleared = 0
        keys_to_remove = []

        for key in pathfinding_service.cache.keys():
            if map_id in key:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del pathfinding_service.cache[key]
            cleared += 1

        return {
            'success': True,
            'map_id': map_id,
            'cleared_items': cleared,
            'message': f"{cleared}개의 캐시 항목이 삭제되었습니다"
        }

    except Exception as e:
        logger.error(f"캐시 삭제 오류: {e}")
        raise HTTPException(status_code=500, detail="캐시 삭제 중 오류가 발생했습니다")


@router.post("/validate-point", response_model=ValidatePointResponse)
async def validate_point(
    request: ValidatePointRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    좌표 검증 및 자동 보정

    사용자가 클릭한 좌표가 장애물 위에 있는지 확인하고,
    장애물이면 가장 가까운 보행 가능 지점으로 자동 보정합니다.

    **입력:**
    - map_id: 지도 ID
    - point: 검증할 좌표 (0-1 정규화)

    **출력:**
    - is_valid: 원래 좌표가 보행 가능한지
    - original_point: 원래 좌표
    - adjusted_point: 보정된 좌표 (필요시)
    - was_adjusted: 보정 여부
    - adjustment_distance: 보정 거리 (픽셀)
    """
    try:
        # 좌표 검증 및 보정
        result = await pathfinding_service.validate_and_adjust_point(
            db=db,
            map_id=request.map_id,
            point=request.point
        )

        return ValidatePointResponse(
            is_valid=result['is_valid'],
            original_point=result['original_point'],
            adjusted_point=result['adjusted_point'],
            was_adjusted=result['was_adjusted'],
            adjustment_distance=result.get('adjustment_distance')
        )

    except ValueError as e:
        logger.error(f"좌표 검증 오류: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"좌표 검증 처리 오류: {e}")
        raise HTTPException(status_code=500, detail="좌표 검증 중 오류가 발생했습니다")