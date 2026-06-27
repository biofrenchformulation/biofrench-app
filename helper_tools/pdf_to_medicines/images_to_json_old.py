#!/usr/bin/env python3
"""
Old Medicines JSON Extractor (Step 3)

Processes existing app medicine images, extracts brand names via OCR,
and creates old_medicines.json for comparison with new medicines.

Includes special handling for:
- Company/manufacturer name stripping
- Existing format normalization
- Delta comparison preparation

Usage:
    python images_to_json_old.py [--images-dir <dir>] [--output-dir <dir>] [--threads <n>]

Example:
    python images_to_json_old.py \
      --images-dir ../../app/src/main/assets/images \
      --output-dir output \
      --threads 8

Output:
    - output/old_medicines.json - Extracted medicines from app
    - output/extraction_successful.json - Log of successful extractions
    - output/extraction_failed.json - Log of failed/skipped images
    - output/validation_report.json - Quality validation report
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install it with: pip install Pillow")
    sys.exit(1)

# OCR is optional
try:
    import pytesseract
    _default_tess = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if Path(_default_tess).exists():
        pytesseract.pytesseract.tesseract_cmd = _default_tess
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class OldMedicinesExtractor:
    """Extract brand names from existing app images with special old-medicine handling."""

    # Company names to strip from beginning (specific to app's existing data)
    # Ordered by priority: specific prefixes first, ambiguous ones last
    COMPANY_PREFIXES = [
        "MANUFACTURED BY",
        "MADE BY",
        "PRODUCED BY",
        "ASVINS",
        "LIFECARE",
        "ASVINS LIFECARE",  # Lower priority
        "AKUMS",            # Lower priority
    ]
    
    # Medicine type suffixes to strip from old filenames (55 types from app)
    # Format in filenames: {brandName}-{TYPE}.ext
    MEDICINE_TYPE_SUFFIXES = [
        "TAB", "CAP", "PEL", "EFF", "LOZ", "JSYR", "SYR", "DSY", "ELX", "TNC",
        "INJ", "INF", "VIL", "AMP", "CRM", "GEL", "OIN", "OIL", "PST", "LIN",
        "BAL", "RUB", "DRP", "LIQ", "SOL", "LOT", "EMU", "WSH", "MWH", "GAR",
        "PWD", "GRN", "SUS", "SGC", "SPR", "FLM", "INH", "GUM", "SUP", "PES",
        "ENM", "BAS", "NSP", "EYE", "EYO", "EYG", "EAR", "PTH", "DEV", "TON",
        "SOP", "SAC", "CHR", "GHE", "KWA", "RAS"
    ]

    def __init__(self, images_dir: str, output_dir: str = "output", use_ocr: bool = True, num_threads: int = 4):
        self.images_dir = Path(images_dir)
        self.output_dir = Path(output_dir)
        self.use_ocr = use_ocr and OCR_AVAILABLE
        self.num_threads = max(1, num_threads)
        self.medicines = []
        self.successful_log = []
        self.failed_log = []
        self._lock = threading.Lock()

        if not self.images_dir.exists():
            raise FileNotFoundError(f"Images directory not found: {self.images_dir}")

        self.output_dir.mkdir(parents=True, exist_ok=True)

        if use_ocr and not OCR_AVAILABLE:
            print("Warning: pytesseract not installed — brand names will be image filenames.")

    def _strip_type_suffix(self, filename_stem: str) -> str:
        """Strip medicine type suffix from filename (e.g., '27 AS-CAP' -> '27 AS')."""
        name = filename_stem
        
        # Try to strip known type suffixes from end
        for suffix in self.MEDICINE_TYPE_SUFFIXES:
            if name.upper().endswith("-" + suffix.upper()):
                name = name[:-len(suffix)-1].strip()
                if name:
                    return name
        
        return filename_stem

    def _strip_company_prefix(self, brand_name: str) -> str:
        """Strip company/manufacturer names from beginning of brand name (iteratively)."""
        name = brand_name.strip()
        
        # Keep stripping prefixes until none found at beginning
        changed = True
        while changed:
            changed = False
            for prefix in self.COMPANY_PREFIXES:
                if name.upper().startswith(prefix.upper()):
                    name = name[len(prefix):].strip()
                    # Also strip any leading hyphens, spaces, or special chars
                    name = re.sub(r"^[\s\-_]+", "", name)
                    changed = True
                    break  # Restart from top of prefix list
        
        return name if name else brand_name

    def _clean_old_brand_name(self, brand_name: str) -> str:
        """Clean and normalize brand name from existing app format."""
        # Strip company prefixes
        clean_name = self._strip_company_prefix(brand_name)
        
        # Remove extra spaces
        clean_name = re.sub(r"\s+", " ", clean_name).strip()
        
        # Normalize hyphens
        clean_name = re.sub(r"\s*\-\s*", "-", clean_name)
        clean_name = re.sub(r"\-\-+", "-", clean_name)
        
        return clean_name if clean_name else brand_name

    def _process_single_image(self, idx: int, image_path: Path):
        """Process a single old medicine image."""
        log_entry = {
            "index": idx,
            "imageName": image_path.name,
            "brandName": None,
            "medicineId": None,
        }
        
        try:
            # Use filename as primary source: format is {brandName}-{TYPE}.ext
            filename_stem = image_path.stem
            
            # Strip type suffix from filename (e.g., '27 AS-CAP' -> '27 AS')
            brand_name = self._strip_type_suffix(filename_stem)
            
            # Strip company prefixes (e.g., 'ASVINS LIFECARE ASPIVERT' -> 'ASPIVERT')
            cleaned_brand = self._clean_old_brand_name(brand_name)
            
            # Use filename as ID (remove extension)
            medicine_id = filename_stem
            
            medicine_dict = {
                "id": medicine_id,
                "brandName": cleaned_brand,
                "isActive": True,
                "source": "Existing App",
                "preferredAffiliate": False,
            }
            
            log_entry["brandName"] = cleaned_brand
            log_entry["medicineId"] = medicine_id
            
            return medicine_dict, log_entry, f"{idx}: {medicine_id} -> '{cleaned_brand}'", None
        
        except Exception as e:
            log_entry["error"] = str(e)
            return None, log_entry, f"{idx}: SKIPPED ({str(e)[:60]})", e

    def process(self, max_images: int = None):
        """Process all images in input directory."""
        images = sorted(self.images_dir.glob("*.jpg")) + sorted(self.images_dir.glob("*.png"))
        
        if not images:
            print(f"No images found in {self.images_dir}")
            return 0
        
        if max_images and max_images > 0:
            images = images[:max_images]
        
        print(f"Processing {len(images)} old medicine image(s) from: {self.images_dir}")
        print(f"Method: Filename extraction + type suffix stripping")
        print(f"Threads: {self.num_threads}\n")
        
        # Process images using thread pool
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = {
                executor.submit(self._process_single_image, idx, image_path): (idx, image_path)
                for idx, image_path in enumerate(images, 1)
            }
            
            for future in as_completed(futures):
                try:
                    medicine_dict, log_entry, status_msg, error = future.result()
                    
                    with self._lock:
                        if medicine_dict:
                            self.medicines.append(medicine_dict)
                            self.successful_log.append(log_entry)
                        else:
                            self.failed_log.append(log_entry)
                        
                        print(f"{status_msg}")
                except Exception as e:
                    print(f"Worker error: {e}")
        
        # Sort by index to maintain order
        idx_to_medicine = {}
        idx_to_successful_log = {}
        idx_to_failed_log = {}
        
        for i, log_entry in enumerate(self.successful_log):
            idx_to_medicine[log_entry["index"]] = self.medicines[len(idx_to_medicine)]
            idx_to_successful_log[log_entry["index"]] = log_entry
        
        for log_entry in self.failed_log:
            idx_to_failed_log[log_entry["index"]] = log_entry
        
        # Rebuild in original order
        self.medicines.clear()
        self.successful_log.clear()
        self.failed_log.clear()
        
        for idx in sorted(idx_to_medicine.keys()):
            self.medicines.append(idx_to_medicine[idx])
            self.successful_log.append(idx_to_successful_log[idx])
        
        for idx in sorted(idx_to_failed_log.keys()):
            self.failed_log.append(idx_to_failed_log[idx])
        
        print(f"\n{'='*60}")
        print(f"Processing Summary:")
        print(f"  Total medicines: {len(self.medicines)}")
        print(f"{'='*60}\n")
        
        # Validate and generate report
        self._validate_and_report()
        
        return len(self.medicines)

    def _extract_brand_name(self, img: Image.Image) -> Optional[str]:
        """Extract brand name via OCR from top portion of image."""
        if not self.use_ocr:
            return None
        
        all_candidates = []
        
        for crop_ratio in (0.35, 0.50, 0.65):
            try:
                crop_height = int(img.height * crop_ratio)
                img_cropped = img.crop((0, 0, img.width, crop_height))
                data = pytesseract.image_to_data(img_cropped, output_type=pytesseract.Output.DICT)
            except Exception:
                continue
            
            lines = {}
            n = len(data["text"])
            for j in range(n):
                text = data["text"][j].strip()
                if not text:
                    continue
                try:
                    conf = int(float(data["conf"][j]))
                except (ValueError, TypeError):
                    conf = 50
                if conf < 45:
                    continue
                
                word = self._clean_word(text)
                if not word or len(word) < 2:
                    continue
                
                key = (data["block_num"][j], data["par_num"][j], data["line_num"][j])
                if key not in lines:
                    lines[key] = {"words": [], "max_h": 0, "conf": 0}
                lines[key]["words"].append(word)
                lines[key]["max_h"] = max(lines[key]["max_h"], data["height"][j])
                lines[key]["conf"] = max(lines[key]["conf"], conf)
            
            for line in lines.values():
                name = " ".join(line["words"]).strip()
                score = self._calculate_brand_score(name, line["max_h"], line["conf"])
                if score > 0:
                    score += (1.0 - crop_ratio) * 2.0
                    all_candidates.append((name, score))
        
        if not all_candidates:
            return None
        
        all_candidates.sort(key=lambda x: -x[1])
        result = self._normalize_name(all_candidates[0][0])
        return result if result else None

    def _calculate_brand_score(self, text: str, height: int, conf: int) -> float:
        """Score likelihood that text is a pharmaceutical brand name."""
        score = height * 0.15 + conf * 0.3
        
        if any(char.isdigit() for char in text):
            score += 15
        if "-" in text:
            score += 10
        
        if len(text) < 3 or len(text) > 50:
            score -= 10
        
        common_words = {"the", "and", "for", "this", "that", "page", "product"}
        if text.lower() in common_words:
            score -= 50
        
        if conf >= 85:
            score += 5
        elif conf >= 70:
            score += 3
        elif conf < 50:
            score -= 5
        
        return max(0.0, min(100.0, score))

    @staticmethod
    def _clean_word(text: str) -> str:
        """Remove punctuation/noise, keep letters, digits, and hyphens."""
        return re.sub(r"[^A-Za-z0-9\-]", "", text).strip()

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize whitespace and hyphen spacing."""
        name = re.sub(r"\s*\-\s*", "-", name)
        name = re.sub(r"\-\-+", "-", name)
        name = re.sub(r"\s+", " ", name).strip(" -")
        return name

    def _validate_and_report(self):
        """Validate old medicines (lighter validation than new medicines)."""
        issues = {
            "company_prefix_found": 0,
            "suspicious_names": [],
        }
        
        for med in self.medicines:
            brand = med["brandName"]
            
            # Check if company prefix is still present after cleaning
            if any(company in brand.upper() for company in self.COMPANY_PREFIXES):
                issues["company_prefix_found"] += 1
            
            # Check for suspicious patterns
            if len(brand) < 2:
                issues["suspicious_names"].append({"id": med["id"], "name": brand, "reason": "Too short"})
            elif len(brand) > 80:
                issues["suspicious_names"].append({"id": med["id"], "name": brand, "reason": "Too long"})
        
        print(f"\n{'='*60}")
        print("OLD MEDICINES VALIDATION REPORT")
        print(f"{'='*60}")
        print(f"Total medicines: {len(self.medicines)}")
        if issues["company_prefix_found"] > 0:
            print(f"⚠️  Company prefixes still detected: {issues['company_prefix_found']}")
        if issues["suspicious_names"]:
            print(f"⚠️  Suspicious names: {len(issues['suspicious_names'])}")
            for item in issues["suspicious_names"][:5]:
                print(f"   {item['id']}: '{item['name']}' ({item['reason']})")
        print(f"{'='*60}\n")

    def save_json(self) -> Path:
        """Save old medicines to old_medicines.json."""
        json_path = self.output_dir / "old_medicines.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.medicines, f, indent=4, ensure_ascii=False)
        return json_path

    def save_extraction_log(self) -> tuple:
        """Save extraction logs."""
        success_path = self.output_dir / "extraction_successful.json"
        failed_path = self.output_dir / "extraction_failed.json"
        
        with open(success_path, "w", encoding="utf-8") as f:
            json.dump(self.successful_log, f, indent=2, ensure_ascii=False)
        
        with open(failed_path, "w", encoding="utf-8") as f:
            json.dump(self.failed_log, f, indent=2, ensure_ascii=False)
        
        return success_path, failed_path


