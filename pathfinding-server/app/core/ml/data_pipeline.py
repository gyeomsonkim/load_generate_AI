"""
데이터 파이프라인 및 전처리
학습/추론을 위한 데이터 처리 파이프라인
"""
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from torchvision.transforms import functional as TF
import numpy as np
import cv2
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Any, Callable
import json
import random
import logging
from PIL import Image
import albumentations as A
from albumentations.pytorch import ToTensorV2

logger = logging.getLogger(__name__)


class MapDataset(Dataset):
    """지도 세그멘테이션 데이터셋"""

    def __init__(
        self,
        data_dir: str,
        mode: str = 'train',
        transform: Optional[Callable] = None,
        augment: bool = True,
        image_size: Tuple[int, int] = (512, 512)
    ):
        self.data_dir = Path(data_dir)
        self.mode = mode
        self.transform = transform
        self.augment = augment and mode == 'train'
        self.image_size = image_size

        # 클래스 정의 (0: 배경, 1: 보행가능, 2: 장애물, 3: 벽)
        self.classes = {
            'background': 0,
            'walkable': 1,
            'obstacle': 2,
            'wall': 3
        }
        self.num_classes = len(self.classes)

        # 데이터 로드
        self.images = []
        self.masks = []
        self._load_data()

        logger.info(f"Loaded {len(self.images)} samples for {mode}")

    def _load_data(self):
        """데이터 파일 로드"""
        image_dir = self.data_dir / 'images' / self.mode
        mask_dir = self.data_dir / 'masks' / self.mode

        if not image_dir.exists():
            logger.warning(f"Data directory not found: {image_dir}")
            # 더미 데이터 생성 (데모용)
            self._create_dummy_data()
            return

        # 이미지와 마스크 파일 매칭
        for img_path in sorted(image_dir.glob('*.png')):
            mask_path = mask_dir / img_path.name
            if mask_path.exists():
                self.images.append(str(img_path))
                self.masks.append(str(mask_path))

    def _create_dummy_data(self):
        """데모용 더미 데이터 생성"""
        logger.info("Creating dummy data for demonstration")
        for i in range(100):
            self.images.append(f"dummy_image_{i}")
            self.masks.append(f"dummy_mask_{i}")

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        # 실제 파일이 있는 경우
        if Path(self.images[idx]).exists():
            image = cv2.imread(self.images[idx])
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mask = cv2.imread(self.masks[idx], cv2.IMREAD_GRAYSCALE)
        else:
            # 더미 데이터 생성
            image = np.random.randint(0, 255, (*self.image_size, 3), dtype=np.uint8)
            mask = np.random.randint(0, self.num_classes, self.image_size, dtype=np.uint8)

        # 리사이즈
        image = cv2.resize(image, self.image_size)
        mask = cv2.resize(mask, self.image_size, interpolation=cv2.INTER_NEAREST)

        # Augmentation
        if self.augment:
            augmented = self.get_augmentation()(image=image, mask=mask)
            image = augmented['image']
            mask = augmented['mask']

        # Transform 적용
        if self.transform:
            image = self.transform(image)
            mask = torch.from_numpy(mask).long()
        else:
            # 기본 변환
            image = torch.from_numpy(image.transpose(2, 0, 1)).float() / 255.0
            mask = torch.from_numpy(mask).long()

        return {
            'image': image,
            'mask': mask,
            'image_path': self.images[idx]
        }

    def get_augmentation(self):
        """데이터 증강 파이프라인"""
        return A.Compose([
            A.RandomRotate90(p=0.5),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomBrightnessContrast(
                brightness_limit=0.2,
                contrast_limit=0.2,
                p=0.5
            ),
            A.GaussNoise(var_limit=(10.0, 50.0), p=0.3),
            A.GaussianBlur(blur_limit=5, p=0.3),
            A.RandomGamma(gamma_limit=(80, 120), p=0.3),
            A.ElasticTransform(
                alpha=120,
                sigma=6,
                alpha_affine=3.6,
                p=0.3
            ),
            A.GridDistortion(p=0.2),
            A.OpticalDistortion(p=0.2),
        ])


