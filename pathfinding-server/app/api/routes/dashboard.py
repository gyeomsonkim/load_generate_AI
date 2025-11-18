"""
Dashboard 관련 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from datetime import datetime, timedelta
from typing import List, Optional
import logging
import random

from app.models.schemas import (
    DashboardStatsResponse,
    UsageStats,
    HourlyUsage,
    DailyUsage,
    EndpointUsage,
    UserImageInfo,
    ApiKeyInfo,
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    MapInfo
)
from app.models.database import ApiKey, ApiUsage, UserImage, Map
from app.api.dependencies import get_db
from app.api.dependencies_auth import verify_api_key

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_api_key: ApiKey = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Dashboard 통계 조회

    현재 API 키의 종합 사용량 통계를 반환합니다.

    **Headers:**
    - X-API-Key: API 키 (필수)

    **출력:**
    - usage: 전체 사용량 통계
    - hourly_usage: 최근 24시간 사용량
    - daily_usage: 최근 7일 사용량
    - endpoint_usage: 엔드포인트별 사용량
    - recent_uploads: 최근 업로드 이미지 (6개)
    """
    try:
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)

        # === 전체 사용량 통계 ===
        total_calls_result = await db.execute(
            select(func.count(ApiUsage.id))
            .where(ApiUsage.api_key_id == current_api_key.id)
        )
        total_calls = total_calls_result.scalar() or 0

        calls_today_result = await db.execute(
            select(func.count(ApiUsage.id))
            .where(
                and_(
                    ApiUsage.api_key_id == current_api_key.id,
                    ApiUsage.timestamp >= today_start
                )
            )
        )
        calls_today = calls_today_result.scalar() or 0

        calls_week_result = await db.execute(
            select(func.count(ApiUsage.id))
            .where(
                and_(
                    ApiUsage.api_key_id == current_api_key.id,
                    ApiUsage.timestamp >= week_start
                )
            )
        )
        calls_this_week = calls_week_result.scalar() or 0

        calls_month_result = await db.execute(
            select(func.count(ApiUsage.id))
            .where(
                and_(
                    ApiUsage.api_key_id == current_api_key.id,
                    ApiUsage.timestamp >= month_start
                )
            )
        )
        calls_this_month = calls_month_result.scalar() or 0

        # 가장 많이 사용된 엔드포인트
        most_used_result = await db.execute(
            select(
                ApiUsage.endpoint,
                func.count(ApiUsage.id).label('count')
            )
            .where(ApiUsage.api_key_id == current_api_key.id)
            .group_by(ApiUsage.endpoint)
            .order_by(desc('count'))
            .limit(1)
        )
        most_used_row = most_used_result.first()
        most_used_endpoint = most_used_row[0] if most_used_row else None

        # 평균 응답 시간
        avg_response_result = await db.execute(
            select(func.avg(ApiUsage.response_time_ms))
            .where(ApiUsage.api_key_id == current_api_key.id)
        )
        average_response_time_ms = avg_response_result.scalar() or 0.0

        # 성공률 (2xx, 3xx 상태 코드)
        success_result = await db.execute(
            select(func.count(ApiUsage.id))
            .where(
                and_(
                    ApiUsage.api_key_id == current_api_key.id,
                    ApiUsage.status_code < 400
                )
            )
        )
        success_count = success_result.scalar() or 0
        success_rate = (success_count / total_calls * 100) if total_calls > 0 else 100.0

        usage_stats = UsageStats(
            total_calls=total_calls,
            calls_today=calls_today,
            calls_this_week=calls_this_week,
            calls_this_month=calls_this_month,
            most_used_endpoint=most_used_endpoint,
            average_response_time_ms=round(average_response_time_ms, 2),
            success_rate=round(success_rate, 2)
        )

        # === 시간별 사용량 (최근 24시간) ===
        hourly_usage_list = []
        for i in range(24):
            hour_start = today_start - timedelta(hours=23-i)
            hour_end = hour_start + timedelta(hours=1)

            count_result = await db.execute(
                select(func.count(ApiUsage.id))
                .where(
                    and_(
                        ApiUsage.api_key_id == current_api_key.id,
                        ApiUsage.timestamp >= hour_start,
                        ApiUsage.timestamp < hour_end
                    )
                )
            )
            count = count_result.scalar() or 0
            hourly_usage_list.append(HourlyUsage(hour=hour_start, count=count))

        # === 일별 사용량 (최근 7일) ===
        daily_usage_list = []
        for i in range(7):
            day_start = today_start - timedelta(days=6-i)
            day_end = day_start + timedelta(days=1)

            count_result = await db.execute(
                select(func.count(ApiUsage.id))
                .where(
                    and_(
                        ApiUsage.api_key_id == current_api_key.id,
                        ApiUsage.timestamp >= day_start,
                        ApiUsage.timestamp < day_end
                    )
                )
            )
            count = count_result.scalar() or 0
            daily_usage_list.append(
                DailyUsage(
                    date=day_start.strftime("%Y-%m-%d"),
                    count=count
                )
            )

        # === 엔드포인트별 사용량 ===
        endpoint_usage_result = await db.execute(
            select(
                ApiUsage.endpoint,
                func.count(ApiUsage.id).label('count'),
                func.avg(ApiUsage.response_time_ms).label('avg_time')
            )
            .where(ApiUsage.api_key_id == current_api_key.id)
            .group_by(ApiUsage.endpoint)
            .order_by(desc('count'))
            .limit(10)
        )

        endpoint_usage_list = []
        for row in endpoint_usage_result:
            endpoint_usage_list.append(
                EndpointUsage(
                    endpoint=row[0],
                    count=row[1],
                    average_response_time_ms=round(row[2], 2) if row[2] else 0.0
                )
            )

        # === 최근 업로드 이미지 (6개) ===
        recent_uploads_result = await db.execute(
            select(UserImage, Map)
            .join(Map, UserImage.map_id == Map.id)
            .where(
                and_(
                    UserImage.api_key_id == current_api_key.id,
                    UserImage.is_deleted == False
                )
            )
            .order_by(desc(UserImage.upload_timestamp))
            .limit(6)
        )

        recent_uploads_list = []
        for user_image, map_obj in recent_uploads_result:
            map_info = MapInfo(
                id=map_obj.id,
                name=map_obj.name,
                map_type=map_obj.map_type,
                preprocessing_status=map_obj.preprocessing_status,
                created_at=map_obj.created_at,
                original_image_url=f"/media/maps/{map_obj.id}/original.jpg",
                processed_image_url=f"/media/maps/{map_obj.id}/processed.jpg" if map_obj.processed_image_path else None,
                width=map_obj.width,
                height=map_obj.height,
                scale_meters_per_pixel=map_obj.scale_meters_per_pixel
            )

            user_image_info = UserImageInfo(
                id=user_image.id,
                api_key_id=user_image.api_key_id,
                map_id=user_image.map_id,
                upload_timestamp=user_image.upload_timestamp,
                is_deleted=user_image.is_deleted,
                map=map_info
            )
            recent_uploads_list.append(user_image_info)

        return DashboardStatsResponse(
            usage=usage_stats,
            hourly_usage=hourly_usage_list,
            daily_usage=daily_usage_list,
            endpoint_usage=endpoint_usage_list,
            recent_uploads=recent_uploads_list
        )

    except Exception as e:
        logger.error(f"Dashboard 통계 조회 오류: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Dashboard 통계 조회 중 오류가 발생했습니다"
        )


