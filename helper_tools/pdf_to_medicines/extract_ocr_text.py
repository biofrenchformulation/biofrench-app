#!/usr/bin/env python3
"""
Extract OCR Text from Images

Extracts ALL text from pharmacy product images using optical character recognition (OCR).
Preprocesses images to improve OCR accuracy (denoise, threshold, CLAHE, resize).
Original images are NEVER modified - all preprocessing is in-memory only.

Usage:
    python extract_ocr_text.py --input-dir output/images --output-dir output --threads 8
    python extract_ocr_text.py --input-dir output/images --limit 10  # Test with 10 images
    python extract_ocr_text.py --input-dir output/images --image med001.jpg  # Single image
    python extract_ocr_text.py --input-dir output/images --save-preprocessed preprocessed_images

Output:
    - output/images_text_all.json: {image_name: ocr_text}
    - output/extraction_log.json: Processing log
"""

import json
import argparse
import threading
from pathlib import Path
from typing import Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Error: Pillow not installed. Install with: pip install pillow")

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Warning: pytesseract not installed. Install with: pip install pytesseract")

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("Warning: opencv-python not installed. Install with: pip install opencv-python numpy")


class OCRTextExtractor:
    """Extract all text from images using OCR with preprocessing."""

    def __init__(self, input_dir: str = "output/images", output_dir: str = "output",
                 use_ocr: bool = True, num_threads: int = 4,
                 output_json_filename: str = "images_text_all.json",
                 save_preprocessed: Optional[str] = None):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.use_ocr = use_ocr and OCR_AVAILABLE
        self.num_threads = max(1, num_threads)
        self.output_json_filename = output_json_filename
        self.save_preprocessed = Path(save_preprocessed) if save_preprocessed else None
        self.text_data: Dict[str, str] = {}
        self.extraction_log: Dict[str, Dict] = {}
        self._lock = threading.Lock()

        if self.save_preprocessed:
            self.save_preprocessed.mkdir(parents=True, exist_ok=True)
            print(f"[OK] Preprocessed images will be saved to: {self.save_preprocessed}")
            print(f"[OK] Original images remain unchanged in: {self.input_dir}\n")

        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {self.input_dir}")

        self.output_dir.mkdir(parents=True, exist_ok=True)

        if use_ocr and not OCR_AVAILABLE:
            print("Warning: pytesseract not installed — no text extraction possible.")
            print("         Install with: pip install pytesseract  (and install Tesseract-OCR)")

    def _preprocess_image(self, image: Image.Image, image_name: Optional[str] = None) -> Image.Image:
        """Preprocess image for improved OCR accuracy (in-memory, non-destructive).
        
        Enhanced pipeline for BRAND NAME CLARITY:
        - Grayscale conversion
        - Bilateral filtering: removes noise while preserving sharp edges
        - Denoising: removes fine noise
        - Morphological operations: enhances text connectivity
        - Multi-pass thresholding: better text/background separation
        - Edge enhancement: makes brand names pop
        - CLAHE: boosts contrast
        - Resize: upscale to optimal OCR size
        """
        if not CV2_AVAILABLE:
            return image.convert('L')

        # Convert PIL to OpenCV (in-memory copy)
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # 1. Grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        # 2. BILATERAL FILTERING for edge preservation (new - improves brand clarity)
        # Reduces noise while keeping edges sharp - critical for text clarity
        bilateral = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

        # 3. Denoise with optimized parameters
        # Less aggressive than before to preserve detail after bilateral filter
        denoised = cv2.fastNlMeansDenoising(bilateral, h=8, templateWindowSize=9, searchWindowSize=25)

        # 4. Morphological operations for text enhancement
        # First pass: close small gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morph = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
        
        # Second pass: open to remove small noise
        kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel_open)

        # 5. Multi-pass adaptive thresholding (improved brand clarity)
        # First: Gaussian adaptive threshold for varied lighting
        thresh1 = cv2.adaptiveThreshold(morph, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        
        # Second: Apply Otsu's on top for additional text enhancement
        _, thresh_otsu = cv2.threshold(thresh1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        thresh = cv2.bitwise_or(thresh1, thresh_otsu)

        # 6. EDGE ENHANCEMENT for sharper brand names (optimized)
        # Subtle unsharp masking - enhances edges without creating artifacts
        gaussian = cv2.GaussianBlur(thresh, (3, 3), 0)
        edges = cv2.subtract(thresh, gaussian)
        enhanced_edges = cv2.addWeighted(thresh, 1.1, edges, 0.4, 0)  # Less aggressive weighting

        # 7. Morphological enhancement - strengthen text strokes
        dilation_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        dilated = cv2.dilate(enhanced_edges, dilation_kernel, iterations=1)

        # 8. CLAHE contrast enhancement with optimized settings
        # Balanced: not too aggressive to avoid artifact amplification
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(12, 12))
        enhanced = clahe.apply(dilated)

        # 9. Resize if too small (Tesseract sweet spot: 400px minimum)
        height, width = enhanced.shape
        target_min_px = 400
        if height < target_min_px or width < target_min_px:
            scale = max(target_min_px / height, target_min_px / width)
            new_size = (int(width * scale), int(height * scale))
            # INTER_LANCZOS4 for highest quality
            enhanced = cv2.resize(enhanced, new_size, interpolation=cv2.INTER_LANCZOS4)

        # Convert back to PIL
        result = Image.fromarray(enhanced)

        # Optionally save for debugging
        if self.save_preprocessed and image_name:
            output_path = self.save_preprocessed / image_name
            result.save(output_path)

        return result

    def _extract_text_from_image(self, idx: int, image_path: Path) -> Tuple[Optional[str], Dict, str]:
        """Extract text from single image."""
        log_entry = {
            "index": idx,
            "imageName": image_path.name,
            "status": "pending",
            "textLength": 0,
            "error": None,
        }

        try:
            if not self.use_ocr:
                raise RuntimeError("OCR not available")

            # Load and preprocess
            pil_image = Image.open(image_path).convert("RGB")
            pil_image = self._preprocess_image(pil_image, image_path.name)

            # Extract text with enhanced Tesseract config for pharmaceutical product images
            # PSM 6: Assume single column of uniform text (works better for structured product labels)
            # PSM 3: Fully automatic (fallback if 6 doesn't work well)
            # --oem 1: Legacy + neural net combined (usually better OCR accuracy)
            # -c tessedit_cfg_values: Preserve interword spaces, improve digit recognition
            
            # PHARMACY-OPTIMIZED config (PSM 6 for structured pharmaceutical labels):
            custom_config = (
                r'--psm 6 '  # Structured text (product labels are usually structured)
                r'--oem 1 '  # Legacy + neural
                r'-c preserve_interword_spaces=1 '
                r'-c classify_bln_numeric_mode=1'  # Better digit/number recognition
            )
            all_text = pytesseract.image_to_string(pil_image, lang='eng', config=custom_config)
            all_text = all_text.strip()

            if not all_text:
                log_entry["status"] = "no_text"
                return "", log_entry, f"{idx}: {image_path.name} - NO TEXT FOUND"

            log_entry["status"] = "success"
            log_entry["textLength"] = len(all_text)
            return all_text, log_entry, f"{idx}: {image_path.name} - {len(all_text)} chars"

        except Exception as e:
            log_entry["status"] = "failed"
            log_entry["error"] = str(e)
            return None, log_entry, f"{idx}: {image_path.name} - ERROR: {str(e)[:60]}"

    def process(self, single_image: Optional[str] = None, limit: Optional[int] = None) -> int:
        """Process images using thread pool."""
        images = sorted(self.input_dir.glob("*.jpg")) + sorted(self.input_dir.glob("*.png"))

        if not images:
            print(f"No images found in {self.input_dir}")
            return 0

        # Filter to single image if specified
        if single_image:
            images = [img for img in images if img.name == single_image]
            if not images:
                print(f"Image not found: {single_image}")
                return 0

        # Limit if specified
        if limit and limit > 0:
            images = images[:limit]
            print(f"[LIMIT] Processing limited to first {limit} images")

        print(f"Processing {len(images)} image(s)")
        print(f"OCR: {'ON' if self.use_ocr else 'OFF'}")
        print(f"Threads: {self.num_threads}\n")

        if not self.use_ocr:
            print("[WARNING] OCR is disabled.")
            return 0

        # Process with thread pool
        successful_count = 0
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = {
                executor.submit(self._extract_text_from_image, idx, image_path): image_path
                for idx, image_path in enumerate(images, 1)
            }

            for future in as_completed(futures):
                try:
                    all_text, log_entry, status_msg = future.result()
                    with self._lock:
                        image_name = log_entry["imageName"]
                        self.extraction_log[image_name] = log_entry

                        if all_text is not None and log_entry["status"] == "success":
                            self.text_data[image_name] = all_text
                            successful_count += 1

                        print(status_msg)

                except Exception as e:
                    print(f"Worker error: {e}")

        # Sort by index
        sorted_text_data = {}
        for log_entry in sorted(self.extraction_log.values(), key=lambda x: x["index"]):
            image_name = log_entry["imageName"]
            if image_name in self.text_data:
                sorted_text_data[image_name] = self.text_data[image_name]

        self.text_data = sorted_text_data

        print(f"\n{'='*60}")
        print(f"Extraction Summary:")
        print(f"  Total images: {len(images)}")
        print(f"  Successfully extracted: {successful_count}")
        print(f"  Failed/No text: {len(images) - successful_count}")
        print(f"{'='*60}\n")

        return successful_count

    def save_json(self) -> Path:
        """Save extracted text to JSON."""
        json_path = self.output_dir / self.output_json_filename
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.text_data, f, indent=2, ensure_ascii=False)
        return json_path

    def save_log(self) -> Path:
        """Save extraction log."""
        log_path = self.output_dir / "extraction_log.json"
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(self.extraction_log, f, indent=2, ensure_ascii=False)
        return log_path


