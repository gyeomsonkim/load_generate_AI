"""
인증 관련 의존성
"""
from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime

from app.models.database import ApiKey
from app.api.dependencies import get_db


async def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db)
) -> ApiKey:
    """
    API 키 검증 의존성

    Args:
        x_api_key: HTTP 헤더의 X-API-Key 값
        db: 데이터베이스 세션

    Returns:
        ApiKey: 검증된 API 키 객체

    Raises:
        HTTPException: API 키가 유효하지 않을 경우
    """
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key is required. Please provide X-API-Key header."
        )

    # API 키 조회
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.key == x_api_key,
            ApiKey.is_active == True
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or inactive API key"
        )

    # 마지막 사용 시간 업데이트
    api_key.last_used_at = datetime.utcnow()
    await db.commit()

    return api_key


async def optional_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db)
) -> Optional[ApiKey]:
    """
    선택적 API 키 검증 (키가 없어도 통과)

    Args:
        x_api_key: HTTP 헤더의 X-API-Key 값
        db: 데이터베이스 세션

    Returns:
        Optional[ApiKey]: 검증된 API 키 객체 또는 None
    """
    if not x_api_key:
        return None

    result = await db.execute(
        select(ApiKey).where(
            ApiKey.key == x_api_key,
            ApiKey.is_active == True
        )
    )
    api_key = result.scalar_one_or_none()

    if api_key:
        api_key.last_used_at = datetime.utcnow()
        await db.commit()

    return api_key
