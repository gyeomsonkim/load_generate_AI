"""
모델 학습 스크립트
U-Net 세그멘테이션 모델 학습
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
import numpy as np
from pathlib import Path
from tqdm import tqdm
import logging
import argparse
import json
import wandb
from typing import Dict, Optional, Tuple
from datetime import datetime

from app.core.ml.data_pipeline import DataPipeline, MapDataset, DatasetGenerator
from app.core.ml.segmentation.segmentation_model import MapSegmentationModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiceLoss(nn.Module):
    """Dice Loss for segmentation"""

    def __init__(self, smooth: float = 1.0):
        super().__init__()
        self.smooth = smooth

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        pred = torch.softmax(pred, dim=1)
        num_classes = pred.shape[1]
        target_one_hot = torch.nn.functional.one_hot(target, num_classes).permute(0, 3, 1, 2).float()

        dice_loss = 0
        for i in range(num_classes):
            pred_i = pred[:, i]
            target_i = target_one_hot[:, i]
            intersection = (pred_i * target_i).sum(dim=(1, 2))
            union = pred_i.sum(dim=(1, 2)) + target_i.sum(dim=(1, 2))
            dice_i = (2. * intersection + self.smooth) / (union + self.smooth)
            dice_loss += (1 - dice_i.mean())

        return dice_loss / num_classes


class FocalLoss(nn.Module):
    """Focal Loss for class imbalance"""

    def __init__(self, alpha: float = 0.25, gamma: float = 2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.ce_loss = nn.CrossEntropyLoss(reduction='none')

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        ce_loss = self.ce_loss(pred, target)
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        return focal_loss.mean()


class CombinedLoss(nn.Module):
    """Combined loss (CE + Dice + Focal)"""

    def __init__(self, ce_weight: float = 1.0, dice_weight: float = 1.0, focal_weight: float = 0.5):
        super().__init__()
        self.ce_loss = nn.CrossEntropyLoss()
        self.dice_loss = DiceLoss()
        self.focal_loss = FocalLoss()
        self.ce_weight = ce_weight
        self.dice_weight = dice_weight
        self.focal_weight = focal_weight

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> Tuple[torch.Tensor, Dict[str, float]]:
        ce = self.ce_loss(pred, target)
        dice = self.dice_loss(pred, target)
        focal = self.focal_loss(pred, target)

        total_loss = (self.ce_weight * ce +
                     self.dice_weight * dice +
                     self.focal_weight * focal)

        loss_dict = {
            'ce_loss': ce.item(),
            'dice_loss': dice.item(),
            'focal_loss': focal.item(),
            'total_loss': total_loss.item()
        }

        return total_loss, loss_dict


class Trainer:
    """모델 학습 클래스"""

    def __init__(
        self,
        model: MapSegmentationModel,
        config: Dict,
        use_wandb: bool = False
    ):
        self.model = model
        self.config = config
        self.device = model.device
        self.use_wandb = use_wandb

        # 학습 설정
        self.num_epochs = config.get('num_epochs', 100)
        self.learning_rate = config.get('learning_rate', 1e-3)
        self.batch_size = config.get('batch_size', 16)
        self.num_workers = config.get('num_workers', 4)
        self.save_interval = config.get('save_interval', 5)

        # 손실 함수
        self.criterion = CombinedLoss()

        # 옵티마이저
        self.optimizer = optim.AdamW(
            self.model.model.parameters(),
            lr=self.learning_rate,
            weight_decay=config.get('weight_decay', 1e-4)
        )

        # 학습률 스케줄러
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer,
            T_max=self.num_epochs,
            eta_min=1e-6
        )

        # 조기 종료
        self.patience = config.get('patience', 15)
        self.best_val_loss = float('inf')
        self.patience_counter = 0

        # 로깅
        self.log_dir = Path(config.get('log_dir', 'logs'))
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.writer = SummaryWriter(self.log_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        # W&B 초기화
        if self.use_wandb:
            wandb.init(
                project="map-segmentation",
                config=config,
                name=f"{model.model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            wandb.watch(model.model)

    def train(self, train_loader: DataLoader, val_loader: DataLoader):
        """학습 실행"""
        logger.info(f"Starting training for {self.num_epochs} epochs")

        for epoch in range(1, self.num_epochs + 1):
            # 학습
            train_loss, train_metrics = self._train_epoch(train_loader, epoch)

            # 검증
            val_loss, val_metrics = self._validate(val_loader, epoch)

            # 학습률 업데이트
            self.scheduler.step()

            # 로깅
            self._log_metrics(epoch, train_loss, train_metrics, val_loss, val_metrics)

            # 모델 저장
            if epoch % self.save_interval == 0:
                self._save_checkpoint(epoch, val_loss)

            # 조기 종료 체크
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self.patience_counter = 0
                self._save_best_model()
            else:
                self.patience_counter += 1
                if self.patience_counter >= self.patience:
                    logger.info(f"Early stopping at epoch {epoch}")
                    break

        self.writer.close()
        if self.use_wandb:
            wandb.finish()

    def _train_epoch(self, train_loader: DataLoader, epoch: int) -> Tuple[float, Dict]:
        """한 에폭 학습"""
        self.model.model.train()
        total_loss = 0
        metrics = {'iou': 0, 'dice': 0, 'accuracy': 0}
        num_batches = len(train_loader)

        with tqdm(train_loader, desc=f"Epoch {epoch}/{self.num_epochs} [Train]") as pbar:
            for batch_idx, batch in enumerate(pbar):
                images = batch['image'].to(self.device)
                masks = batch['mask'].to(self.device)

                # Forward pass
                outputs = self.model.model(images)
                loss, loss_dict = self.criterion(outputs, masks)

                # Backward pass
                self.optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.model.parameters(), max_norm=1.0)
                self.optimizer.step()

                # 메트릭 계산
                batch_metrics = self._calculate_metrics(outputs, masks)
                for key in metrics:
                    metrics[key] += batch_metrics[key]

                total_loss += loss.item()

                # 진행 상황 업데이트
                pbar.set_postfix({
                    'loss': loss.item(),
                    'iou': batch_metrics['iou']
                })

                # 텐서보드 로깅 (배치별)
                global_step = (epoch - 1) * num_batches + batch_idx
                if batch_idx % 10 == 0:
                    self.writer.add_scalar('Train/batch_loss', loss.item(), global_step)

        # 평균 계산
        avg_loss = total_loss / num_batches
        for key in metrics:
            metrics[key] /= num_batches

        return avg_loss, metrics

    def _validate(self, val_loader: DataLoader, epoch: int) -> Tuple[float, Dict]:
        """검증 실행"""
        self.model.model.eval()
        total_loss = 0
        metrics = {'iou': 0, 'dice': 0, 'accuracy': 0}
        num_batches = len(val_loader)

        with torch.no_grad():
            with tqdm(val_loader, desc=f"Epoch {epoch}/{self.num_epochs} [Val]") as pbar:
                for batch in pbar:
                    images = batch['image'].to(self.device)
                    masks = batch['mask'].to(self.device)

                    # Forward pass
                    outputs = self.model.model(images)
                    loss, _ = self.criterion(outputs, masks)

                    # 메트릭 계산
                    batch_metrics = self._calculate_metrics(outputs, masks)
                    for key in metrics:
                        metrics[key] += batch_metrics[key]

                    total_loss += loss.item()

                    # 진행 상황 업데이트
                    pbar.set_postfix({
                        'loss': loss.item(),
                        'iou': batch_metrics['iou']
                    })

        # 평균 계산
        avg_loss = total_loss / num_batches
        for key in metrics:
            metrics[key] /= num_batches

        return avg_loss, metrics

    def _calculate_metrics(self, outputs: torch.Tensor, targets: torch.Tensor) -> Dict[str, float]:
        """메트릭 계산"""
        preds = torch.argmax(outputs, dim=1)

        # IoU 계산
        intersection = torch.sum((preds == 1) & (targets == 1)).float()
        union = torch.sum((preds == 1) | (targets == 1)).float()
        iou = (intersection / (union + 1e-6)).item()

        # Dice coefficient
        dice = (2 * intersection / (torch.sum(preds == 1) + torch.sum(targets == 1) + 1e-6)).item()

        # Pixel accuracy
        accuracy = (torch.sum(preds == targets) / targets.numel()).item()

        return {
            'iou': iou,
            'dice': dice,
            'accuracy': accuracy
        }

    def _log_metrics(
        self,
        epoch: int,
        train_loss: float,
        train_metrics: Dict,
        val_loss: float,
        val_metrics: Dict
    ):
        """메트릭 로깅"""
        # 콘솔 출력
        logger.info(
            f"Epoch {epoch}: "
            f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, "
            f"Val IoU: {val_metrics['iou']:.4f}, Val Dice: {val_metrics['dice']:.4f}"
        )

        # TensorBoard
        self.writer.add_scalars('Loss', {
            'train': train_loss,
            'val': val_loss
        }, epoch)

        self.writer.add_scalars('IoU', {
            'train': train_metrics['iou'],
            'val': val_metrics['iou']
        }, epoch)

        self.writer.add_scalars('Dice', {
            'train': train_metrics['dice'],
            'val': val_metrics['dice']
        }, epoch)

        self.writer.add_scalar('Learning_Rate',
                              self.optimizer.param_groups[0]['lr'], epoch)

        # W&B
        if self.use_wandb:
            wandb.log({
                'epoch': epoch,
                'train_loss': train_loss,
                'val_loss': val_loss,
                'train_iou': train_metrics['iou'],
                'val_iou': val_metrics['iou'],
                'train_dice': train_metrics['dice'],
                'val_dice': val_metrics['dice'],
                'lr': self.optimizer.param_groups[0]['lr']
            })

    def _save_checkpoint(self, epoch: int, val_loss: float):
        """체크포인트 저장"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'val_loss': val_loss,
            'config': self.config
        }

        checkpoint_path = self.model.model_dir / f"checkpoint_epoch_{epoch}.pth"
        torch.save(checkpoint, checkpoint_path)
        logger.info(f"Saved checkpoint: {checkpoint_path}")

    def _save_best_model(self):
        """최고 성능 모델 저장"""
        best_path = self.model.model_dir / "best_model.pth"
        torch.save(self.model.model.state_dict(), best_path)
        logger.info(f"Saved best model: {best_path}")


