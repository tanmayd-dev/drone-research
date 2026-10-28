"""
Otsu's Adaptive Thresholding and Connected-Component POI Centroid Extraction.
Transforms continuous reconstruction error maps into discrete Points of Interest (POIs).
"""

from typing import List, Tuple, Dict, Any
import numpy as np


def compute_reconstruction_error(original: np.ndarray, reconstructed: np.ndarray) -> np.ndarray:
    """
    Computes per-pixel Mean Squared Error (MSE) between original image and VQ-VAE reconstruction.
    Both images should be shaped [H, W, 3] with values in [0, 1] or [0, 255].
    """
    orig = original.astype(np.float32)
    recon = reconstructed.astype(np.float32)

    if orig.max() > 1.0:
        orig = orig / 255.0
    if recon.max() > 1.0:
        recon = recon / 255.0

    # Pixel-wise MSE across color channels
    err_map = np.mean((orig - recon) ** 2, axis=-1)
    return err_map


def otsu_threshold(error_map: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Computes Otsu's optimal binarization threshold maximizing between-class variance.
    Returns: (binarized_mask [H, W] uint8, optimal_threshold float in [0, 255])
    """
    # Normalize error to uint8 range [0, 255]
    min_val, max_val = error_map.min(), error_map.max()
    if max_val > min_val:
        norm_err = ((error_map - min_val) / (max_val - min_val) * 255.0).astype(np.uint8)
    else:
        norm_err = np.zeros_like(error_map, dtype=np.uint8)

    # Compute 256-bin histogram
    hist, _ = np.histogram(norm_err, bins=256, range=(0, 256))
    total_pixels = norm_err.size

    current_max = 0.0
    threshold = 0
    sum_total = np.dot(np.arange(256), hist)
    sum_b = 0.0
    w_b = 0

    for t in range(256):
        w_b += hist[t]
        if w_b == 0:
            continue
        w_f = total_pixels - w_b
        if w_f == 0:
            break

        sum_b += t * hist[t]
        m_b = sum_b / w_b
        m_f = (sum_total - sum_b) / w_f

        # Between-class variance
        between_var = w_b * w_f * ((m_b - m_f) ** 2)
        if between_var > current_max:
            current_max = between_var
            threshold = t

    binarized = (norm_err >= threshold).astype(np.uint8)
    return binarized, float(threshold)


def extract_poi_centroids(
    binary_mask: np.ndarray,
    min_area: int = 5,
    max_area: int = 5000,
    offset_x: float = 0.0,
    offset_y: float = 0.0
) -> List[Dict[str, Any]]:
    """
    Extracts connected components from binary mask and returns centroid coordinates as POIs.
    Uses pure NumPy BFS/DFS connected components so OpenCV is optional.
    """
    h, w = binary_mask.shape
    visited = np.zeros((h, w), dtype=bool)
    pois = []

    # 8-connectivity neighborhood
    neighbors = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for y in range(h):
        for x in range(w):
            if binary_mask[y, x] and not visited[y, x]:
                # BFS to collect connected component
                queue = [(y, x)]
                visited[y, x] = True
                comp_pixels = []

                while queue:
                    cy, cx = queue.pop(0)
                    comp_pixels.append((cy, cx))

                    for dy, dx in neighbors:
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w:
                            if binary_mask[ny, nx] and not visited[ny, nx]:
                                visited[ny, nx] = True
                                queue.append((ny, nx))

                area = len(comp_pixels)
                if min_area <= area <= max_area:
                    # Centroid calculation
                    avg_y = sum(p[0] for p in comp_pixels) / area
                    avg_x = sum(p[1] for p in comp_pixels) / area
                    pois.append({
                        "x": round(float(avg_x + offset_x), 2),
                        "y": round(float(avg_y + offset_y), 2),
                        "area": area
                    })

    return pois
