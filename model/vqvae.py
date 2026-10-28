"""
Vector Quantized Variational Autoencoder (VQ-VAE) with Squeeze-and-Excitation (SE) blocks.
Learns discrete latent representations of healthy agricultural canopy to isolate damage anomalies.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
try:
    import torchvision.models as models
except ImportError:
    models = None


class SEBlock(nn.Module):
    """
    Squeeze-and-Excitation block for channel-wise attention mapping.
    Selectively emphasizes informative features and suppresses uninformative canopy variations.
    """
    def __init__(self, channel: int, reduction: int = 16):
        super().__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(channel, max(1, channel // reduction), bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(max(1, channel // reduction), channel, bias=False),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, c, _, _ = x.size()
        y = self.avg_pool(x).view(b, c)
        y = self.fc(y).view(b, c, 1, 1)
        return x * y.expand_as(x)


class VectorQuantizer(nn.Module):
    """
    Discrete Vector Quantizer codebook layer for VQ-VAE.
    Quantizes continuous latent embeddings into discrete codebook indices to prevent posterior collapse.
    """
    def __init__(self, num_embeddings: int = 256, embedding_dim: int = 512, commitment_cost: float = 0.25):
        super().__init__()
        self.num_embeddings = num_embeddings
        self.embedding_dim = embedding_dim
        self.commitment_cost = commitment_cost

        self.embedding = nn.Embedding(self.num_embeddings, self.embedding_dim)
        self.embedding.weight.data.uniform_(-1.0 / self.num_embeddings, 1.0 / self.num_embeddings)

    def forward(self, inputs: torch.Tensor):
        # [B, C, H, W] -> [B, H, W, C]
        inputs = inputs.permute(0, 2, 3, 1).contiguous()
        input_shape = inputs.shape

        flat_input = inputs.view(-1, self.embedding_dim)

        # Compute L2 distances between latent vectors and codebook vectors
        distances = (
            torch.sum(flat_input ** 2, dim=1, keepdim=True)
            + torch.sum(self.embedding.weight ** 2, dim=1)
            - 2 * torch.matmul(flat_input, self.embedding.weight.t())
        )

        encoding_indices = torch.argmin(distances, dim=1).unsqueeze(1)
        quantized = self.embedding(encoding_indices).view(input_shape)

        # VQ loss = codebook loss + commitment loss
        e_latent_loss = F.mse_loss(quantized.detach(), inputs)
        q_latent_loss = F.mse_loss(quantized, inputs.detach())
        loss = q_latent_loss + self.commitment_cost * e_latent_loss

        # Straight-through gradient estimator
        quantized = inputs + (quantized - inputs).detach()

        return quantized.permute(0, 3, 1, 2).contiguous(), loss


class VQVAEDecoder(nn.Module):
    """
    Transposed convolution decoder with Squeeze-and-Excitation channel attention.
    Reconstructs 3x256x256 canopy images from discrete codebook embeddings.
    """
    def __init__(self, embedding_dim: int = 512):
        super().__init__()
        self.deconv1 = nn.ConvTranspose2d(embedding_dim, 256, kernel_size=3, stride=2, padding=1, output_padding=1)
        self.relu1 = nn.ReLU()
        self.se1 = SEBlock(256)

        self.deconv2 = nn.ConvTranspose2d(256, 128, kernel_size=3, stride=2, padding=1, output_padding=1)
        self.relu2 = nn.ReLU()
        self.se2 = SEBlock(128)

        self.deconv3 = nn.ConvTranspose2d(128, 64, kernel_size=3, stride=2, padding=1, output_padding=1)
        self.relu3 = nn.ReLU()
        self.se3 = SEBlock(64)

        self.deconv4 = nn.ConvTranspose2d(64, 64, kernel_size=3, stride=2, padding=1, output_padding=1)
        self.relu4 = nn.ReLU()
        self.se4 = SEBlock(64)

        self.deconv5 = nn.ConvTranspose2d(64, 32, kernel_size=3, stride=2, padding=1, output_padding=1)
        self.relu5 = nn.ReLU()

        self.final_conv = nn.Conv2d(32, 3, kernel_size=3, stride=1, padding=1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, quantized: torch.Tensor) -> torch.Tensor:
        x = self.relu1(self.deconv1(quantized))
        x = self.se1(x)
        x = self.relu2(self.deconv2(x))
        x = self.se2(x)
        x = self.relu3(self.deconv3(x))
        x = self.se3(x)
        x = self.relu4(self.deconv4(x))
        x = self.se4(x)
        x = self.relu5(self.deconv5(x))
        x = self.final_conv(x)
        return self.sigmoid(x)


class VQVAE(nn.Module):
    """
    Upgraded VQ-VAE model without bypass skip connections for robust anomaly detection.
    Enforces that anomalies (diseased canopies) fail reconstruction, producing sharp error maps.
    """
    def __init__(self, num_embeddings: int = 256, embedding_dim: int = 512, pretrained_backbone: bool = True):
        super().__init__()
        if models is None:
            raise ImportError("torchvision is required to instantiate VQVAE.")

        weights = models.ResNet34_Weights.DEFAULT if pretrained_backbone else None
        resnet = models.resnet34(weights=weights)

        self.conv1 = resnet.conv1
        self.bn1 = resnet.bn1
        self.relu = resnet.relu
        self.maxpool = resnet.maxpool

        self.layer1 = resnet.layer1
        self.se1 = SEBlock(64)
        self.layer2 = resnet.layer2
        self.se2 = SEBlock(128)
        self.layer3 = resnet.layer3
        self.se3 = SEBlock(256)
        self.layer4 = resnet.layer4
        self.se4 = SEBlock(512)

        self.norm = nn.BatchNorm2d(512)
        self.pre_vq_conv = nn.Conv2d(512, embedding_dim, kernel_size=1, stride=1)
        self.vq = VectorQuantizer(num_embeddings, embedding_dim)
        self.decoder = VQVAEDecoder(embedding_dim)

    def forward(self, x: torch.Tensor):
        h = self.conv1(x)
        h = self.bn1(h)
        h = self.relu(h)
        h = self.maxpool(h)

        f1 = self.se1(self.layer1(h))
        f2 = self.se2(self.layer2(f1))
        f3 = self.se3(self.layer3(f2))
        f4 = self.se4(self.layer4(f3))

        encoded = self.norm(f4)
        pre_vq = self.pre_vq_conv(encoded)
        quantized, vq_loss = self.vq(pre_vq)
        reconstruction = self.decoder(quantized)
        return reconstruction, vq_loss
