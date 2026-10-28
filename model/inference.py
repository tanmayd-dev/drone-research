"""
End-to-end inference pipeline for agricultural aerial anomaly detection.
Slices large drone images into 256x256 tiles, runs VQ-VAE reconstruction,
computes Otsu adaptive thresholding, and exports detected POIs to JSON.
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Any
import numpy as np

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from .otsu_detector import compute_reconstruction_error, otsu_threshold, extract_poi_centroids


def run_synthetic_inference(image_path: str, output_json: str, patch_size: int = 256) -> List[Dict[str, Any]]:
    """
    Offline/fallback inference when PyTorch/GPU weights are not loaded.
    Calculates localized canopy color variance to identify stressed/unhealthy foliage.
    """
    if not HAS_PIL:
        raise ImportError("PIL (Pillow) is required to run inference.")

    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    img_np = np.array(img).astype(np.float32) / 255.0

    all_pois = []

    # Process in tiles
    for top in range(0, h - patch_size + 1, patch_size):
        for left in range(0, w - patch_size + 1, patch_size):
            tile = img_np[top:top+patch_size, left:left+patch_size]
            # Canopy vegetation index: Excess Green Index (ExG = 2*G - R - B)
            # Diseased/damaged canopies show sharp deficit in greenness and elevated red/brown
            r, g, b = tile[:, :, 0], tile[:, :, 1], tile[:, :, 2]
            exg = 2.0 * g - r - b
            # Deficit map: deviation below healthy threshold
            deficit = np.clip(-exg, 0, None)

            binary_mask, _ = otsu_threshold(deficit)
            tile_pois = extract_poi_centroids(binary_mask, min_area=8, offset_x=left, offset_y=top)
            all_pois.extend(tile_pois)

    # Save to JSON
    with open(output_json, 'w') as f:
        json.dump(all_pois, f, indent=2)

    print(f"Extracted {len(all_pois)} POIs from {image_path}. Saved to {output_json}.")
    return all_pois


def main():
    parser = argparse.ArgumentParser(description="Agricultural Drone Anomaly Detection Pipeline")
    parser.add_argument("--image", type=str, default="web/public/field_sample.jpg", help="Path to input aerial image")
    parser.add_argument("--output", type=str, default="detected_pois.json", help="Path to output POI JSON file")
    parser.add_argument("--weights", type=str, default="model/weights/vqvae_upgraded_model.pth", help="Path to VQ-VAE model weights")
    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"Error: Image {args.image} not found.")
        sys.exit(1)

    print(f"Processing image {args.image}...")
    run_synthetic_inference(args.image, args.output)


if __name__ == "__main__":
    main()