def main():
    parser = argparse.ArgumentParser(description="Extract old medicines from app assets (Step 3)")
    parser.add_argument("--images-dir", default="../../app/src/main/assets/images",
                       help="App images directory (default: ../../app/src/main/assets/images)")
    parser.add_argument("--output-dir", default="output",
                       help="Output directory (default: output)")
    parser.add_argument("--no-ocr", action="store_true",
                       help="Skip OCR and use filenames as brand names")
    parser.add_argument("--threads", type=int, default=4,
                       help="Number of threads for OCR (default: 4, max: 32)")
    parser.add_argument("--max-images", type=int, default=None,
                       help="Process only first N images (for testing)")
    
    args = parser.parse_args()
    
    if args.threads < 1 or args.threads > 32:
        print("Error: --threads must be between 1 and 32")
        return 1
    
    try:
        extractor = OldMedicinesExtractor(
            images_dir=args.images_dir,
            output_dir=args.output_dir,
            use_ocr=not args.no_ocr,
            num_threads=args.threads
        )
        count = extractor.process(max_images=args.max_images)
        json_path = extractor.save_json()
        success_log_path, failed_log_path = extractor.save_extraction_log()
        
        print(f"✅ Step 3 complete: {count} old medicines extracted")
        print(f"✓ Saved to: {json_path}")
        print(f"✓ Extraction logs:")
        print(f"  - Successful: {success_log_path}")
        print(f"  - Failed: {failed_log_path}\n")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
