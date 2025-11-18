"""
ML 관련 API 엔드포인트
머신러닝 모델 관리 및 A/B 테스팅
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import logging

from app.services.ml_service import get_ml_service, ProcessingMode

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ml", tags=["ml"])


# Request/Response 모델
class ProcessingModeRequest(BaseModel):
    """처리 모드 요청"""
    mode: ProcessingMode = Field(..., description="처리 모드")
    description: Optional[str] = Field(None, description="설명")


class ABTestConfigRequest(BaseModel):
    """A/B 테스팅 설정 요청"""
    enabled: bool = Field(..., description="A/B 테스팅 활성화")
    ml_ratio: float = Field(0.3, description="ML 사용 비율 (0.0-1.0)", ge=0.0, le=1.0)


class MLModelInfo(BaseModel):
    """ML 모델 정보"""
    model_loaded: bool
    model_type: str
    enabled: bool
    default_mode: str


class ABTestMetrics(BaseModel):
    """A/B 테스팅 메트릭"""
    ml: Dict[str, Any]
    cv: Dict[str, Any]
    comparison: Optional[Dict[str, Any]] = None


class MLServiceStatus(BaseModel):
    """ML 서비스 상태"""
    ml_enabled: bool
    model_info: MLModelInfo
    ab_test_enabled: bool
    ab_test_ratio: float
    cache_enabled: bool


@router.get("/status", response_model=MLServiceStatus)
async def get_ml_status():
    """
    ML 서비스 상태 조회

    Returns:
        ML 서비스 현재 상태
    """
    try:
        ml_service = get_ml_service()

        return MLServiceStatus(
            ml_enabled=ml_service.config.enable_ml,
            model_info=MLModelInfo(
                model_loaded=ml_service.ml_model is not None,
                model_type=ml_service.config.model_type,
                enabled=ml_service.config.enable_ml,
                default_mode=ml_service.config.default_mode
            ),
            ab_test_enabled=ml_service.config.ab_test_enabled,
            ab_test_ratio=ml_service.config.ab_test_ratio,
            cache_enabled=ml_service.config.enable_cache
        )

    except Exception as e:
        logger.error(f"Failed to get ML status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mode")
async def set_processing_mode(request: ProcessingModeRequest):
    """
    기본 처리 모드 설정

    Args:
        request: 처리 모드 요청

    Returns:
        설정 결과
    """
    try:
        ml_service = get_ml_service()
        ml_service.config.default_mode = request.mode

        logger.info(f"Processing mode changed to: {request.mode}")

        return {
            "success": True,
            "mode": request.mode,
            "message": f"Processing mode set to {request.mode}"
        }

    except Exception as e:
        logger.error(f"Failed to set processing mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ab-test/config")
async def configure_ab_test(request: ABTestConfigRequest):
    """
    A/B 테스팅 설정

    Args:
        request: A/B 테스팅 설정 요청

    Returns:
        설정 결과
    """
    try:
        ml_service = get_ml_service()
        ml_service.enable_ab_testing(request.enabled, request.ml_ratio)

        return {
            "success": True,
            "ab_test_enabled": request.enabled,
            "ml_ratio": request.ml_ratio,
            "message": f"A/B testing {'enabled' if request.enabled else 'disabled'}"
        }

    except Exception as e:
        logger.error(f"Failed to configure A/B test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ab-test/metrics", response_model=ABTestMetrics)
async def get_ab_test_metrics():
    """
    A/B 테스팅 메트릭 조회

    Returns:
        A/B 테스팅 메트릭 데이터
    """
    try:
        ml_service = get_ml_service()
        metrics = ml_service.get_ab_test_metrics()

        return ABTestMetrics(**metrics)

    except Exception as e:
        logger.error(f"Failed to get A/B test metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ab-test/reset")
async def reset_ab_test_metrics():
    """
    A/B 테스팅 메트릭 초기화

    Returns:
        초기화 결과
    """
    try:
        ml_service = get_ml_service()
        ml_service.ab_metrics = {
            'ml': {'count': 0, 'success': 0, 'avg_time': 0, 'total_time': 0},
            'cv': {'count': 0, 'success': 0, 'avg_time': 0, 'total_time': 0}
        }

        logger.info("A/B test metrics reset")

        return {
            "success": True,
            "message": "A/B test metrics reset successfully"
        }

    except Exception as e:
        logger.error(f"Failed to reset A/B test metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model/info")
async def get_model_info():
    """
    ML 모델 상세 정보 조회

    Returns:
        모델 상세 정보
    """
    try:
        ml_service = get_ml_service()

        if not ml_service.ml_model:
            return {
                "success": False,
                "message": "ML model not loaded"
            }

        model_info = ml_service.ml_model.get_model_info()

        return {
            "success": True,
            "model_info": model_info
        }

    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/model/benchmark")
async def benchmark_model(
    input_shape: str = Query("1,3,512,512", description="Input shape (B,C,H,W)"),
    iterations: int = Query(100, description="Number of iterations", ge=10, le=1000)
):
    """
    ML 모델 벤치마크 실행

    Args:
        input_shape: 입력 텐서 shape
        iterations: 반복 횟수

    Returns:
        벤치마크 결과
    """
    try:
        ml_service = get_ml_service()

        if not ml_service.ml_model:
            raise HTTPException(status_code=400, detail="ML model not loaded")

        # 입력 shape 파싱
        shape = tuple(map(int, input_shape.split(',')))

        # 벤치마크 실행
        results = ml_service.ml_model.benchmark(input_shape=shape, iterations=iterations)

        return {
            "success": True,
            "benchmark_results": results,
            "input_shape": shape,
            "iterations": iterations
        }

    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear")
async def clear_cache():
    """
    결과 캐시 초기화

    Returns:
        초기화 결과
    """
    try:
        ml_service = get_ml_service()
        ml_service.clear_cache()

        return {
            "success": True,
            "message": "Cache cleared successfully"
        }

    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    ML 서비스 헬스 체크

    Returns:
        서비스 상태
    """
    try:
        ml_service = get_ml_service()

        health_status = {
            "status": "healthy",
            "ml_service": "running",
            "ml_model_loaded": ml_service.ml_model is not None,
            "cv_preprocessor": "available",
            "cache_size": len(ml_service.result_cache)
        }

        # 모델이 없으면 경고
        if not ml_service.ml_model:
            health_status["status"] = "degraded"
            health_status["warning"] = "ML model not loaded, using CV only"

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }