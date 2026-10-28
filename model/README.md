# Deep Learning Vision Pipeline: Anomaly Detection & POI Extraction

This directory contains the deep learning models and inference pipeline for detecting damaged tree canopies (Points of Interest / POIs) from aerial drone images.

---

## Architecture Overview

```
Aerial Drone Image Patch [3 x 256 x 256]
                 │
                 ▼
     ┌───────────────────────┐
     │   ResNet34 Backbone   │ (Image Encoder with Squeeze-and-Excitation)
     └───────────┬───────────┘
                 ▼ Latent Feature Map [512 x 8 x 8]
     ┌───────────────────────┐
     │   Vector Quantizer    │ (Discrete Codebook: 256 Embeddings x 512 Dim)
     └───────────┬───────────┘
                 ▼ Quantized Latents [512 x 8 x 8]
     ┌───────────────────────┐
     │    VQ-VAE Decoder     │ (Transposed Convolutions + SE Attention)
     └───────────┬───────────┘
                 ▼ Reconstructed Patch [3 x 256 x 256]
     ┌───────────────────────┐
     │ Mean Squared Error    │ (Pixel-wise MSE vs. Original Input)
     └───────────┬───────────┘
                 ▼ Anomaly Error Heatmap
     ┌───────────────────────┐
     │   Otsu Binarization   │ (Dynamic Between-Class Variance Maximization)
     └───────────┬───────────┘
                 ▼ Binary Damaged Canopy Mask
     ┌───────────────────────┐
     │ Connected Components  │ (Centroid Extraction: POIs)
     └───────────────────────┘
```

### Key Technical Innovations
1. **Self-Supervised Anomaly Reconstruction:** Unlike object detection models (e.g., YOLO) that rely on bounding box templates and fail on unseen diseases, VQ-VAE learns the distribution of *healthy* tree foliage. Damaged foliage or insect infestations (such as Red Turpentine Beetles) deviate sharply from codebook priors, resulting in elevated reconstruction errors.
2. **Discrete Codebook vs. Continuous Latents:** The Vector Quantizer replaces continuous Gaussian priors with 256 discrete vectors of 512 dimensions, effectively preventing posterior collapse.
3. **Lighting-Invariant Otsu Binarization:** Rather than applying fixed global thresholds that vary under changing sunlight and shadow, Otsu's adaptive thresholding selects the threshold $T^*$ that maximizes between-class variance dynamically.

---

## Files

* `train-model.ipynb`: Complete Jupyter training notebook containing loss formulations (Masked MSE Loss + SSIM), data augmentation, and training loop.
* `vqvae.py`: Modular PyTorch implementations of `SEBlock`, `VectorQuantizer`, `VQVAEDecoder`, and `VQVAE`.
* `segformer.py`: Multi-scale transformer semantic segmentation backbone (`SegFormerLight`).
* `otsu_detector.py`: Pure NumPy Otsu binarization and connected-component centroid extractor.
* `inference.py`: Standalone CLI pipeline to slice full aerial field images, run reconstruction, and generate `detected_pois.json`.
* `weights/`: Directory designated for PyTorch model weights (`vqvae_upgraded_model.pth`).

---

## Running Inference

To run the POI extraction pipeline on an aerial image:

```bash
python -m model.inference --image "web/public/field_sample.jpg" --output "detected_pois.json"
```
