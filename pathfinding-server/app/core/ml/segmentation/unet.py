"""
U-Net 세그멘테이션 모델
지도 이미지의 픽셀 단위 분류를 위한 딥러닝 모델
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)


class DoubleConv(nn.Module):
    """U-Net의 기본 구성 블록: Double Convolution"""

    def __init__(self, in_channels: int, out_channels: int, mid_channels: Optional[int] = None):
        super().__init__()
        if not mid_channels:
            mid_channels = out_channels

        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, mid_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(mid_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(mid_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.double_conv(x)


class Down(nn.Module):
    """Downscaling with maxpool then double conv"""

    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.maxpool_conv = nn.Sequential(
            nn.MaxPool2d(2),
            DoubleConv(in_channels, out_channels)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.maxpool_conv(x)


class Up(nn.Module):
    """Upscaling then double conv"""

    def __init__(self, in_channels: int, out_channels: int, bilinear: bool = True):
        super().__init__()

        # Bilinear upsampling vs Transposed convolution
        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
            self.conv = DoubleConv(in_channels, out_channels, in_channels // 2)
        else:
            self.up = nn.ConvTranspose2d(in_channels, in_channels // 2, kernel_size=2, stride=2)
            self.conv = DoubleConv(in_channels, out_channels)

    def forward(self, x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
        x1 = self.up(x1)

        # 입력 크기 차이 처리 (패딩)
        diffY = x2.size()[2] - x1.size()[2]
        diffX = x2.size()[3] - x1.size()[3]

        x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2,
                        diffY // 2, diffY - diffY // 2])

        # Skip connection
        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)


class OutConv(nn.Module):
    """Final convolution"""

    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(x)


class UNet(nn.Module):
    """U-Net 아키텍처"""

    def __init__(
        self,
        n_channels: int = 3,
        n_classes: int = 4,
        bilinear: bool = False,
        base_features: int = 64
    ):
        super().__init__()
        self.n_channels = n_channels
        self.n_classes = n_classes
        self.bilinear = bilinear

        # Encoder (Contracting path)
        self.inc = DoubleConv(n_channels, base_features)
        self.down1 = Down(base_features, base_features * 2)
        self.down2 = Down(base_features * 2, base_features * 4)
        self.down3 = Down(base_features * 4, base_features * 8)
        factor = 2 if bilinear else 1
        self.down4 = Down(base_features * 8, base_features * 16 // factor)

        # Decoder (Expanding path)
        self.up1 = Up(base_features * 16, base_features * 8 // factor, bilinear)
        self.up2 = Up(base_features * 8, base_features * 4 // factor, bilinear)
        self.up3 = Up(base_features * 4, base_features * 2 // factor, bilinear)
        self.up4 = Up(base_features * 2, base_features, bilinear)

        # Output
        self.outc = OutConv(base_features, n_classes)

        # Dropout for regularization
        self.dropout = nn.Dropout2d(p=0.2)

        logger.info(f"Initialized UNet with {n_channels} input channels and {n_classes} classes")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Encoder
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)

        # Decoder with skip connections
        x = self.up1(x5, x4)
        x = self.dropout(x)  # Dropout in decoder
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        x = self.up4(x, x1)

        # Output
        logits = self.outc(x)
        return logits


class AttentionUNet(nn.Module):
    """Attention U-Net with attention gates"""

    def __init__(
        self,
        n_channels: int = 3,
        n_classes: int = 4,
        base_features: int = 64
    ):
        super().__init__()
        self.n_channels = n_channels
        self.n_classes = n_classes

        # Encoder
        self.inc = DoubleConv(n_channels, base_features)
        self.down1 = Down(base_features, base_features * 2)
        self.down2 = Down(base_features * 2, base_features * 4)
        self.down3 = Down(base_features * 4, base_features * 8)
        self.down4 = Down(base_features * 8, base_features * 16)

        # Attention Gates
        self.att1 = AttentionGate(base_features * 16, base_features * 8, base_features * 8)
        self.att2 = AttentionGate(base_features * 8, base_features * 4, base_features * 4)
        self.att3 = AttentionGate(base_features * 4, base_features * 2, base_features * 2)
        self.att4 = AttentionGate(base_features * 2, base_features, base_features)

        # Decoder
        self.up1 = UpWithAttention(base_features * 16, base_features * 8)
        self.up2 = UpWithAttention(base_features * 8, base_features * 4)
        self.up3 = UpWithAttention(base_features * 4, base_features * 2)
        self.up4 = UpWithAttention(base_features * 2, base_features)

        # Output
        self.outc = OutConv(base_features, n_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Encoder
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)

        # Decoder with attention
        x4_att = self.att1(x5, x4)
        x = self.up1(x5, x4_att)

        x3_att = self.att2(x, x3)
        x = self.up2(x, x3_att)

        x2_att = self.att3(x, x2)
        x = self.up3(x, x2_att)

        x1_att = self.att4(x, x1)
        x = self.up4(x, x1_att)

        # Output
        logits = self.outc(x)
        return logits


class AttentionGate(nn.Module):
    """Attention Gate for Attention U-Net"""

    def __init__(self, F_g: int, F_l: int, F_int: int):
        super().__init__()
        self.W_g = nn.Sequential(
            nn.Conv2d(F_g, F_int, kernel_size=1, stride=1, padding=0, bias=True),
            nn.BatchNorm2d(F_int)
        )

        self.W_x = nn.Sequential(
            nn.Conv2d(F_l, F_int, kernel_size=1, stride=1, padding=0, bias=True),
            nn.BatchNorm2d(F_int)
        )

        self.psi = nn.Sequential(
            nn.Conv2d(F_int, 1, kernel_size=1, stride=1, padding=0, bias=True),
            nn.BatchNorm2d(1),
            nn.Sigmoid()
        )

        self.relu = nn.ReLU(inplace=True)

    def forward(self, g: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
        g1 = self.W_g(g)
        x1 = self.W_x(x)
        psi = self.relu(g1 + x1)
        psi = self.psi(psi)
        return x * psi


class UpWithAttention(nn.Module):
    """Upsampling with attention for Attention U-Net"""

    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.up = nn.ConvTranspose2d(in_channels, in_channels // 2, kernel_size=2, stride=2)
        self.conv = DoubleConv(in_channels, out_channels)

    def forward(self, x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
        x1 = self.up(x1)

        # Handle size differences
        diffY = x2.size()[2] - x1.size()[2]
        diffX = x2.size()[3] - x1.size()[3]

        x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2,
                        diffY // 2, diffY - diffY // 2])

        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)


class DeepLabV3Plus(nn.Module):
    """DeepLabV3+ for comparison (simplified version)"""

    def __init__(self, n_classes: int = 4, output_stride: int = 16):
        super().__init__()
        from torchvision.models import resnet50
        from torchvision.models._utils import IntermediateLayerGetter

        # Backbone (ResNet50)
        backbone = resnet50(pretrained=True)
        return_layers = {'layer4': 'out', 'layer1': 'low_level'}
        self.backbone = IntermediateLayerGetter(backbone, return_layers=return_layers)

        # ASPP (Atrous Spatial Pyramid Pooling)
        self.aspp = ASPP(2048, 256, output_stride)

        # Decoder
        self.decoder = Decoder(n_classes, 256, 256)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        input_shape = x.shape[-2:]

        features = self.backbone(x)
        x = self.aspp(features['out'])
        x = self.decoder(x, features['low_level'])
        x = F.interpolate(x, size=input_shape, mode='bilinear', align_corners=False)

        return x


class ASPP(nn.Module):
    """Atrous Spatial Pyramid Pooling"""

    def __init__(self, in_channels: int, out_channels: int, output_stride: int):
        super().__init__()
        if output_stride == 16:
            dilations = [1, 6, 12, 18]
        elif output_stride == 8:
            dilations = [1, 12, 24, 36]
        else:
            raise NotImplementedError

        self.aspp1 = ASPPConv(in_channels, out_channels, dilations[0])
        self.aspp2 = ASPPConv(in_channels, out_channels, dilations[1])
        self.aspp3 = ASPPConv(in_channels, out_channels, dilations[2])
        self.aspp4 = ASPPConv(in_channels, out_channels, dilations[3])
        self.global_avg_pool = ASPPPooling(in_channels, out_channels)

        self.project = nn.Sequential(
            nn.Conv2d(out_channels * 5, out_channels, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(),
            nn.Dropout(0.5)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        res1 = self.aspp1(x)
        res2 = self.aspp2(x)
        res3 = self.aspp3(x)
        res4 = self.aspp4(x)
        res5 = self.global_avg_pool(x)
        res = torch.cat([res1, res2, res3, res4, res5], dim=1)
        return self.project(res)


class ASPPConv(nn.Sequential):
    def __init__(self, in_channels: int, out_channels: int, dilation: int):
        modules = [
            nn.Conv2d(in_channels, out_channels, 3, padding=dilation, dilation=dilation, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU()
        ]
        super().__init__(*modules)


class ASPPPooling(nn.Sequential):
    def __init__(self, in_channels: int, out_channels: int):
        super().__init__(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(in_channels, out_channels, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        size = x.shape[-2:]
        for mod in self:
            x = mod(x)
        return F.interpolate(x, size=size, mode='bilinear', align_corners=False)


class Decoder(nn.Module):
    def __init__(self, n_classes: int, feature_channels: int, low_level_channels: int):
        super().__init__()
        self.conv1 = nn.Conv2d(low_level_channels, 48, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(48)
        self.relu = nn.ReLU()

        self.last_conv = nn.Sequential(
            nn.Conv2d(feature_channels + 48, 256, 3, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Conv2d(256, 256, 3, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Conv2d(256, n_classes, 1)
        )

    def forward(self, x: torch.Tensor, low_level_feat: torch.Tensor) -> torch.Tensor:
        low_level_feat = self.conv1(low_level_feat)
        low_level_feat = self.bn1(low_level_feat)
        low_level_feat = self.relu(low_level_feat)

        x = F.interpolate(x, size=low_level_feat.shape[-2:], mode='bilinear', align_corners=False)
        x = torch.cat([x, low_level_feat], dim=1)
        x = self.last_conv(x)

        return x