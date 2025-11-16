"""
API 의존성 주입
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config import settings
from app.services.storage_service import StorageService

# 데이터베이스 엔진 생성
engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    future=True
)

# 세션 팩토리
async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """데이터베이스 세션 의존성"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


def get_storage_service() -> StorageService:
    """스토리지 서비스 의존성"""
    return StorageService(
        storage_type=settings.storage_type,
        config={
            "storage_path": settings.storage_path,
            "minio_endpoint": settings.minio_endpoint,
            "minio_access_key": settings.minio_access_key,
            "minio_secret_key": settings.minio_secret_key,
            "minio_bucket": settings.minio_bucket,
            "minio_secure": settings.minio_secure
        }
    )