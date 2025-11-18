"""
세그멘테이션 모델 통합 클래스
U-Net 모델을 BaseMLModel과 통합하여 사용
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import cv2
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union, List
import logging

from app.core.ml.base import BaseMLModel
from app.core.ml.segmentation.unet import UNet, AttentionUNet, DeepLabV3Plus

logger = logging.getLogger(__name__)


class MapSegmentationModel(BaseMLModel):
    """지도 세그멘테이션 모델"""

    def __init__(
        self,
        model_type: str = 'unet',  # 'unet', 'attention_unet', 'deeplabv3plus'
        n_classes: int = 4,
        model_version: str = "1.0.0",
        device: Optional[str] = None,
        pretrained_path: Optional[str] = None
    ):
        super().__init__(
            model_name=f"map_segmentation_{model_type}",
            model_version=model_version,
            device=device
        )

        self.model_type = model_type
        self.n_classes = n_classes
        self.pretrained_path = pretrained_path

        # 클래스 정의
        self.classes = {
            0: 'background',
            1: 'walkable',
            2: 'obstacle',
            3: 'wall'
        }

        # 클래스별 색상 (시각화용)
        self.class_colors = {
            0: [0, 0, 0],        # 배경 - 검정
            1: [0, 255, 0],      # 보행가능 - 녹색
            2: [255, 0, 0],      # 장애물 - 빨강
            3: [128, 128, 128]   # 벽 - 회색
        }

        # 모델 초기화
        self.model = self.build_model()

        # 사전 학습된 가중치 로드
        if pretrained_path:
            self.load_pretrained_weights(pretrained_path)
        else:
            # 기본 가중치 로드 시도
            default_path = self.model_dir / f"{self.model_name}.pth"
            if default_path.exists():
                self.load_model(str(default_path))

        logger.info(f"Initialized {model_type} segmentation model with {n_classes} classes")

    def build_model(self) -> nn.Module:
        """모델 아키텍처 구축"""
        if self.model_type == 'unet':
            model = UNet(n_channels=3, n_classes=self.n_classes, bilinear=False)
        elif self.model_type == 'attention_unet':
            model = AttentionUNet(n_channels=3, n_classes=self.n_classes)
        elif self.model_type == 'deeplabv3plus':
            model = DeepLabV3Plus(n_classes=self.n_classes)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

        model = model.to(self.device)
        return model

    def preprocess(self, input_data: Union[np.ndarray, str]) -> torch.Tensor:
        """입력 데이터 전처리"""
        # 이미지 로드 (경로인 경우)
        if isinstance(input_data, str):
            image = cv2.imread(input_data)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image = input_data
            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
            elif image.shape[2] == 3 and isinstance(input_data, np.ndarray):
                # OpenCV는 기본적으로 BGR을 사용
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 원본 크기 저장
        self.original_size = (image.shape[1], image.shape[0])

        # 리사이즈 (512x512)
        image = cv2.resize(image, (512, 512))

        # 정규화 및 텐서 변환
        image = image.astype(np.float32) / 255.0
        image = image.transpose(2, 0, 1)  # HWC -> CHW
        image = torch.from_numpy(image)

        # ImageNet 정규화
        mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
        image = (image - mean) / std

        # 배치 차원 추가
        image = image.unsqueeze(0)

        return image

    def postprocess(self, output: torch.Tensor) -> Dict[str, Any]:
        """모델 출력 후처리"""
        # Softmax 적용 (logits -> probabilities)
        probs = F.softmax(output, dim=1)

        # Argmax로 클래스 예측
        pred_mask = torch.argmax(probs, dim=1)  # B, H, W

        # 첫 번째 배치 선택
        pred_mask = pred_mask[0].cpu().numpy().astype(np.uint8)

        # 원본 크기로 리사이즈
        pred_mask = cv2.resize(pred_mask, self.original_size, interpolation=cv2.INTER_NEAREST)

        # 클래스별 확률 맵
        class_probs = {}
        for i in range(self.n_classes):
            prob_map = probs[0, i].cpu().numpy()
            prob_map = cv2.resize(prob_map, self.original_size, interpolation=cv2.INTER_LINEAR)
            class_probs[self.classes[i]] = prob_map

        # 결과 구성
        result = {
            'segmentation_mask': pred_mask,
            'class_probabilities': class_probs,
            'walkable_mask': (pred_mask == 1).astype(np.uint8),
            'obstacle_mask': (pred_mask == 2).astype(np.uint8),
            'wall_mask': (pred_mask == 3).astype(np.uint8),
            'statistics': self._calculate_statistics(pred_mask)
        }

        return result

    def _calculate_statistics(self, mask: np.ndarray) -> Dict[str, float]:
        """마스크 통계 계산"""
        total_pixels = mask.size
        stats = {}

        for class_id, class_name in self.classes.items():
            pixel_count = np.sum(mask == class_id)
            percentage = (pixel_count / total_pixels) * 100
            stats[f'{class_name}_percentage'] = round(percentage, 2)
            stats[f'{class_name}_pixels'] = int(pixel_count)

        return stats

    def segment_map(self, image: Union[np.ndarray, str]) -> Dict[str, Any]:
        """지도 이미지 세그멘테이션 실행"""
        return self.predict(image)

    def visualize_segmentation(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        alpha: float = 0.5
    ) -> np.ndarray:
        """세그멘테이션 결과 시각화"""
        # BGR to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            vis_image = image.copy()
        else:
            vis_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        # 마스크 크기 맞추기
        if mask.shape[:2] != vis_image.shape[:2]:
            mask = cv2.resize(mask, (vis_image.shape[1], vis_image.shape[0]),
                            interpolation=cv2.INTER_NEAREST)

        # 컬러 오버레이 생성
        overlay = np.zeros_like(vis_image)
        for class_id, color in self.class_colors.items():
            overlay[mask == class_id] = color

        # 블렌딩
        result = cv2.addWeighted(vis_image, 1 - alpha, overlay, alpha, 0)

        # 경계선 추가 (선택적)
        edges = cv2.Canny(mask.astype(np.uint8) * 50, 50, 100)
        edges = cv2.dilate(edges, np.ones((2, 2), np.uint8), iterations=1)
        result[edges > 0] = [255, 255, 0]  # 노란색 경계

        return result

    def extract_navigation_grid(
        self,
        segmentation_mask: np.ndarray,
        cell_size: int = 5
    ) -> np.ndarray:
        """세그멘테이션 결과에서 네비게이션 그리드 생성"""
        # 보행 가능 영역만 추출
        walkable = (segmentation_mask == 1).astype(np.uint8)

        # 그리드 크기 계산
        h, w = walkable.shape
        grid_h = h // cell_size
        grid_w = w // cell_size

        # 그리드 생성
        grid = np.zeros((grid_h, grid_w), dtype=np.uint8)

        for i in range(grid_h):
            for j in range(grid_w):
                cell = walkable[
                    i * cell_size:(i + 1) * cell_size,
                    j * cell_size:(j + 1) * cell_size
                ]
                # 셀의 70% 이상이 보행 가능하면 1
                if np.mean(cell) > 0.7:
                    grid[i, j] = 1

        return grid

    def load_pretrained_weights(self, weights_path: str):
        """사전 학습된 가중치 로드"""
        try:
            if not Path(weights_path).exists():
                logger.warning(f"Pretrained weights not found: {weights_path}")
                return False

            state_dict = torch.load(weights_path, map_location=self.device)

            # 가중치만 있는 경우
            if not isinstance(state_dict, dict) or 'model_state_dict' not in state_dict:
                self.model.load_state_dict(state_dict)
            else:
                self.model.load_state_dict(state_dict['model_state_dict'])

            self.model.eval()
            logger.info(f"Loaded pretrained weights from: {weights_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load pretrained weights: {e}")
            return False

    def compare_with_cv(
        self,
        image: np.ndarray,
        cv_result: Dict[str, Any]
    ) -> Dict[str, float]:
        """Computer Vision 방식과 결과 비교"""
        # ML 세그멘테이션 실행
        ml_result = self.segment_map(image)
        ml_mask = ml_result['walkable_mask']

        # CV 결과 로드
        cv_mask = cv_result.get('walkable_mask', np.zeros_like(ml_mask))

        # 크기 맞추기
        if cv_mask.shape != ml_mask.shape:
            cv_mask = cv2.resize(cv_mask, ml_mask.shape[::-1], interpolation=cv2.INTER_NEAREST)

        # IoU (Intersection over Union) 계산
        intersection = np.sum((ml_mask == 1) & (cv_mask == 1))
        union = np.sum((ml_mask == 1) | (cv_mask == 1))
        iou = intersection / (union + 1e-6)

        # Dice coefficient 계산
        dice = 2 * intersection / (np.sum(ml_mask) + np.sum(cv_mask) + 1e-6)

        # Pixel accuracy
        accuracy = np.sum(ml_mask == cv_mask) / ml_mask.size

        return {
            'iou': float(iou),
            'dice': float(dice),
            'pixel_accuracy': float(accuracy),
            'ml_walkable_ratio': float(np.mean(ml_mask)),
            'cv_walkable_ratio': float(np.mean(cv_mask))
        }


class EnsembleSegmentation:
    """여러 세그멘테이션 모델의 앙상블"""

    def __init__(self, models: List[MapSegmentationModel]):
        self.models = models
        self.num_models = len(models)
        logger.info(f"Initialized ensemble with {self.num_models} models")

    def predict(self, image: Union[np.ndarray, str]) -> Dict[str, Any]:
        """앙상블 예측"""
        # 각 모델의 예측 수집
        all_probs = []

        for model in self.models:
            # 전처리
            processed = model.preprocess(image)

            # 예측
            with torch.no_grad():
                logits = model.model(processed.to(model.device))
                probs = F.softmax(logits, dim=1)
                all_probs.append(probs.cpu())

        # 확률 평균
        avg_probs = torch.stack(all_probs).mean(dim=0)

        # 최종 예측
        pred_mask = torch.argmax(avg_probs, dim=1)[0].numpy().astype(np.uint8)

        # 원본 크기로 리사이즈
        original_size = self.models[0].original_size
        pred_mask = cv2.resize(pred_mask, original_size, interpolation=cv2.INTER_NEAREST)

        return {
            'segmentation_mask': pred_mask,
            'ensemble_confidence': torch.max(avg_probs).item(),
            'walkable_mask': (pred_mask == 1).astype(np.uint8),
            'obstacle_mask': (pred_mask == 2).astype(np.uint8),
            'wall_mask': (pred_mask == 3).astype(np.uint8)
        }