@router.get("/images", response_model=List[UserImageInfo])
async def get_user_images(
    current_api_key: ApiKey = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    사용자 업로드 이미지 목록 조회

    현재 API 키로 업로드한 모든 이미지 목록을 반환합니다.

    **Headers:**
    - X-API-Key: API 키 (필수)

    **출력:**
    - 업로드 이미지 목록 (최신순)
    """
    try:
        result = await db.execute(
            select(UserImage, Map)
            .join(Map, UserImage.map_id == Map.id)
            .where(
                and_(
                    UserImage.api_key_id == current_api_key.id,
                    UserImage.is_deleted == False
                )
            )
            .order_by(desc(UserImage.upload_timestamp))
        )

        images_list = []
        for user_image, map_obj in result:
            map_info = MapInfo(
                id=map_obj.id,
                name=map_obj.name,
                map_type=map_obj.map_type,
                preprocessing_status=map_obj.preprocessing_status,
                created_at=map_obj.created_at,
                original_image_url=f"/media/maps/{map_obj.id}/original.jpg",
                processed_image_url=f"/media/maps/{map_obj.id}/processed.jpg" if map_obj.processed_image_path else None,
                width=map_obj.width,
                height=map_obj.height,
                scale_meters_per_pixel=map_obj.scale_meters_per_pixel
            )

            user_image_info = UserImageInfo(
                id=user_image.id,
                api_key_id=user_image.api_key_id,
                map_id=user_image.map_id,
                upload_timestamp=user_image.upload_timestamp,
                is_deleted=user_image.is_deleted,
                map=map_info
            )
            images_list.append(user_image_info)

        return images_list

    except Exception as e:
        logger.error(f"이미지 목록 조회 오류: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="이미지 목록 조회 중 오류가 발생했습니다"
        )


@router.get("/usage", response_model=List[DailyUsage])
async def get_usage_by_period(
    period: str = Query("week", regex="^(day|week|month)$"),
    current_api_key: ApiKey = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    기간별 API 사용량 조회

    **Headers:**
    - X-API-Key: API 키 (필수)

    **Query Parameters:**
    - period: day (24시간), week (7일), month (30일)

    **출력:**
    - 기간별 사용량 리스트
    """
    try:
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)
        usage_list = []

        if period == "day":
            # 최근 24시간 (시간별)
            for i in range(24):
                hour_start = today_start - timedelta(hours=23-i)
                hour_end = hour_start + timedelta(hours=1)

                count_result = await db.execute(
                    select(func.count(ApiUsage.id))
                    .where(
                        and_(
                            ApiUsage.api_key_id == current_api_key.id,
                            ApiUsage.timestamp >= hour_start,
                            ApiUsage.timestamp < hour_end
                        )
                    )
                )
                count = count_result.scalar() or 0
                usage_list.append(
                    DailyUsage(
                        date=hour_start.strftime("%Y-%m-%d %H:00"),
                        count=count
                    )
                )

        elif period == "week":
            # 최근 7일 (일별)
            for i in range(7):
                day_start = today_start - timedelta(days=6-i)
                day_end = day_start + timedelta(days=1)

                count_result = await db.execute(
                    select(func.count(ApiUsage.id))
                    .where(
                        and_(
                            ApiUsage.api_key_id == current_api_key.id,
                            ApiUsage.timestamp >= day_start,
                            ApiUsage.timestamp < day_end
                        )
                    )
                )
                count = count_result.scalar() or 0
                usage_list.append(
                    DailyUsage(
                        date=day_start.strftime("%Y-%m-%d"),
                        count=count
                    )
                )

        else:  # month
            # 최근 30일 (일별)
            for i in range(30):
                day_start = today_start - timedelta(days=29-i)
                day_end = day_start + timedelta(days=1)

                count_result = await db.execute(
                    select(func.count(ApiUsage.id))
                    .where(
                        and_(
                            ApiUsage.api_key_id == current_api_key.id,
                            ApiUsage.timestamp >= day_start,
                            ApiUsage.timestamp < day_end
                        )
                    )
                )
                count = count_result.scalar() or 0
                usage_list.append(
                    DailyUsage(
                        date=day_start.strftime("%Y-%m-%d"),
                        count=count
                    )
                )

        return usage_list

    except Exception as e:
        logger.error(f"사용량 조회 오류: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="사용량 조회 중 오류가 발생했습니다"
        )


