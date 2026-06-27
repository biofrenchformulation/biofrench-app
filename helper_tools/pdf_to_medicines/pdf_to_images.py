#!/usr/bin/env python3
"""
PDF to Images Extractor (Step 1 of 2)

Extracts images from PDF without processing names.
Each page becomes one JPG image in output/images/ with sequential naming.

Usage:
    python pdf_to_images.py <pdf_path> [--output-dir <dir>] [--dpi <n>]

Example:
    python pdf_to_images.py ../MEDICINES.pdf --output-dir output --dpi 200

Output:
    - output/images/med001.jpg, med002.jpg, med003.jpg, etc.
"""

import argparse
import sys
from pathlib import Path
from typing import Tuple

try:
    import pypdfium2 as pdfium
except ImportError:
    print("Error: pypdfium2 is required. Install it with: pip install pypdfium2")
    sys.exit(1)

try:
    from PIL import Image, ImageChops
except ImportError:
    print("Error: Pillow is required. Install it with: pip install Pillow")
    sys.exit(1)


class PDFToImagesExtractor:
    """Extracts images from PDF, one per page, with sequential naming."""

    def __init__(self, pdf_path: str, output_dir: str = "output", dpi: int = 200, crop: bool = True):
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / "images"
        self.dpi = dpi
        self.crop = crop

        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def extract(self, start_page: int = 1, end_page=None) -> Tuple[int, int]:
        """Render pages and save as images with sequential numbering."""
        pdf = pdfium.PdfDocument(str(self.pdf_path))
        total_pages = len(pdf)

        start_idx = max(0, start_page - 1)
        end_idx = total_pages if end_page is None else min(end_page, total_pages)

        print(f"Processing PDF: {self.pdf_path.name}")
        print(f"Total pages: {total_pages}  |  Processing pages {start_idx + 1}-{end_idx}")
        print(f"DPI: {self.dpi}  |  Crop: {'on' if self.crop else 'off'}\n")

        image_count = 0
        for page_idx in range(start_idx, end_idx):
            try:
                page = pdf[page_idx]
                pil_image = self._render_page(page)

                if self.crop:
                    pil_image = self._crop_product(pil_image)

                # Sequential naming: med001.jpg, med002.jpg, etc.
                image_count += 1
                image_name = f"med{image_count:03d}.jpg"
                image_path = self.images_dir / image_name

                pil_image.save(image_path, "JPEG", quality=95)
                print(f"Page {page_idx + 1}/{end_idx}: Saved {image_name}")

            except Exception as e:
                print(f"Page {page_idx + 1}/{end_idx}: SKIPPED ({str(e)[:60]})")

        pdf.close()

        print(f"\n{'='*60}")
        print(f"Extraction Summary:")
        print(f"  Total images extracted: {image_count}")
        print(f"  Location: {self.images_dir}")
        print(f"{'='*60}")

        return image_count, total_pages

    def _render_page(self, page) -> Image.Image:
        """Render a single PDF page to a PIL image at the configured DPI."""
        scale = self.dpi / 72.0
        bitmap = page.render(scale=scale)
        return bitmap.to_pil().convert("RGB")

    def _crop_product(self, img: Image.Image) -> Image.Image:
        """Crop away uniform white margins around the product image."""
        try:
            bg = Image.new("RGB", img.size, (255, 255, 255))
            diff = ImageChops.difference(img, bg)
            bbox = diff.getbbox()
            if bbox:
                pad = 4
                left = max(0, bbox[0] - pad)
                top = max(0, bbox[1] - pad)
                right = min(img.width, bbox[2] + pad)
                bottom = min(img.height, bbox[3] + pad)
                return img.crop((left, top, right, bottom))
        except Exception:
            pass
        return img


def main():
    parser = argparse.ArgumentParser(description="Extract images from PDF (Step 1)")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output-dir", default="output", help="Output directory for images (default: output)")
    parser.add_argument("--dpi", type=int, default=200, help="DPI for rendering (default: 200)")
    parser.add_argument("--start-page", type=int, default=1, help="Start page (default: 1)")
    parser.add_argument("--end-page", type=int, default=None, help="End page (default: all)")
    parser.add_argument("--no-crop", action="store_true", help="Skip cropping images")

    args = parser.parse_args()

    try:
        extractor = PDFToImagesExtractor(
            pdf_path=args.pdf_path,
            output_dir=args.output_dir,
            dpi=args.dpi,
            crop=not args.no_crop
        )
        image_count, total_pages = extractor.extract(
            start_page=args.start_page,
            end_page=args.end_page
        )
        print(f"\n✓ Step 1 complete: {image_count} images extracted")
        print(f"Next: Run 'python images_to_json.py' to extract names and create JSON")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
