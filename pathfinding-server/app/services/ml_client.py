"""
ML Inference Server HTTP 클라이언트
"""
import httpx
import asyncio
import numpy as np
import cv2
import base64
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import time

from app.config import settings

logger = logging.getLogger(__name__)


class MLInferenceClient:
    """ML Inference Server HTTP 클라이언트"""

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        self.base_url = base_url or getattr(settings, 'ml_inference_url', 'http://localhost:8001')
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout
        )

        logger.info(f"ML Inference Client initialized: {self.base_url}")

    async def health_check(self) -> bool:
        """
        ML 서버 헬스 체크

        Returns:
            서버가 정상이면 True
        """
        try:
            response = await self.client.get("/health")
            response.raise_for_status()

            data = response.json()
            is_healthy = data.get('status') == 'healthy' and data.get('model_loaded', False)

            if is_healthy:
                logger.info("✅ ML server is healthy")
            else:
                logger.warning(f"⚠️  ML server is degraded: {data}")

            return is_healthy

        except Exception as e:
            logger.error(f"❌ ML server health check failed: {e}")
            return False

    async def segment_map(
        self,
        image: np.ndarray,
        return_visualization: bool = False,
        return_navigation_grid: bool = False
    ) -> Dict[str, Any]:
        """
        맵 세그멘테이션

        Args:
            image: 입력 이미지 (numpy array, BGR)
            return_visualization: 시각화 결과 포함 여부
            return_navigation_grid: 네비게이션 그리드 포함 여부

        Returns:
            세그멘테이션 결과
        """
        start_time = time.time()

        for attempt in range(self.max_retries):
            try:
                # 이미지를 바이트로 인코딩
                _, image_encoded = cv2.imencode('.png', image)
                image_bytes = image_encoded.tobytes()

                # multipart/form-data로 전송
                files = {'image': ('map.png', image_bytes, 'image/png')}
                params = {
                    'return_visualization': return_visualization,
                    'return_navigation_grid': return_navigation_grid
                }

                logger.info(f"Sending segmentation request (attempt {attempt + 1}/{self.max_retries})")

                response = await self.client.post(
                    "/api/v1/segment",
                    files=files,
                    params=params
                )

                response.raise_for_status()
                result = response.json()

                # Base64 디코딩
                processed_result = self._decode_base64_results(result)

                # 처리 시간 추가
                processed_result['http_time'] = time.time() - start_time
                processed_result['total_time'] = processed_result['http_time'] + result.get('inference_time', 0)

                logger.info(f"✅ Segmentation completed in {processed_result['total_time']:.3f}s")

                return processed_result

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error (attempt {attempt + 1}): {e.response.status_code} - {e.response.text}")
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f"ML server request failed: {e.response.text}")

            except httpx.TimeoutException as e:
                logger.error(f"Timeout (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    raise RuntimeError("ML server timeout")

            except Exception as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f"ML server request failed: {str(e)}")

            # 재시도 전 대기
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt  # 지수 백오프
                logger.info(f"Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

        raise RuntimeError("ML server request failed after all retries")

    def _decode_base64_results(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Base64 인코딩된 결과를 numpy array로 디코딩"""
        decoded = result.copy()

        # 세그멘테이션 마스크
        if 'segmentation_mask_base64' in result and result['segmentation_mask_base64']:
            mask_bytes = base64.b64decode(result['segmentation_mask_base64'])
            mask_np = cv2.imdecode(
                np.frombuffer(mask_bytes, np.uint8),
                cv2.IMREAD_UNCHANGED
            )
            decoded['segmentation_mask'] = mask_np

        # 보행 가능 마스크
        if 'walkable_mask_base64' in result and result['walkable_mask_base64']:
            walkable_bytes = base64.b64decode(result['walkable_mask_base64'])
            walkable_np = cv2.imdecode(
                np.frombuffer(walkable_bytes, np.uint8),
                cv2.IMREAD_UNCHANGED
            )
            decoded['walkable_mask'] = (walkable_np > 0).astype(np.uint8)

        # 시각화
        if 'visualization_base64' in result and result['visualization_base64']:
            vis_bytes = base64.b64decode(result['visualization_base64'])
            vis_np = cv2.imdecode(
                np.frombuffer(vis_bytes, np.uint8),
                cv2.IMREAD_COLOR
            )
            decoded['visualization'] = vis_np

        return decoded

    async def get_model_info(self) -> Dict[str, Any]:
        """모델 정보 조회"""
        try:
            response = await self.client.get("/api/v1/model/info")
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {"loaded": False, "error": str(e)}

    async def close(self):
        """클라이언트 종료"""
        await self.client.aclose()
        logger.info("ML Inference Client closed")


# 싱글톤 인스턴스
_ml_client: Optional[MLInferenceClient] = None


def get_ml_client() -> MLInferenceClient:
    """ML 클라이언트 싱글톤 가져오기"""
    global _ml_client

    if _ml_client is None:
        _ml_client = MLInferenceClient()

    return _ml_client


async def cleanup_ml_client():
    """ML 클라이언트 정리"""
    global _ml_client

    if _ml_client:
        await _ml_client.close()
        _ml_client = None
