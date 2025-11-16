"""
FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from app.config import settings
from app.api.routes import maps
from app.models.database import Base
from app.api.dependencies import engine

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시
    logger.info(f"서버 시작: {settings.app_name} v{settings.app_version}")

    # 데이터베이스 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("데이터베이스 테이블 생성 완료")

    # 스토리지 디렉토리 생성
    storage_path = Path(settings.storage_path)
    storage_path.mkdir(parents=True, exist_ok=True)
    (storage_path / "uploads").mkdir(exist_ok=True)
    (storage_path / "processed").mkdir(exist_ok=True)
    logger.info(f"스토리지 디렉토리 준비 완료: {storage_path}")

    yield

    # 종료 시
    logger.info("서버 종료 중...")
    await engine.dispose()


# FastAPI 앱 생성
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 정적 파일 서빙 (로컬 스토리지 사용 시)
if settings.storage_type == "local":
    app.mount("/files", StaticFiles(directory=settings.storage_path), name="files")


# API 라우터 등록
app.include_router(maps.router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """루트 경로"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "AI 기반 길찾기 서버",
        "docs": "/docs",
        "api": settings.api_prefix
    }


@app.get(f"{settings.api_prefix}/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    from app.models.schemas import HealthResponse

    # 데이터베이스 연결 확인
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
            db_status = "connected"
    except Exception as e:
        logger.error(f"DB 연결 실패: {e}")
        db_status = "disconnected"

    # Redis 연결 확인 (Phase 2에서 구현)
    redis_status = "not_implemented"

    # 스토리지 확인
    storage_status = "ok" if Path(settings.storage_path).exists() else "error"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "unhealthy",
        version=settings.app_version,
        database=db_status,
        redis=redis_status,
        storage=storage_status,
        ml_models_loaded=False  # Phase 2에서 구현
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """404 에러 핸들러"""
    return JSONResponse(
        status_code=404,
        content={"detail": "요청한 리소스를 찾을 수 없습니다"}
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """500 에러 핸들러"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "서버 내부 오류가 발생했습니다"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )