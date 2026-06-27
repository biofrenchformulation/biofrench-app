#!/usr/bin/env python3
"""
Images to JSON Converter (Step 2 & 3)

Processes extracted images, extracts brand names via OCR,
and creates medicines.json for app import.

Uses multi-threading for faster parallel processing of images.

Usage:
    # Step 2: Extract new medicines from PDF
    python images_to_json.py --input-dir output/images --output-dir output --source "Asvins Lifecare Pvt Ltd" --threads 8
    
    # Step 3: Extract old medicines from app assets
    python images_to_json.py --input-dir ../../app/src/main/assets/images --output-dir output --output-json old_medicines.json --threads 8

Output:
    - medicines.json (or custom name) - JSON with all extracted medicines
    - extraction_successful.json - Log of successful extractions
    - extraction_failed.json - Log of failed/skipped images
    - validation_report.json - Quality validation report
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
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

import shutil


class ImagesToJsonConverter:
    """Processes images, extracts brand names, and generates JSON."""

    # Medicine type abbreviations for short, clean filenames
    TYPE_ABBREVIATIONS = {
        "Tablet": "TAB",
        "Tablets": "TAB",
        "Capsule": "CAP",
        "Capsules": "CAP",
        "Junior Syrup": "JSYR",
        "Syrup": "SYR",
        "Injection": "INJ",
        "Infusion": "INF",
        "Cream": "CRM",
        "Gel": "GEL",
        "Drops": "DRP",
        "Ointment": "OIN",
        "Powder": "PWD",
        "Suspension": "SUS",
        "Softgel": "SGC",
        "Softgels": "SGC",
        "Spray": "SPR",
        "Liquid": "LIQ",
        "Solution": "SOL",
        "Lotion": "LOT",
        "Shampoo": "SHP",
        "Tonic": "TON",
        "Device": "DEV",
        "Soap": "SOP",
        "Sachet": "SAC",
        "Oil": "OIL",
        "Patch": "PTH",
        "Suppository": "SUP",
        "Paste": "PST",
        "Liniment": "LIN",
        "Nasal Spray": "NSP",
        "Eye Drops": "EYE",
        "Ear Drops": "EAR",
        "Effervescent": "EFF",
        "Dry Syrup": "DSY",
        "Vial": "VIL",
        "Ampule": "AMP",
        "Lozenges": "LOZ",
        "Film": "FLM",
        "Balm": "BAL",
        "Inhaler": "INH",
        "Emulsion": "EMU",
        "Granules": "GRN",
        "Pessary": "PES",
        "Enema": "ENM",
        "Tincture": "TNC",
        "Elixir": "ELX",
        "Mouthwash": "MWH",
        "Gargle": "GAR",
        "Gummies": "GUM",
        "Wash": "WSH",
        "Rub": "RUB",
        "Pellets": "PEL",
        "Eye Ointment": "EYO",
        "Eye Gel": "EYG",
        "Churna": "CHR",
        "Ghee": "GHE",
        "Kwath": "KWA",
        "Ras": "RAS",
        "Basti": "BAS",
    }

    def __init__(self, input_dir: str = "output/images", output_dir: str = "output",
                 source: str = "Asvins Lifecare Pvt Ltd", use_ocr: bool = True, num_threads: int = 4,
                 output_json_filename: str = "medicines.json"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.source = source
        self.use_ocr = use_ocr and OCR_AVAILABLE
        self.num_threads = max(1, num_threads)  # At least 1 thread
        self.output_json_filename = output_json_filename
        self.medicines: List[Dict] = []
        self.successful_log: List[Dict] = []  # Log successful extractions
        self.failed_log: List[Dict] = []      # Log failed/skipped extractions
        self._lock = threading.Lock()  # For thread-safe access to lists

        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {self.input_dir}")

        self.output_dir.mkdir(parents=True, exist_ok=True)

        if use_ocr and not OCR_AVAILABLE:
            print("Warning: pytesseract not installed — brand names will be image filenames.")
            print("         Install with: pip install pytesseract  (and install Tesseract-OCR)")

    def _process_single_image(self, idx: int, image_path: Path) -> Tuple[Dict, Optional[str]]:
        """
        Process a single image. Returns (medicine_dict, log_entry).
        log_entry is the successful or failed log entry.
        """
        log_entry = {
            "index": idx,
            "imageName": image_path.name,
            "brandName": None,
            "medicineType": None,
            "medicineId": None,
        }
        
        try:
            pil_image = Image.open(image_path).convert("RGB")
            
            # Extract brand name via OCR
            brand_name = None
            medicine_type = None
            if self.use_ocr:
                brand_name = self._extract_brand_name(pil_image)
                # Also scan entire image for medicine type (may be elsewhere)
                medicine_type = self._extract_type_from_image(pil_image)

            # Fallback to filename if OCR failed
            if not brand_name:
                brand_name = image_path.stem.upper()

            # Extract medicine type from brand name if not found in image
            if not medicine_type:
                medicine_type = self._extract_medicine_type(brand_name)

            # Build base ID first
            base_id = self._sanitize_id(brand_name)

            # Build final ID: brand name + type abbreviation if found
            if medicine_type:
                type_abbr = self.TYPE_ABBREVIATIONS.get(medicine_type, medicine_type)
                string_id = f"{base_id}-{type_abbr}"
            else:
                string_id = base_id

            medicine_dict = {
                "id": string_id,
                "brandName": brand_name,
                "isActive": True,
                "source": self.source,
                "preferredAffiliate": False,
                "originalImageName": image_path.name,  # Mapping: original med00X.jpg
            }
            
            # Update log entry (successful)
            log_entry["brandName"] = brand_name
            log_entry["medicineType"] = medicine_type
            log_entry["medicineId"] = string_id
            
            type_str = f" [{medicine_type}]" if medicine_type else ""
            status_msg = f"{idx}: {string_id}{type_str} -> '{brand_name}'"
            
            return medicine_dict, log_entry, status_msg, None

        except Exception as e:
            log_entry["error"] = str(e)
            status_msg = f"{idx}: SKIPPED ({str(e)[:60]})"
            return None, log_entry, status_msg, e

    def process(self, single_image: Optional[str] = None) -> int:
        """Process images in input directory using thread pool.
        
        Args:
            single_image: Optional filename to process just one image (e.g., 'med112.jpg')
        """
        images = sorted(self.input_dir.glob("*.jpg")) + sorted(self.input_dir.glob("*.png"))

        if not images:
            print(f"No images found in {self.input_dir}")
            return 0

        # Filter to single image if specified
        if single_image:
            images = [img for img in images if img.name == single_image]
            if not images:
                print(f"Image not found: {single_image}")
                print(f"Available images: {', '.join([img.name for img in sorted(self.input_dir.glob('*.jpg')) + sorted(self.input_dir.glob('*.png'))])[:200]}")
                return 0

        print(f"Processing {len(images)} image(s) from: {self.input_dir}")
        print(f"OCR: {'on' if self.use_ocr else 'off'}")
        print(f"Threads: {self.num_threads}\n")

        # Process images using thread pool
        results = []
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            # Submit all tasks
            futures = {
                executor.submit(self._process_single_image, idx, image_path): (idx, image_path)
                for idx, image_path in enumerate(images, 1)
            }
            
            # Collect results as they complete
            for future in as_completed(futures):
                try:
                    medicine_dict, log_entry, status_msg, error = future.result()
                    
                    # Thread-safe updates
                    with self._lock:
                        if medicine_dict:
                            self.medicines.append(medicine_dict)
                            self.successful_log.append(log_entry)
                        else:
                            self.failed_log.append(log_entry)
                        
                        print(f"{status_msg}")
                        results.append((medicine_dict is not None, log_entry))
                except Exception as e:
                    print(f"Worker error: {e}")

        # Sort medicines by image index to maintain order
        # (results came in completion order, but we need image order)
        idx_to_medicine = {}
        idx_to_successful_log = {}
        idx_to_failed_log = {}
        
        for i, log_entry in enumerate(self.successful_log):
            idx_to_medicine[log_entry["index"]] = self.medicines[len(idx_to_medicine)]
            idx_to_successful_log[log_entry["index"]] = log_entry
        
        for log_entry in self.failed_log:
            idx_to_failed_log[log_entry["index"]] = log_entry
        
        # Rebuild in original image order
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
        print(f"{'='*60}")

        # Run validation and generate report
        validation_passed = self._validate_and_report()

        # Only rename images if validation passed with no critical issues
        if validation_passed:
            self._rename_images_to_final_names()
        else:
            print("\n⚠️  IMAGE RENAME SKIPPED - Fix validation issues first!")
            print("   Edit output/medicines.json directly and re-run step 2c with rename_images.py\n")

        return len(self.medicines)

    def _extract_brand_name(self, img: Image.Image) -> Optional[str]:
        """
        Extract brand name via OCR (top 35% of image where names typically appear).
        """
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

    def _extract_medicine_type(self, brand_name: str) -> Optional[str]:
        """Extract medicine type/dosage form from brand name."""
        dosage_forms = {
            "tablet": "Tablet",
            "tablets": "Tablets",
            "capsule": "Capsule",
            "capsules": "Capsules",
            "junior syrup": "Junior Syrup",
            "syrup": "Syrup",
            "injection": "Injection",
            "infusion": "Infusion",
            "cream": "Cream",
            "gel": "Gel",
            "drops": "Drops",
            "ointment": "Ointment",
            "powder": "Powder",
            "suspension": "Suspension",
            "softgel": "Softgel",
            "softgels": "Softgels",
            "spray": "Spray",
            "device": "Device",
            "liquid": "Liquid",
            "solution": "Solution",
            "lotion": "Lotion",
            "shampoo": "Shampoo",
            "tonic": "Tonic",
            "device": "Device",
            "soap": "Soap",
            "sachet": "Sachet",
            "oil": "Oil",
            "patch": "Patch",
            "suppository": "Suppository",
            "paste": "Paste",
            "liniment": "Liniment",
            "nasal spray": "Nasal Spray",
            "eye drops": "Eye Drops",
            "ear drops": "Ear Drops",
            "effervescent": "Effervescent",
            "dry syrup": "Dry Syrup",
            "vial": "Vial",
            "ampule": "Ampule",
            "lozenges": "Lozenges",
            "film": "Film",
            "balm": "Balm",
            "inhaler": "Inhaler",
            "emulsion": "Emulsion",
            "granules": "Granules",
            "pessary": "Pessary",
            "enema": "Enema",
            "tincture": "Tincture",
            "elixir": "Elixir",
            "mouthwash": "Mouthwash",
            "gargle": "Gargle",
            "gummies": "Gummies",
            "wash": "Wash",
            "rub": "Rub",
            "pellets": "Pellets",
            "eye ointment": "Eye Ointment",
            "eye gel": "Eye Gel",
            "churna": "Churna",
            "ghee": "Ghee",
            "kwath": "Kwath",
            "ras": "Ras",
            "basti": "Basti",
        }

        # Check for multi-word phrases first (e.g., "Junior Syrup")
        brand_lower = brand_name.lower()
        for phrase in ["junior syrup"]:
            if phrase in brand_lower:
                return dosage_forms[phrase]

        # Check individual words
        words = brand_name.split()
        for word in words:
            word_lower = word.lower().strip(".,;:-")
            if word_lower in dosage_forms:
                return dosage_forms[word_lower]

        return None

    def _extract_type_from_image(self, img: Image.Image) -> Optional[str]:
        """Scan entire image for medicine type/dosage form keywords."""
        if not self.use_ocr:
            return None

        dosage_forms = {
            "tablet": "Tablet",
            "tablets": "Tablets",
            "capsule": "Capsule",
            "capsules": "Capsules",
            "junior syrup": "Junior Syrup",
            "syrup": "Syrup",
            "injection": "Injection",
            "infusion": "Infusion",
            "cream": "Cream",
            "gel": "Gel",
            "drops": "Drops",
            "ointment": "Ointment",
            "powder": "Powder",
            "suspension": "Suspension",
            "softgel": "Softgel",
            "softgels": "Softgels",
            "spray": "Spray",
            "device": "Device",
            "liquid": "Liquid",
            "solution": "Solution",
            "lotion": "Lotion",
            "shampoo": "Shampoo",
            "tonic": "Tonic",
            "device": "Device",
            "soap": "Soap",
            "sachet": "Sachet",
            "oil": "Oil",
            "patch": "Patch",
            "suppository": "Suppository",
            "paste": "Paste",
            "liniment": "Liniment",
            "nasal spray": "Nasal Spray",
            "eye drops": "Eye Drops",
            "ear drops": "Ear Drops",
            "effervescent": "Effervescent",
            "dry syrup": "Dry Syrup",
            "vial": "Vial",
            "ampule": "Ampule",
            "lozenges": "Lozenges",
            "film": "Film",
            "balm": "Balm",
            "inhaler": "Inhaler",
            "emulsion": "Emulsion",
            "granules": "Granules",
            "pessary": "Pessary",
            "enema": "Enema",
            "tincture": "Tincture",
            "elixir": "Elixir",
            "mouthwash": "Mouthwash",
            "gargle": "Gargle",
            "gummies": "Gummies",
            "wash": "Wash",
            "rub": "Rub",
            "pellets": "Pellets",
            "eye ointment": "Eye Ointment",
            "eye gel": "Eye Gel",
            "churna": "Churna",
            "ghee": "Ghee",
            "kwath": "Kwath",
            "ras": "Ras",
            "basti": "Basti",
        }

        try:
            # Scan entire image for text
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            all_text = " ".join(data["text"]).lower()

            # Check for multi-word phrases first (e.g., "Junior Syrup")
            if "junior syrup" in all_text:
                return dosage_forms["junior syrup"]

            # Check for other dosage form keywords
            for keyword in dosage_forms.keys():
                if keyword != "junior syrup" and keyword in all_text:
                    return dosage_forms[keyword]
        except Exception:
            pass

        return None

    @staticmethod
    def _clean_word(text: str) -> str:
        """Remove punctuation/noise, keep letters, digits, and hyphens."""
        return re.sub(r"[^A-Za-z0-9\-]", "", text).strip()

    @staticmethod
    def _sanitize_id(text: str) -> str:
        """Convert brand name to a stable ID."""
        text = re.sub(r"[^A-Za-z0-9\s\-_]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text if text else "unknown"

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize whitespace and hyphen spacing."""
        name = re.sub(r"\s*\-\s*", "-", name)
        name = re.sub(r"\-\-+", "-", name)
        name = re.sub(r"\s+", " ", name).strip(" -")
        return name

    def _save_validation_report(self, issues: Dict):
        """Save validation report to JSON file."""
        report_path = self.output_dir / "validation_report.json"
        report = {
            "total_medicines": len(self.medicines),
            "issues": {
                "duplicates": issues["duplicates"],
                "missing_type": issues["missing_type"],
                "suspicious_names": issues["suspicious_name"],
                "bad_ids": issues["bad_id"]
            }
        }
        
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"Validation report saved: {report_path}")
        except Exception as e:
            print(f"Warning: Could not save validation report: {e}")

    def _rename_images_to_final_names(self):
        """Rename extracted images from med001.jpg to final {id}.jpg format."""
        images = sorted(self.input_dir.glob("*.jpg")) + sorted(self.input_dir.glob("*.png"))
        
        if len(images) != len(self.medicines):
            print(f"Warning: Image count ({len(images)}) != medicine count ({len(self.medicines)})")
            return

        print(f"\nRenaming {len(images)} images to final names...")
        for idx, medicine in enumerate(self.medicines):
            if idx >= len(images):
                break
            old_path = images[idx]
            final_id = medicine["id"]
            new_name = f"{final_id}{old_path.suffix}"
            new_path = self.input_dir / new_name

            try:
                if new_path.exists():
                    new_path.unlink()
                old_path.rename(new_path)
                print(f"  {old_path.name} → {new_name}")
            except Exception as e:
                print(f"  {old_path.name} → ERROR: {e}")

    def _validate_and_report(self):
        """Validate medicines and generate quality report. Returns True if validation passed."""
        issues = {
            "duplicates": [],
            "missing_type": [],
            "suspicious_name": [],
            "bad_id": [],
            "warnings": []
        }

        seen_ids = set()
        suspicious_patterns = [
            r"^[A-Z0-9\-]+$",  # All caps/numbers only
            r".{2,}",          # Too short (< 2 chars handled separately)
        ]

        # Build a mapping of ID to original image name
        id_to_image = {med["id"]: med.get("originalImageName", "unknown") for med in self.medicines}

        for med in self.medicines:
            med_id = med["id"]
            brand = med["brandName"]
            image_name = med.get("originalImageName", "unknown")

            # Check for duplicates
            if med_id in seen_ids:
                issues["duplicates"].append({"id": med_id, "image": image_name})
            seen_ids.add(med_id)

            # Check for missing medicine type
            if not med_id.endswith(("-TAB", "-TABS", "-CAP", "-CAPS", "-JSYR", "-SYR", "-INJ", "-INF",
                                    "-CRM", "-GEL", "-DRP", "-OIN", "-PWD", "-SUS", 
                                    "-SGC", "-SPR", "-DEV", "-LIQ", "-SOL", "-LOT", "-SHP", "-TON", "-SOP", "-SAC",
                                    "-OIL", "-PTH", "-SUP", "-PST", "-LIN", "-NSP", "-EYE", "-EAR",
                                    "-EFF", "-DSY", "-VIL", "-AMP", "-LOZ", "-FLM", "-BAL", "-INH", "-EMU", "-GRN", "-PES", "-ENM",
                                    "-TNC", "-ELX", "-MWH", "-GAR", "-GUM", "-WSH", "-RUB", "-PEL", "-EYO", "-EYG",
                                    "-CHR", "-GHE", "-KWA", "-RAS", "-BAS")):
                issues["missing_type"].append({"id": med_id, "image": image_name})

            # Check for suspicious brand names
            if len(brand) < 2:
                issues["suspicious_name"].append({"id": med_id, "name": brand, "image": image_name, "reason": "Too short"})
            elif len(brand) > 80:
                issues["suspicious_name"].append({"id": med_id, "name": brand, "image": image_name, "reason": "Too long (>80 chars)"})
            elif not any(c.isalnum() for c in brand):
                issues["suspicious_name"].append({"id": med_id, "name": brand, "image": image_name, "reason": "No alphanumeric chars"})
            elif brand.count("-") > 3:
                issues["suspicious_name"].append({"id": med_id, "name": brand, "image": image_name, "reason": "Too many hyphens (>3)"})
            
            # Check for pharmaceutical composition/description patterns (should NOT be in brand name)
            brand_lower = brand.lower()
            
            # Check for composition keywords (e.g., "Diclofenac Sodium IP 75mg")
            composition_keywords = {"mg", "mcg", "gm", "ml", "wv", "w/v", "w/w", "ip", "usp",
                                  "sodium", "hydrochloride", "sulphate", "sulfate", "tartrate",
                                  "citrate", "phosphate", "acetate", "chloride", "bromide"}
            composition_count = sum(1 for kw in composition_keywords if kw in brand_lower)
            if composition_count >= 2:
                issues["suspicious_name"].append({"id": med_id, "name": brand, "image": image_name, 
                                                 "reason": "Looks like composition (multiple pharma keywords)"})
            
            # Check for generic drug name patterns (should be in brand name, not as brand)
            generic_drugs = {
                "selenium", "l-carnitine", "diclofenac", "hydroxyzine", "minoxidil",
                "dapagliflozin", "metformin", "glimepiride", "metoprolol", "olmesartan"
            }
            if any(drug in brand_lower for drug in generic_drugs):
                issues["suspicious_name"].append({"id": med_id, "name": brand, "image": image_name, 
                                                 "reason": "Looks like generic drug name, not brand"})
            
            # Check for dose patterns (e.g., "1125 gm", "25mg")
            if re.search(r'^\d+\s*(mg|mcg|ml|gm|wv)', brand_lower):
                issues["suspicious_name"].append({"id": med_id, "name": brand, "image": image_name, 
                                                 "reason": "Starts with dose (e.g., '25mg')"})
            
            # Check for formulation keywords that shouldn't be brand names
            formulation_keywords = {"capsules", "tablets", "injection", "ointment", "cream", "gel",
                                  "suspension", "solution", "lotion", "spray", "film", "pellets"}
            if any(kw in brand_lower for kw in formulation_keywords):
                issues["suspicious_name"].append({"id": med_id, "name": brand, "image": image_name, 
                                                 "reason": "Contains formulation keyword (not brand)"})
            
            # Check for company/manufacturer names
            company_keywords = {"akums", "asvins", "lifecare", "pvt", "ltd", "pharmaceuticals",
                              "manufactured by", "made by", "produced by"}
            if any(kw in brand_lower for kw in company_keywords):
                issues["suspicious_name"].append({"id": med_id, "name": brand, "image": image_name, 
                                                 "reason": "Contains company/manufacturer name"})

            # Check for bad ID format
            if len(med_id) < 2:
                issues["bad_id"].append({"id": med_id, "image": image_name, "reason": "Too short"})
            elif len(med_id) > 100:
                issues["bad_id"].append({"id": med_id, "image": image_name, "reason": "Too long (>100 chars)"})
            elif med_id.startswith("-") or med_id.endswith("-"):
                issues["bad_id"].append({"id": med_id, "image": image_name, "reason": "Starts or ends with hyphen"})

        # Generate report
        print(f"\n{'='*60}")
        print("VALIDATION REPORT")
        print(f"{'='*60}")

        critical_issues = len(set([item["id"] for item in issues["duplicates"]])) + len(issues["bad_id"])
        total_issues = sum(len(v) if isinstance(v, list) else 0 for v in issues.values())

        if total_issues == 0:
            print("✅ VALIDATION PASSED - All medicines are valid!")
            validation_ok = True
        else:
            print(f"⚠️  Found {total_issues} issue(s):\n")

            if issues["duplicates"]:
                unique_dups = set([item["id"] for item in issues["duplicates"]])
                print(f"❌ DUPLICATES ({len(unique_dups)}): CRITICAL")
                for dup_item in issues["duplicates"]:
                    print(f"   {dup_item['id']} (from {dup_item['image']})")

            if issues["bad_id"]:
                print(f"\n❌ BAD ID FORMAT ({len(issues['bad_id'])}): CRITICAL")
                for bad_item in issues["bad_id"]:
                    print(f"   {bad_item['id']} (from {bad_item['image']}): {bad_item['reason']}")

            if issues["missing_type"]:
                print(f"\n❌ MISSING MEDICINE TYPE ({len(issues['missing_type'])}): WARNING")
                for missing_item in issues["missing_type"][:5]:
                    print(f"   {missing_item['id']} (from {missing_item['image']})")
                if len(issues["missing_type"]) > 5:
                    print(f"   ... and {len(issues['missing_type']) - 5} more")

            if issues["suspicious_name"]:
                print(f"\n⚠️  SUSPICIOUS NAMES ({len(issues['suspicious_name'])}): WARNING")
                for susp_item in issues["suspicious_name"][:5]:
                    print(f"   {susp_item['id']} (from {susp_item['image']}): '{susp_item['name']}' ({susp_item['reason']})")
                if len(issues["suspicious_name"]) > 5:
                    print(f"   ... and {len(issues['suspicious_name']) - 5} more")

            validation_ok = critical_issues == 0

        print(f"\n{'='*60}")
        print("SUMMARY:")
        print(f"  Total medicines: {len(self.medicines)}")
        print(f"  Duplicates: {len(set([item['id'] for item in issues['duplicates']]))}")
        print(f"  Bad IDs: {len(issues['bad_id'])}")
        print(f"  Missing type: {len(issues['missing_type'])}")
        print(f"  Suspicious names: {len(issues['suspicious_name'])}")
        if validation_ok:
            print(f"  Status: ✅ READY TO RENAME")
        else:
            print(f"  Status: ❌ BLOCKING - Fix critical issues before rename")
        print(f"{'='*60}\n")

        # Save detailed report
        self._save_validation_report(issues)

        return validation_ok

    def save_json(self) -> Path:
        """Save medicines to specified JSON file."""
        json_path = self.output_dir / self.output_json_filename
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.medicines, f, indent=4, ensure_ascii=False)
        return json_path

    def save_extraction_log(self) -> tuple:
        """Save extraction logs to separate files (successful and failed)."""
        success_path = self.output_dir / "extraction_successful.json"
        failed_path = self.output_dir / "extraction_failed.json"
        
        with open(success_path, "w", encoding="utf-8") as f:
            json.dump(self.successful_log, f, indent=2, ensure_ascii=False)
        
        with open(failed_path, "w", encoding="utf-8") as f:
            json.dump(self.failed_log, f, indent=2, ensure_ascii=False)
        
        return success_path, failed_path


def main():
    parser = argparse.ArgumentParser(description="Process images and create medicines.json (Step 2)")
    parser.add_argument("--input-dir", default="output/images", help="Directory with extracted images (default: output/images)")
    parser.add_argument("--output-dir", default="output", help="Output directory for medicines.json (default: output)")
    parser.add_argument("--output-json", default="medicines.json", help="Output JSON filename (default: medicines.json, use 'old_medicines.json' for Step 3)")
    parser.add_argument("--source", default="Asvins Lifecare Pvt Ltd", help="Medicine source (default: Asvins Lifecare Pvt Ltd)")
    parser.add_argument("--no-ocr", action="store_true", help="Skip OCR and use filenames as brand names")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads for parallel processing (default: 4, max: 32)")
    parser.add_argument("--image", default=None, help="Optional: Test single image only (e.g., med112.jpg)")
    parser.add_argument("--validate-only", default=None, help="Skip extraction, just validate existing medicines.json (e.g., --validate-only output/medicines.json)")

    args = parser.parse_args()

    try:
        # Validation-only mode
        if args.validate_only:
            json_path = Path(args.validate_only)
            output_dir = args.output_dir
            
            if not json_path.exists():
                print(f"Error: File not found: {json_path}")
                sys.exit(1)
            
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    medicines = json.load(f)
            except Exception as e:
                print(f"Error: Could not load JSON: {e}")
                sys.exit(1)
            
            print(f"\nValidating {len(medicines)} medicines from {json_path}...\n")
            
            # Use converter's validation method
            converter = ImagesToJsonConverter(
                input_dir=args.input_dir,
                output_dir=output_dir,
                source=args.source,
                use_ocr=False,
                num_threads=1
            )
            converter.medicines = medicines
            validation_passed = converter._validate_and_report()
            
            if validation_passed:
                print("✅ Validation passed!")
                sys.exit(0)
            else:
                print("❌ Validation failed. Review report above.")
                sys.exit(1)
        
        # Normal extraction mode
        converter = ImagesToJsonConverter(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            source=args.source,
            use_ocr=not args.no_ocr,
            num_threads=args.threads,
            output_json_filename=args.output_json
        )
        count = converter.process(single_image=args.image)
        json_path = converter.save_json()
        success_log_path, failed_log_path = converter.save_extraction_log()
        print(f"\n✓ Step 2 complete: {count} medicines exported to {json_path}")
        print(f"✓ Extraction logs saved:")
        print(f"  - Successful: {success_log_path}")
        print(f"  - Failed: {failed_log_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