class DataPipeline:
    """데이터 처리 파이프라인"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.batch_size = self.config.get('batch_size', 16)
        self.num_workers = self.config.get('num_workers', 4)
        self.image_size = self.config.get('image_size', (512, 512))

        # 정규화 파라미터 (ImageNet 기준)
        self.mean = [0.485, 0.456, 0.406]
        self.std = [0.229, 0.224, 0.225]

    def get_transforms(self, mode: str = 'train') -> transforms.Compose:
        """모드별 변환 정의"""
        if mode == 'train':
            return transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize(self.image_size),
                transforms.ToTensor(),
                transforms.Normalize(mean=self.mean, std=self.std)
            ])
        else:
            return transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize(self.image_size),
                transforms.ToTensor(),
                transforms.Normalize(mean=self.mean, std=self.std)
            ])

    def create_dataloader(
        self,
        data_dir: str,
        mode: str = 'train',
        shuffle: Optional[bool] = None
    ) -> DataLoader:
        """데이터로더 생성"""
        if shuffle is None:
            shuffle = (mode == 'train')

        dataset = MapDataset(
            data_dir=data_dir,
            mode=mode,
            transform=None,  # Dataset 내부에서 처리
            augment=(mode == 'train'),
            image_size=self.image_size
        )

        dataloader = DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=shuffle,
            num_workers=self.num_workers,
            pin_memory=torch.cuda.is_available(),
            drop_last=(mode == 'train')
        )

        return dataloader

    def preprocess_image(self, image: np.ndarray) -> torch.Tensor:
        """단일 이미지 전처리 (추론용)"""
        # BGR to RGB
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 리사이즈
        image = cv2.resize(image, self.image_size)

        # 텐서 변환 및 정규화
        image = image.transpose(2, 0, 1).astype(np.float32) / 255.0
        image = torch.from_numpy(image)

        # 정규화
        for i, (mean, std) in enumerate(zip(self.mean, self.std)):
            image[i] = (image[i] - mean) / std

        # 배치 차원 추가
        return image.unsqueeze(0)

    def postprocess_mask(self, mask: torch.Tensor, original_size: Tuple[int, int]) -> np.ndarray:
        """마스크 후처리 (추론 결과 변환)"""
        # Softmax/Argmax 적용
        if len(mask.shape) == 4:  # B, C, H, W
            mask = torch.argmax(mask, dim=1)  # B, H, W

        # 첫 번째 배치 선택
        if len(mask.shape) == 3:
            mask = mask[0]

        # NumPy 변환
        mask = mask.cpu().numpy().astype(np.uint8)

        # 원본 크기로 리사이즈
        mask = cv2.resize(mask, original_size, interpolation=cv2.INTER_NEAREST)

        return mask

    def visualize_segmentation(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        alpha: float = 0.5
    ) -> np.ndarray:
        """세그멘테이션 결과 시각화"""
        # 컬러맵 정의
        colors = {
            0: [0, 0, 0],        # 배경 - 검정
            1: [0, 255, 0],      # 보행가능 - 녹색
            2: [255, 0, 0],      # 장애물 - 빨강
            3: [128, 128, 128]   # 벽 - 회색
        }

        # 컬러 마스크 생성
        h, w = mask.shape
        color_mask = np.zeros((h, w, 3), dtype=np.uint8)

        for class_id, color in colors.items():
            color_mask[mask == class_id] = color

        # 오버레이
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        result = cv2.addWeighted(image, 1 - alpha, color_mask, alpha, 0)

        return result


class DataAugmentor:
    """고급 데이터 증강"""

    def __init__(self, augmentation_config: Optional[Dict] = None):
        self.config = augmentation_config or {}

    def get_training_augmentation(self, image_size: Tuple[int, int]) -> A.Compose:
        """학습용 증강 파이프라인"""
        return A.Compose([
            # 크기 조정
            A.Resize(*image_size),

            # 기하학적 변환
            A.RandomRotate90(p=0.5),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.Transpose(p=0.3),
            A.ShiftScaleRotate(
                shift_limit=0.1,
                scale_limit=0.2,
                rotate_limit=30,
                p=0.5
            ),

            # 색상 변환
            A.OneOf([
                A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3),
                A.RandomGamma(gamma_limit=(80, 120)),
                A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=30, val_shift_limit=20),
                A.CLAHE(clip_limit=4.0, tile_grid_size=(8, 8)),
            ], p=0.8),

            # 노이즈 및 블러
            A.OneOf([
                A.GaussNoise(var_limit=(10.0, 50.0)),
                A.GaussianBlur(blur_limit=5),
                A.MedianBlur(blur_limit=5),
                A.MotionBlur(blur_limit=5),
            ], p=0.4),

            # 왜곡
            A.OneOf([
                A.ElasticTransform(alpha=120, sigma=6, alpha_affine=3.6),
                A.GridDistortion(num_steps=5, distort_limit=0.3),
                A.OpticalDistortion(distort_limit=0.5, shift_limit=0.5),
            ], p=0.3),

            # CutOut 스타일 증강
            A.CoarseDropout(
                max_holes=8,
                max_height=32,
                max_width=32,
                min_holes=1,
                min_height=8,
                min_width=8,
                fill_value=0,
                p=0.3
            ),

            ToTensorV2()
        ])

    def get_validation_augmentation(self, image_size: Tuple[int, int]) -> A.Compose:
        """검증용 증강 (리사이즈만)"""
        return A.Compose([
            A.Resize(*image_size),
            ToTensorV2()
        ])

    def mixup(
        self,
        images: torch.Tensor,
        masks: torch.Tensor,
        alpha: float = 0.2
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """MixUp 증강"""
        batch_size = images.size(0)
        indices = torch.randperm(batch_size)

        lambda_val = np.random.beta(alpha, alpha)

        mixed_images = lambda_val * images + (1 - lambda_val) * images[indices]
        mixed_masks = masks  # 세그멘테이션에서는 마스크 믹싱 안함

        return mixed_images, mixed_masks

    def cutmix(
        self,
        images: torch.Tensor,
        masks: torch.Tensor,
        alpha: float = 1.0
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """CutMix 증강"""
        batch_size = images.size(0)
        indices = torch.randperm(batch_size)

        lambda_val = np.random.beta(alpha, alpha)
        h, w = images.size(-2), images.size(-1)

        # 랜덤 박스 생성
        cx = np.random.uniform(0, w)
        cy = np.random.uniform(0, h)
        w_box = w * np.sqrt(1 - lambda_val)
        h_box = h * np.sqrt(1 - lambda_val)

        x1 = int(np.clip(cx - w_box / 2, 0, w))
        x2 = int(np.clip(cx + w_box / 2, 0, w))
        y1 = int(np.clip(cy - h_box / 2, 0, h))
        y2 = int(np.clip(cy + h_box / 2, 0, h))

        # CutMix 적용
        images[:, :, y1:y2, x1:x2] = images[indices, :, y1:y2, x1:x2]
        masks[:, y1:y2, x1:x2] = masks[indices, y1:y2, x1:x2]

        return images, masks


class DatasetGenerator:
    """합성 데이터셋 생성기 (학습 데이터가 없을 때)"""

    def __init__(self, output_dir: str, num_samples: int = 1000):
        self.output_dir = Path(output_dir)
        self.num_samples = num_samples

        # 디렉토리 생성
        for split in ['train', 'val', 'test']:
            (self.output_dir / 'images' / split).mkdir(parents=True, exist_ok=True)
            (self.output_dir / 'masks' / split).mkdir(parents=True, exist_ok=True)

    def generate_synthetic_map(
        self,
        size: Tuple[int, int] = (512, 512)
    ) -> Tuple[np.ndarray, np.ndarray]:
        """합성 지도 이미지 및 마스크 생성"""
        h, w = size

        # 빈 이미지와 마스크 생성
        image = np.ones((h, w, 3), dtype=np.uint8) * 255
        mask = np.zeros((h, w), dtype=np.uint8)

        # 랜덤 벽 생성 (class 3)
        num_walls = random.randint(5, 15)
        for _ in range(num_walls):
            if random.random() > 0.5:
                # 수평 벽
                y = random.randint(50, h - 50)
                x1 = random.randint(0, w // 2)
                x2 = random.randint(w // 2, w)
                thickness = random.randint(5, 15)

                cv2.line(image, (x1, y), (x2, y), (128, 128, 128), thickness)
                cv2.line(mask, (x1, y), (x2, y), 3, thickness)
            else:
                # 수직 벽
                x = random.randint(50, w - 50)
                y1 = random.randint(0, h // 2)
                y2 = random.randint(h // 2, h)
                thickness = random.randint(5, 15)

                cv2.line(image, (x, y1), (x, y2), (128, 128, 128), thickness)
                cv2.line(mask, (x, y1), (x, y2), 3, thickness)

        # 랜덤 장애물 생성 (class 2)
        num_obstacles = random.randint(10, 30)
        for _ in range(num_obstacles):
            cx = random.randint(20, w - 20)
            cy = random.randint(20, h - 20)
            radius = random.randint(5, 20)

            cv2.circle(image, (cx, cy), radius, (255, 0, 0), -1)
            cv2.circle(mask, (cx, cy), radius, 2, -1)

        # 보행 가능 영역 표시 (class 1)
        walkable_mask = (mask == 0)
        mask[walkable_mask] = 1

        # 노이즈 추가
        noise = np.random.normal(0, 10, image.shape)
        image = np.clip(image + noise, 0, 255).astype(np.uint8)

        return image, mask

    def generate_dataset(self):
        """전체 데이터셋 생성"""
        splits = {'train': 0.7, 'val': 0.15, 'test': 0.15}

        sample_idx = 0
        for split, ratio in splits.items():
            num_split_samples = int(self.num_samples * ratio)

            for i in range(num_split_samples):
                image, mask = self.generate_synthetic_map()

                # 저장
                image_path = self.output_dir / 'images' / split / f'map_{sample_idx:04d}.png'
                mask_path = self.output_dir / 'masks' / split / f'map_{sample_idx:04d}.png'

                cv2.imwrite(str(image_path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                cv2.imwrite(str(mask_path), mask)

                sample_idx += 1

            logger.info(f"Generated {num_split_samples} samples for {split}")

        logger.info(f"Dataset generation complete: {self.num_samples} samples")