"""
기본 API 키 생성 스크립트

서버 초기 설정 시 사용할 기본 API 키 (000000)를 생성합니다.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from app.models.database import Base, ApiKey
from app.config import settings


async def create_default_api_key():
    """기본 API 키 생성"""
    # 엔진 생성
    engine = create_async_engine(settings.database_url, echo=True)

    # 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 세션 생성
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # 기존 000000 키 확인
        result = await session.execute(
            select(ApiKey).where(ApiKey.key == "000000")
        )
        existing_key = result.scalar_one_or_none()

        if existing_key:
            print(f"✅ 기본 API 키가 이미 존재합니다: 000000")
            print(f"   - ID: {existing_key.id}")
            print(f"   - 활성화: {existing_key.is_active}")
            print(f"   - 사용 횟수: {existing_key.usage_count}")
        else:
            # 새 키 생성
            new_key = ApiKey(
                key="000000",
                is_active=True,
                usage_count=0
            )
            session.add(new_key)
            await session.commit()
            await session.refresh(new_key)

            print(f"✅ 기본 API 키 생성 완료!")
            print(f"   - API Key: 000000")
            print(f"   - ID: {new_key.id}")
            print(f"   - 사용법: X-API-Key: 000000")

    await engine.dispose()


if __name__ == "__main__":
    print("=" * 50)
    print("기본 API 키 생성 스크립트")
    print("=" * 50)
    asyncio.run(create_default_api_key())
    print("=" * 50)