def main():
    parser = argparse.ArgumentParser(
        description="Extract OCR text from images with preprocessing"
    )
    parser.add_argument("--input-dir", default="output/images",
                        help="Input images directory (default: output/images)")
    parser.add_argument("--output-dir", default="output",
                        help="Output directory for JSON files (default: output)")
    parser.add_argument("--threads", type=int, default=4,
                        help="Number of threads (default: 4)")
    parser.add_argument("--image", default=None,
                        help="Process single image only (e.g., med001.jpg)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit to first N images (e.g., 10 for testing)")
    parser.add_argument("--save-preprocessed", default=None,
                        help="Save preprocessed images to folder for debugging")
    parser.add_argument("--no-ocr", action="store_true",
                        help="Disable OCR (not recommended)")
    parser.add_argument("--output-json", default="images_text_all.json",
                        help="Output JSON filename (default: images_text_all.json)")

    args = parser.parse_args()

    extractor = OCRTextExtractor(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        use_ocr=not args.no_ocr,
        num_threads=args.threads,
        output_json_filename=args.output_json,
        save_preprocessed=args.save_preprocessed
    )

    successful = extractor.process(single_image=args.image, limit=args.limit)

    if successful > 0:
        json_path = extractor.save_json()
        log_path = extractor.save_log()
        print(f"✅ Saved: {json_path}")
        print(f"📋 Saved: {log_path}")


if __name__ == "__main__":
    main()
