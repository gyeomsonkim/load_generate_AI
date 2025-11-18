"""
ML 모델 베이스 클래스 및 인터페이스
모든 ML 모델이 상속받을 기본 클래스
"""
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any, Optional, Tuple, Union, List
from pathlib import Path
import json
import logging
from abc import ABC, abstractmethod
import onnx
import onnxruntime as ort
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class BaseMLModel(ABC):
    """ML 모델 베이스 클래스"""

    def __init__(
        self,
        model_name: str,
        model_version: str = "1.0.0",
        device: Optional[str] = None
    ):
        self.model_name = model_name
        self.model_version = model_version
        self.device = device or self._get_device()
        self.model = None
        self.metadata = {
            'name': model_name,
            'version': model_version,
            'created_at': datetime.now().isoformat(),
            'device': self.device,
            'framework': 'pytorch'
        }

        # 모델 경로 설정
        self.model_dir = Path("models") / model_name
        self.model_dir.mkdir(parents=True, exist_ok=True)

        # 성능 메트릭
        self.metrics = {
            'inference_count': 0,
            'total_inference_time': 0,
            'error_count': 0,
            'last_inference': None
        }

        logger.info(f"Initialized {model_name} v{model_version} on {self.device}")

    def _get_device(self) -> str:
        """사용 가능한 디바이스 자동 감지"""
        if torch.cuda.is_available():
            return 'cuda'
        elif torch.backends.mps.is_available():
            return 'mps'
        return 'cpu'

    @abstractmethod
    def build_model(self) -> nn.Module:
        """모델 아키텍처 구축"""
        pass

    @abstractmethod
    def preprocess(self, input_data: Any) -> torch.Tensor:
        """입력 데이터 전처리"""
        pass

    @abstractmethod
    def postprocess(self, output: torch.Tensor) -> Any:
        """모델 출력 후처리"""
        pass

    def load_model(self, checkpoint_path: Optional[str] = None) -> bool:
        """모델 가중치 로드"""
        try:
            if checkpoint_path is None:
                checkpoint_path = self.model_dir / f"{self.model_name}_v{self.model_version}.pth"

            if not Path(checkpoint_path).exists():
                logger.warning(f"Checkpoint not found: {checkpoint_path}")
                return False

            # 모델 구축
            if self.model is None:
                self.model = self.build_model()

            # 가중치 로드
            checkpoint = torch.load(checkpoint_path, map_location=self.device)

            if isinstance(checkpoint, dict):
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.metadata.update(checkpoint.get('metadata', {}))
                self.metrics.update(checkpoint.get('metrics', {}))
                logger.info(f"Loaded model from checkpoint: {checkpoint_path}")
            else:
                self.model.load_state_dict(checkpoint)
                logger.info(f"Loaded model weights: {checkpoint_path}")

            self.model.to(self.device)
            self.model.eval()
            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    def save_model(self, checkpoint_path: Optional[str] = None) -> bool:
        """모델 저장"""
        try:
            if checkpoint_path is None:
                checkpoint_path = self.model_dir / f"{self.model_name}_v{self.model_version}.pth"

            checkpoint = {
                'model_state_dict': self.model.state_dict(),
                'metadata': self.metadata,
                'metrics': self.metrics,
                'timestamp': datetime.now().isoformat()
            }

            torch.save(checkpoint, checkpoint_path)
            logger.info(f"Saved model to: {checkpoint_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False

    def predict(self, input_data: Any, batch_size: int = 1) -> Any:
        """추론 실행"""
        try:
            start_time = datetime.now()

            # 전처리
            processed_input = self.preprocess(input_data)

            # 배치 처리
            if batch_size > 1 and len(processed_input.shape) > 0:
                processed_input = self._create_batch(processed_input, batch_size)

            # 추론
            with torch.no_grad():
                if self.model is None:
                    raise ValueError("Model not loaded. Call load_model() first.")

                self.model.eval()
                output = self.model(processed_input.to(self.device))

            # 후처리
            result = self.postprocess(output.cpu())

            # 메트릭 업데이트
            inference_time = (datetime.now() - start_time).total_seconds()
            self.metrics['inference_count'] += 1
            self.metrics['total_inference_time'] += inference_time
            self.metrics['last_inference'] = datetime.now().isoformat()

            return result

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            self.metrics['error_count'] += 1
            raise

    def _create_batch(self, tensor: torch.Tensor, batch_size: int) -> torch.Tensor:
        """배치 생성"""
        if len(tensor.shape) == 3:  # 단일 이미지
            return tensor.unsqueeze(0).repeat(batch_size, 1, 1, 1)
        return tensor

    def export_onnx(self, output_path: Optional[str] = None, input_shape: Tuple = (1, 3, 512, 512)) -> bool:
        """ONNX 형식으로 모델 내보내기"""
        try:
            if output_path is None:
                output_path = self.model_dir / f"{self.model_name}_v{self.model_version}.onnx"

            if self.model is None:
                raise ValueError("Model not loaded")

            # 더미 입력 생성
            dummy_input = torch.randn(input_shape).to(self.device)

            # ONNX 내보내기
            torch.onnx.export(
                self.model,
                dummy_input,
                output_path,
                export_params=True,
                opset_version=11,
                do_constant_folding=True,
                input_names=['input'],
                output_names=['output'],
                dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
            )

            # 검증
            onnx_model = onnx.load(output_path)
            onnx.checker.check_model(onnx_model)

            logger.info(f"Exported model to ONNX: {output_path}")
            return True

        except Exception as e:
            logger.error(f"ONNX export failed: {e}")
            return False

    def benchmark(self, input_shape: Tuple = (1, 3, 512, 512), iterations: int = 100) -> Dict[str, float]:
        """모델 성능 벤치마크"""
        import time

        results = {
            'avg_inference_time': 0,
            'min_inference_time': float('inf'),
            'max_inference_time': 0,
            'throughput': 0,
            'model_size_mb': 0
        }

        try:
            # 모델 크기 계산
            param_size = sum(p.numel() * p.element_size() for p in self.model.parameters())
            buffer_size = sum(b.numel() * b.element_size() for b in self.model.buffers())
            results['model_size_mb'] = (param_size + buffer_size) / 1024 / 1024

            # 워밍업
            dummy_input = torch.randn(input_shape).to(self.device)
            for _ in range(10):
                _ = self.model(dummy_input)

            # 벤치마크
            times = []
            for _ in range(iterations):
                start = time.perf_counter()
                with torch.no_grad():
                    _ = self.model(dummy_input)
                end = time.perf_counter()
                times.append(end - start)

            results['avg_inference_time'] = np.mean(times) * 1000  # ms
            results['min_inference_time'] = np.min(times) * 1000
            results['max_inference_time'] = np.max(times) * 1000
            results['throughput'] = 1.0 / np.mean(times)  # fps

            logger.info(f"Benchmark results: {results}")
            return results

        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            return results

    def get_model_info(self) -> Dict[str, Any]:
        """모델 정보 반환"""
        info = {
            'metadata': self.metadata,
            'metrics': self.metrics,
            'device': self.device,
            'is_loaded': self.model is not None
        }

        if self.model is not None:
            info['parameters'] = sum(p.numel() for p in self.model.parameters())
            info['trainable_parameters'] = sum(p.numel() for p in self.model.parameters() if p.requires_grad)

        return info


class ONNXInferenceEngine:
    """ONNX Runtime 추론 엔진"""

    def __init__(self, model_path: str, providers: Optional[List[str]] = None):
        self.model_path = model_path

        # Provider 설정 (GPU/CPU)
        if providers is None:
            providers = self._get_providers()

        # ONNX Runtime 세션 생성
        self.session = ort.InferenceSession(model_path, providers=providers)
        self.input_names = [inp.name for inp in self.session.get_inputs()]
        self.output_names = [out.name for out in self.session.get_outputs()]

        logger.info(f"Loaded ONNX model: {model_path}")
        logger.info(f"Providers: {providers}")

    def _get_providers(self) -> List[str]:
        """사용 가능한 Provider 감지"""
        providers = []

        if 'CUDAExecutionProvider' in ort.get_available_providers():
            providers.append('CUDAExecutionProvider')

        providers.append('CPUExecutionProvider')
        return providers

    def predict(self, input_data: np.ndarray) -> np.ndarray:
        """ONNX 모델 추론"""
        input_dict = {self.input_names[0]: input_data}
        outputs = self.session.run(self.output_names, input_dict)
        return outputs[0]

    def benchmark(self, input_shape: Tuple, iterations: int = 100) -> Dict[str, float]:
        """ONNX 모델 벤치마크"""
        import time

        dummy_input = np.random.randn(*input_shape).astype(np.float32)

        # 워밍업
        for _ in range(10):
            _ = self.predict(dummy_input)

        # 벤치마크
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            _ = self.predict(dummy_input)
            end = time.perf_counter()
            times.append(end - start)

        return {
            'avg_inference_time_ms': np.mean(times) * 1000,
            'throughput_fps': 1.0 / np.mean(times)
        }


class ModelRegistry:
    """모델 레지스트리 (버전 관리)"""

    def __init__(self, registry_path: str = "models/registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.models = self._load_registry()

    def _load_registry(self) -> Dict:
        """레지스트리 로드"""
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        return {}

    def _save_registry(self):
        """레지스트리 저장"""
        with open(self.registry_path, 'w') as f:
            json.dump(self.models, f, indent=2)

    def register_model(
        self,
        model_name: str,
        model_version: str,
        model_path: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """모델 등록"""
        model_id = hashlib.md5(f"{model_name}:{model_version}".encode()).hexdigest()[:8]

        if model_name not in self.models:
            self.models[model_name] = {}

        self.models[model_name][model_version] = {
            'id': model_id,
            'path': model_path,
            'registered_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        self._save_registry()
        logger.info(f"Registered model: {model_name} v{model_version} (ID: {model_id})")
        return model_id

    def get_model(self, model_name: str, model_version: Optional[str] = None) -> Optional[Dict]:
        """모델 정보 조회"""
        if model_name not in self.models:
            return None

        if model_version is None:
            # 최신 버전 반환
            versions = sorted(self.models[model_name].keys(), reverse=True)
            if versions:
                return self.models[model_name][versions[0]]
        else:
            return self.models[model_name].get(model_version)

    def list_models(self) -> Dict:
        """등록된 모든 모델 목록"""
        return self.models