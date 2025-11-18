"""
ML 서비스 레이어
머신러닝 모델과 기존 CV 방식을 통합 관리
"""
import asyncio
import numpy as np
import cv2
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union, List
import logging
import time
import json
from enum import Enum
from datetime import datetime
import hashlib

from app.core.pathfinding.preprocessor import MapPreprocessor
from app.config import settings
from app.services.ml_client import get_ml_client, MLInferenceClient

logger = logging.getLogger(__name__)


class ProcessingMode(str, Enum):
    """처리 모드"""
    CV_ONLY = "cv_only"  # 기존 CV 방식만
    ML_ONLY = "ml_only"  # ML 방식만
    HYBRID = "hybrid"    # ML + CV 혼합
    AB_TEST = "ab_test"  # A/B 테스팅


class MLServiceConfig:
    """ML 서비스 설정"""

    def __init__(self):
        # 모델 경로
        self.model_dir = Path("models")
        self.model_dir.mkdir(parents=True, exist_ok=True)

        # 모델 설정
        self.enable_ml = getattr(settings, 'enable_ml', True)
        self.model_type = getattr(settings, 'ml_model_type', 'unet')
        self.default_mode = ProcessingMode.HYBRID

        # A/B 테스팅 설정
        self.ab_test_ratio = getattr(settings, 'ab_test_ml_ratio', 0.3)
        self.ab_test_enabled = getattr(settings, 'ab_test_enabled', False)

        # 성능 임계값
        self.ml_confidence_threshold = getattr(settings, 'ml_confidence_threshold', 0.85)
        self.fallback_to_cv = getattr(settings, 'enable_ml_fallback', True)

        # 캐싱 설정
        self.enable_cache = True
        self.cache_ttl = 3600  # 1시간