def main():
    """메인 학습 함수"""
    parser = argparse.ArgumentParser(description="Train segmentation model")
    parser.add_argument('--data_dir', type=str, default='datasets/maps',
                       help='Dataset directory')
    parser.add_argument('--model_type', type=str, default='unet',
                       choices=['unet', 'attention_unet', 'deeplabv3plus'],
                       help='Model type')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Number of epochs')
    parser.add_argument('--batch_size', type=int, default=16,
                       help='Batch size')
    parser.add_argument('--lr', type=float, default=1e-3,
                       help='Learning rate')
    parser.add_argument('--generate_data', action='store_true',
                       help='Generate synthetic dataset')
    parser.add_argument('--use_wandb', action='store_true',
                       help='Use Weights & Biases')
    args = parser.parse_args()

    # 설정
    config = {
        'num_epochs': args.epochs,
        'batch_size': args.batch_size,
        'learning_rate': args.lr,
        'num_workers': 4,
        'weight_decay': 1e-4,
        'save_interval': 5,
        'patience': 15,
        'log_dir': 'logs',
        'image_size': (512, 512)
    }

    # 데이터셋 생성 (필요한 경우)
    if args.generate_data or not Path(args.data_dir).exists():
        logger.info("Generating synthetic dataset...")
        generator = DatasetGenerator(args.data_dir, num_samples=1000)
        generator.generate_dataset()

    # 데이터 파이프라인
    pipeline = DataPipeline(config)
    train_loader = pipeline.create_dataloader(args.data_dir, mode='train')
    val_loader = pipeline.create_dataloader(args.data_dir, mode='val')

    # 모델 초기화
    model = MapSegmentationModel(
        model_type=args.model_type,
        n_classes=4,
        model_version="1.0.0"
    )

    # 학습기 초기화
    trainer = Trainer(model, config, use_wandb=args.use_wandb)

    # 학습 실행
    trainer.train(train_loader, val_loader)

    logger.info("Training completed!")


if __name__ == "__main__":
    main()