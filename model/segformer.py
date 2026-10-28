"""
SegFormer semantic segmentation module.
Extracts multi-scale transformer features for agricultural crop canopy segmentation.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    import torchvision.models as models
except ImportError:
    models = None


class SegFormerLight(nn.Module):
    """
    Contemporary light-weight multi-scale vision transformer / convolutional semantic segmenter.
    Extracts multi-scale hierarchical feature maps and projects them into a unified segmentation logit map.
    """
    def __init__(self, num_classes: int = 1, pretrained: bool = True):
        super().__init__()
        if models is None:
            raise ImportError("torchvision is required to instantiate SegFormerLight.")

        weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
        self.backbone = models.efficientnet_b0(weights=weights)

        # Feature projections for hierarchical stages
        self.proj1 = nn.Conv2d(24, 64, 1)
        self.proj2 = nn.Conv2d(40, 64, 1)
        self.proj3 = nn.Conv2d(112, 64, 1)
        self.proj4 = nn.Conv2d(320, 64, 1)

        self.linear_fuse = nn.Conv2d(64 * 4, 128, 1)
        self.classifier = nn.Conv2d(128, num_classes, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = []
        h = x
        for idx, layer in enumerate(self.backbone.features):
            h = layer(h)
            if idx in [1, 3, 5, 8]:
                features.append(h)

        f1, f2, f3, f4 = features
        out_size = (64, 64)

        p1 = F.interpolate(self.proj1(f1), size=out_size, mode='bilinear', align_corners=False)
        p2 = F.interpolate(self.proj2(f2), size=out_size, mode='bilinear', align_corners=False)
        p3 = F.interpolate(self.proj3(f3), size=out_size, mode='bilinear', align_corners=False)
        p4 = F.interpolate(self.proj4(f4), size=out_size, mode='bilinear', align_corners=False)

        fuse = self.linear_fuse(torch.cat([p1, p2, p3, p4], dim=1))
        logits = self.classifier(F.relu(fuse))
        return F.interpolate(logits, size=(256, 256), mode='bilinear', align_corners=False)