@router.get("/api-keys", response_model=List[ApiKeyInfo])
async def get_api_keys(
    current_api_key: ApiKey = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    API 키 목록 조회

    현재 사용자의 모든 API 키 목록을 반환합니다.
    (현재는 단일 사용자이므로 모든 키 반환)

    **Headers:**
    - X-API-Key: API 키 (필수)

    **출력:**
    - API 키 목록 (최신순)
    """
    try:
        result = await db.execute(
            select(ApiKey)
            .order_by(desc(ApiKey.created_at))
        )
        api_keys = result.scalars().all()

        return [
            ApiKeyInfo(
                id=key.id,
                key=key.key,
                is_active=key.is_active,
                usage_count=key.usage_count,
                created_at=key.created_at,
                last_used_at=key.last_used_at
            )
            for key in api_keys
        ]

    except Exception as e:
        logger.error(f"API 키 목록 조회 오류: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="API 키 목록 조회 중 오류가 발생했습니다"
        )


@router.post("/api-keys", response_model=ApiKeyCreateResponse, status_code=201)
async def create_api_key(
    request: ApiKeyCreateRequest,
    current_api_key: ApiKey = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    새 API 키 생성

    6자리 랜덤 숫자로 새 API 키를 생성합니다.

    **Headers:**
    - X-API-Key: API 키 (필수)

    **입력:**
    - name: 키 이름 (선택사항)

    **출력:**
    - 생성된 API 키 정보
    """
    try:
        # 6자리 랜덤 키 생성 (중복 체크)
        max_attempts = 10
        new_key_value = None

        for _ in range(max_attempts):
            candidate_key = str(random.randint(100000, 999999))

            # 중복 체크
            result = await db.execute(
                select(ApiKey).where(ApiKey.key == candidate_key)
            )
            existing_key = result.scalar_one_or_none()

            if not existing_key:
                new_key_value = candidate_key
                break

        if not new_key_value:
            raise HTTPException(
                status_code=500,
                detail="API 키 생성 실패: 고유한 키를 생성할 수 없습니다"
            )

        # 새 키 생성
        new_api_key = ApiKey(
            key=new_key_value,
            is_active=True,
            usage_count=0
        )
        db.add(new_api_key)
        await db.commit()
        await db.refresh(new_api_key)

        logger.info(f"새 API 키 생성됨: {new_key_value}")

        return ApiKeyCreateResponse(
            id=new_api_key.id,
            key=new_api_key.key,
            is_active=new_api_key.is_active,
            usage_count=new_api_key.usage_count,
            created_at=new_api_key.created_at,
            last_used_at=new_api_key.last_used_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API 키 생성 오류: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="API 키 생성 중 오류가 발생했습니다"
        )


@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: int,
    current_api_key: ApiKey = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    API 키 삭제

    특정 API 키를 비활성화합니다 (Soft delete).

    **Headers:**
    - X-API-Key: API 키 (필수)

    **Path Parameters:**
    - key_id: 삭제할 API 키 ID

    **출력:**
    - 성공 메시지

    **에러:**
    - 403: 현재 사용 중인 키는 삭제 불가
    - 404: API 키를 찾을 수 없음
    """
    try:
        # 삭제할 키 조회
        result = await db.execute(
            select(ApiKey).where(ApiKey.id == key_id)
        )
        api_key_to_delete = result.scalar_one_or_none()

        if not api_key_to_delete:
            raise HTTPException(
                status_code=404,
                detail="API 키를 찾을 수 없습니다"
            )

        # 현재 사용 중인 키는 삭제 불가
        if api_key_to_delete.id == current_api_key.id:
            raise HTTPException(
                status_code=403,
                detail="현재 사용 중인 API 키는 삭제할 수 없습니다"
            )

        # Soft delete
        api_key_to_delete.is_active = False
        await db.commit()

        logger.info(f"API 키 비활성화됨: {api_key_to_delete.key}")

        return {
            "message": "API key deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API 키 삭제 오류: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="API 키 삭제 중 오류가 발생했습니다"
        )