class MLService:
    """ML 서비스 메인 클래스"""

    def __init__(self, config: Optional[MLServiceConfig] = None):
        self.config = config or MLServiceConfig()

        # ML 클라이언트 (HTTP)
        self.ml_client: Optional[MLInferenceClient] = None
        self.cv_preprocessor = MapPreprocessor()

        # A/B 테스팅 메트릭
        self.ab_metrics = {
            'ml': {'count': 0, 'success': 0, 'avg_time': 0, 'total_time': 0},
            'cv': {'count': 0, 'success': 0, 'avg_time': 0, 'total_time': 0}
        }

        # 결과 캐시
        self.result_cache: Dict[str, Dict] = {}

        # ML 클라이언트 초기화
        if self.config.enable_ml:
            self.ml_client = get_ml_client()

        logger.info(f"MLService initialized (ML enabled: {self.config.enable_ml})")

    async def _check_ml_server_health(self) -> bool:
        """ML 서버 헬스 체크"""
        if not self.ml_client:
            return False

        try:
            return await self.ml_client.health_check()
        except Exception as e:
            logger.error(f"ML server health check failed: {e}")
            return False

    async def preprocess_map(
        self,
        image_path: str,
        output_dir: str,
        mode: Optional[ProcessingMode] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        지도 전처리 (ML/CV 통합)

        Args:
            image_path: 입력 이미지 경로
            output_dir: 출력 디렉토리
            mode: 처리 모드 (None이면 자동 선택)
            user_id: 사용자 ID (A/B 테스팅용)
        """
        start_time = time.time()

        # 처리 모드 결정
        if mode is None:
            mode = self._determine_processing_mode(user_id)

        logger.info(f"Processing map with mode: {mode}")

        # 캐시 확인
        cache_key = self._generate_cache_key(image_path, mode)
        if self.config.enable_cache and cache_key in self.result_cache:
            cached_result = self.result_cache[cache_key]
            if time.time() - cached_result['cached_at'] < self.config.cache_ttl:
                logger.info("Returning cached result")
                cached_result['from_cache'] = True
                return cached_result

        # 이미지 로드
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")

        # 처리 모드별 실행
        if mode == ProcessingMode.ML_ONLY:
            result = await self._process_with_ml(image, image_path, output_dir)
        elif mode == ProcessingMode.CV_ONLY:
            result = await self._process_with_cv(image, image_path, output_dir)
        elif mode == ProcessingMode.HYBRID:
            result = await self._process_hybrid(image, image_path, output_dir)
        elif mode == ProcessingMode.AB_TEST:
            result = await self._process_ab_test(image, image_path, output_dir, user_id)
        else:
            raise ValueError(f"Unknown processing mode: {mode}")

        # 처리 시간 추가
        result['processing_time'] = time.time() - start_time
        result['processing_mode'] = mode
        result['from_cache'] = False

        # 캐싱
        if self.config.enable_cache:
            result['cached_at'] = time.time()
            self.result_cache[cache_key] = result

        return result

    async def _process_with_ml(
        self,
        image: np.ndarray,
        image_path: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """ML 모델로 처리 (HTTP 클라이언트 사용)"""
        if not self.ml_client:
            logger.warning("ML client not available, falling back to CV")
            return await self._process_with_cv(image, image_path, output_dir)

        start_time = time.time()

        try:
            # ML 서버로 세그멘테이션 요청
            ml_result = await self.ml_client.segment_map(
                image,
                return_visualization=True,
                return_navigation_grid=True
            )

            # 출력 저장
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # 세그멘테이션 마스크 저장
            if 'segmentation_mask' in ml_result:
                segmentation_path = output_path / "ml_segmentation.png"
                cv2.imwrite(str(segmentation_path), ml_result['segmentation_mask'])
            else:
                segmentation_path = None

            # 보행 가능 영역 저장
            if 'walkable_mask' in ml_result:
                walkable_path = output_path / "ml_walkable.png"
                cv2.imwrite(str(walkable_path), ml_result['walkable_mask'] * 255)
            else:
                walkable_path = None

            # 시각화 저장
            if 'visualization' in ml_result:
                vis_path = output_path / "ml_visualization.png"
                cv2.imwrite(str(vis_path), ml_result['visualization'])
            else:
                vis_path = None

            # 네비게이션 그리드 저장
            if 'navigation_grid' in ml_result:
                grid_path = output_path / "ml_grid.json"
                with open(grid_path, 'w') as f:
                    json.dump(ml_result['navigation_grid'], f)
            else:
                grid_path = None

            # 결과 구성
            result = {
                'success': True,
                'method': 'ml',
                'model_type': self.config.model_type,
                'segmentation_path': str(segmentation_path) if segmentation_path else None,
                'walkable_mask_path': str(walkable_path) if walkable_path else None,
                'visualization_path': str(vis_path) if vis_path else None,
                'navigation_grid_path': str(grid_path) if grid_path else None,
                'statistics': ml_result.get('statistics', {}),
                'walkable_percentage': ml_result.get('statistics', {}).get('walkable_percentage', 0),
                'ml_inference_time': ml_result.get('inference_time', 0),
                'http_time': ml_result.get('http_time', 0),
                'total_time': ml_result.get('total_time', time.time() - start_time)
            }

            # A/B 메트릭 업데이트
            self._update_ab_metrics('ml', time.time() - start_time, True)

            return result

        except Exception as e:
            logger.error(f"ML processing failed: {e}")
            self._update_ab_metrics('ml', time.time() - start_time, False)

            if self.config.fallback_to_cv:
                logger.info("Falling back to CV processing")
                return await self._process_with_cv(image, image_path, output_dir)
            raise

    async def _process_with_cv(
        self,
        image: np.ndarray,
        image_path: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """기존 CV 방식으로 처리"""
        start_time = time.time()

        try:
            # CV 전처리 (동기 함수를 비동기로 실행)
            loop = asyncio.get_event_loop()
            cv_result = await loop.run_in_executor(
                None,
                self.cv_preprocessor.preprocess_map,
                image_path,
                output_dir
            )

            cv_result['success'] = True
            cv_result['method'] = 'cv'
            cv_result['cv_processing_time'] = time.time() - start_time

            # A/B 메트릭 업데이트
            self._update_ab_metrics('cv', time.time() - start_time, True)

            return cv_result

        except Exception as e:
            logger.error(f"CV processing failed: {e}")
            self._update_ab_metrics('cv', time.time() - start_time, False)
            raise

    async def _process_hybrid(
        self,
        image: np.ndarray,
        image_path: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """ML + CV 하이브리드 처리"""
        # ML과 CV를 병렬로 실행
        ml_task = asyncio.create_task(self._process_with_ml(image, image_path, output_dir + "/ml"))
        cv_task = asyncio.create_task(self._process_with_cv(image, image_path, output_dir + "/cv"))

        ml_result, cv_result = await asyncio.gather(ml_task, cv_task, return_exceptions=True)

        # 에러 처리
        if isinstance(ml_result, Exception):
            logger.error(f"ML failed in hybrid mode: {ml_result}")
            return cv_result if not isinstance(cv_result, Exception) else {'success': False, 'error': str(ml_result)}

        if isinstance(cv_result, Exception):
            logger.error(f"CV failed in hybrid mode: {cv_result}")
            return ml_result

        # ML 신뢰도 확인
        ml_confidence = self._calculate_ml_confidence(ml_result)

        # 신뢰도 기반 선택
        if ml_confidence >= self.config.ml_confidence_threshold:
            selected_method = 'ml'
            primary_result = ml_result
            logger.info(f"Selected ML (confidence: {ml_confidence:.2f})")
        else:
            selected_method = 'cv'
            primary_result = cv_result
            logger.info(f"Selected CV (ML confidence too low: {ml_confidence:.2f})")

        # 통합 결과
        hybrid_result = {
            'success': True,
            'method': 'hybrid',
            'selected_method': selected_method,
            'ml_confidence': ml_confidence,
            'ml_result': ml_result,
            'cv_result': cv_result,
            'primary_result': primary_result,
            'comparison': self._compare_results(ml_result, cv_result)
        }

        return hybrid_result

    async def _process_ab_test(
        self,
        image: np.ndarray,
        image_path: str,
        output_dir: str,
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """A/B 테스팅"""
        # 사용자 그룹 결정 (해시 기반)
        use_ml = self._should_use_ml_for_user(user_id)

        if use_ml:
            result = await self._process_with_ml(image, image_path, output_dir)
            result['ab_group'] = 'ml'
        else:
            result = await self._process_with_cv(image, image_path, output_dir)
            result['ab_group'] = 'cv'

        result['ab_test'] = True
        result['user_id'] = user_id

        return result

    def _determine_processing_mode(self, user_id: Optional[str]) -> ProcessingMode:
        """처리 모드 자동 결정"""
        if not self.config.enable_ml or not self.ml_client:
            return ProcessingMode.CV_ONLY

        if self.config.ab_test_enabled and user_id:
            return ProcessingMode.AB_TEST

        return self.config.default_mode

    def _should_use_ml_for_user(self, user_id: Optional[str]) -> bool:
        """A/B 테스트에서 사용자에게 ML 적용 여부"""
        if not user_id:
            return np.random.random() < self.ab_test_ratio

        # 사용자 ID 해시로 일관된 그룹 할당
        hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        return (hash_value % 100) < (self.ab_test_ratio * 100)

    def _calculate_ml_confidence(self, ml_result: Dict) -> float:
        """ML 결과의 신뢰도 계산"""
        if not ml_result.get('success'):
            return 0.0

        # 통계 기반 신뢰도 (간단한 휴리스틱)
        stats = ml_result.get('statistics', {})
        walkable_pct = stats.get('walkable_percentage', 0)

        # 보행 가능 영역이 너무 많거나 적으면 신뢰도 낮음
        if walkable_pct < 10 or walkable_pct > 90:
            return 0.5

        # 기본 신뢰도
        return 0.9

    def _compare_results(self, ml_result: Dict, cv_result: Dict) -> Dict[str, Any]:
        """ML과 CV 결과 비교"""
        comparison = {
            'processing_time': {
                'ml': ml_result.get('ml_inference_time', 0),
                'cv': cv_result.get('cv_processing_time', 0)
            },
            'walkable_percentage': {
                'ml': ml_result.get('walkable_percentage', 0),
                'cv': cv_result.get('walkable_percentage', 0)
            }
        }

        # 차이 계산
        comparison['time_difference'] = comparison['processing_time']['ml'] - comparison['processing_time']['cv']
        comparison['walkable_diff'] = abs(
            comparison['walkable_percentage']['ml'] - comparison['walkable_percentage']['cv']
        )

        return comparison

    def _update_ab_metrics(self, method: str, processing_time: float, success: bool):
        """A/B 테스팅 메트릭 업데이트"""
        metrics = self.ab_metrics[method]
        metrics['count'] += 1

        if success:
            metrics['success'] += 1
            metrics['total_time'] += processing_time
            metrics['avg_time'] = metrics['total_time'] / metrics['success']

    def _generate_cache_key(self, image_path: str, mode: ProcessingMode) -> str:
        """캐시 키 생성"""
        # 파일 경로 + 모드 + 수정 시간 해시
        file_stat = Path(image_path).stat()
        key_string = f"{image_path}:{mode}:{file_stat.st_mtime}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def get_ab_test_metrics(self) -> Dict[str, Any]:
        """A/B 테스팅 메트릭 조회"""
        metrics = self.ab_metrics.copy()

        # 성공률 계산
        for method in ['ml', 'cv']:
            count = metrics[method]['count']
            if count > 0:
                metrics[method]['success_rate'] = metrics[method]['success'] / count
            else:
                metrics[method]['success_rate'] = 0

        # 비교
        if metrics['ml']['count'] > 0 and metrics['cv']['count'] > 0:
            metrics['comparison'] = {
                'ml_faster': metrics['ml']['avg_time'] < metrics['cv']['avg_time'],
                'time_difference': abs(metrics['ml']['avg_time'] - metrics['cv']['avg_time']),
                'ml_more_reliable': metrics['ml']['success_rate'] > metrics['cv']['success_rate']
            }

        return metrics

    def enable_ab_testing(self, enabled: bool = True, ratio: float = 0.3):
        """A/B 테스팅 활성화/비활성화"""
        self.config.ab_test_enabled = enabled
        self.config.ab_test_ratio = ratio
        logger.info(f"A/B testing {'enabled' if enabled else 'disabled'} (ML ratio: {ratio})")

    def clear_cache(self):
        """캐시 초기화"""
        self.result_cache.clear()
        logger.info("Result cache cleared")


# 싱글톤 인스턴스
_ml_service_instance: Optional[MLService] = None


def get_ml_service() -> MLService:
    """ML 서비스 싱글톤 인스턴스 가져오기"""
    global _ml_service_instance

    if _ml_service_instance is None:
        _ml_service_instance = MLService()

    return _ml_service_instance


async def cleanup_ml_service():
    """ML 서비스 정리 (앱 종료 시)"""
    global _ml_service_instance

    if _ml_service_instance:
        _ml_service_instance.clear_cache()
        _ml_service_instance = None
        logger.info("ML service cleaned up")