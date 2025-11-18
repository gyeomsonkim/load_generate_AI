"""
인증 관련 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import logging

from app.models.schemas import (
    ApiKeyVerifyRequest,
    ApiKeyVerifyResponse,
    ApiKeyInfo
)
from app.models.database import ApiKey
from app.api.dependencies import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/verify", response_model=ApiKeyVerifyResponse)
async def verify_api_key(
    request: ApiKeyVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    API 키 검증

    6자리 API 키를 검증하고 키 정보를 반환합니다.

    **입력:**
    - api_key: 6자리 API 키

    **출력:**
    - valid: 키 유효 여부
    - key_info: 키 정보 (유효한 경우)

    **에러:**
    - 401: 유효하지 않은 API 키
    """
    try:
        # API 키 조회
        result = await db.execute(
            select(ApiKey).where(
                ApiKey.key == request.api_key,
                ApiKey.is_active == True
            )
        )
        api_key = result.scalar_one_or_none()

        if not api_key:
            return ApiKeyVerifyResponse(
                valid=False,
                key_info=None
            )

        # 마지막 사용 시간 업데이트
        api_key.last_used_at = datetime.utcnow()
        api_key.usage_count += 1
        await db.commit()
        await db.refresh(api_key)

        # API 키 정보 반환
        key_info = ApiKeyInfo(
            id=api_key.id,
            key=api_key.key,
            is_active=api_key.is_active,
            usage_count=api_key.usage_count,
            created_at=api_key.created_at,
            last_used_at=api_key.last_used_at
        )

        logger.info(f"API key verified successfully: {request.api_key}")
        return ApiKeyVerifyResponse(
            valid=True,
            key_info=key_info
        )

    except Exception as e:
        logger.error(f"API 키 검증 오류: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="API 키 검증 중 오류가 발생했습니다"
        )
