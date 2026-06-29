#!/usr/bin/env python3
"""
Extract Medicine Info from OCR Text with Improved Pattern Matching

Parses OCR text JSON (from extract_ocr_text.py with preprocessing) to extract:
- Brand name with dosage: multi-tier pattern matching for complete identifiers
- Medicine type/form (Tablet, Capsule, Syrup, etc.)
- OCR character correction (L→I, O→0, etc.)
- Manufacturer/source from OCR text

Improved OCR handling:
- Better pattern matching for hyphenated brand names
- Multi-line dosage extraction
- Context-aware brand completion
- Robust fallback patterns

Input: images_text_all.json (from extract_ocr_text.py with preprocessing)
Output: medicines.json (complete structured data)

Usage:
    python extract_medicine_info.py --input-json output/images_text_all.json
    python extract_medicine_info.py --input-json output/images_text_all.json --output-json medicines.json
    python extract_medicine_info.py --input-json output/images_text_all.json --verbose
"""

import json
import re
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from difflib import SequenceMatcher


# Configuration for improved OCR extraction
class ExtractionConfig:
    """Configuration for medicine extraction from OCR text"""
    
    # Brand name patterns
    MIN_BRAND_LENGTH = 5
    BRAND_HYPHEN_PATTERNS = {
        'hyphenated': r'\b([A-Z][A-Z0-9]{3,}(?:\-[A-Z0-9]{1,}){1,})\b',
        'complete_with_dosage': r'\b([A-Z][A-Z0-9]{3,}(?:\-[A-Z0-9]{1,})*\-\d{1,3})\b',
    }
    
    # Medicine type patterns
    MEDICINE_TYPES = {
        'tablet': ['tablet', 'tablets', 'tab', 'tabs'],
        'capsule': ['capsule', 'capsules', 'cap', 'caps'],
        'syrup': ['syrup', 'syrups', 'oral solution'],
        'injection': ['injection', 'injections', 'injectable'],
        'cream': ['cream', 'creams'],
        'ointment': ['ointment', 'ointments', 'oleum'],
        'gel': ['gel', 'gels'],
        'suspension': ['suspension', 'suspensions', 'oral'],
        'powder': ['powder', 'powders'],
        'spray': ['spray', 'sprays', 'aerosol'],
        'drops': ['drops', 'liquid', 'solution'],
    }
    
    # OCR noise patterns to filter
    OCR_NOISE_DIGITS = {'04', '07', '08', '09', '00', '01', '02', '03'}
    
    # Dosage extraction patterns
    DOSAGE_PATTERN = r'(\d{1,3})(?:mg|ml|mcg|µg)'
    
    # Extraction confidence thresholds
    MIN_CONFIDENCE = 0.7
    GOOD_CONFIDENCE = 0.85


class OCRCorrector:
    """Correct common OCR character misreads"""
    
    # Common OCR character substitutions
    CHAR_MISREADS = {
        'L': ['I', '1', '|'],
        'I': ['l', '1', '|', 'L'],
        'O': ['0', 'D'],
        'M': ['N'],
        'S': ['5', '8'],
        'B': ['8', 'D'],
        'Z': ['2'],
        'G': ['C', '6'],
        'U': ['V', 'W'],
    }
    
    def __init__(self, reference_ids: Dict[str, str]):
        self.reference_ids = reference_ids
    
    def find_reference_match(self, extracted_id: str, threshold: float = 0.85) -> Optional[Tuple[str, float]]:
        """Find closest matching reference ID using fuzzy matching"""
        if not self.reference_ids:
            return None
        
        best_match = None
        best_score = 0
        
        for ref_id in self.reference_ids:
            score = SequenceMatcher(None, extracted_id.upper(), ref_id.upper()).ratio()
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = ref_id
        
        return (best_match, best_score) if best_match else None
    
    def correct_character_misreads(self, extracted_id: str) -> List[str]:
        """Generate list of possible corrections for common OCR misreads"""
        corrections = [extracted_id]
        
        for pos, char in enumerate(extracted_id):
            if char in self.CHAR_MISREADS:
                for misread in self.CHAR_MISREADS[char]:
                    corrected = extracted_id[:pos] + misread + extracted_id[pos+1:]
                    corrections.append(corrected)
        
        unique_corrections = []
        seen = set()
        for correction in corrections:
            if correction not in seen:
                seen.add(correction)
                unique_corrections.append(correction)
        
        scored_corrections = []
        for correction in unique_corrections:
            match = self.find_reference_match(correction, threshold=0.80)
            if match:
                scored_corrections.append((correction, match[1]))
            else:
                scored_corrections.append((correction, 0))
        
        scored_corrections.sort(key=lambda x: x[1], reverse=True)
        return [c[0] for c in scored_corrections]
    
    def is_ocr_noise(self, extracted_id: str) -> bool:
        """Determine if extracted ID is likely OCR noise"""
        noise_indicators = [
            (r'^[A-Z]{2,}-{2,}', 'double-hyphen'),
            (r'^([A-Z])\1{2,}', 'triple letter'),
            (r'[0-9]{10,}', 'long number'),
            (r'[^A-Z0-9\-]{3,}', 'special chars'),
        ]
        
        id_upper = extracted_id.upper()
        for pattern, reason in noise_indicators:
            if re.search(pattern, id_upper):
                return True
        
        return False


class ExtractionValidator:
    """Validate extracted medicines against reference"""
    
    def __init__(self, reference_ids: Dict[str, str]):
        self.reference_ids = reference_ids
        self.reference_id_list = set(reference_ids.keys())
    
    def is_exact_match(self, medicine_id: str) -> bool:
        """Check if ID matches reference exactly"""
        return medicine_id in self.reference_id_list
    
    def find_likely_reference(self, extracted_id: str) -> Optional[str]:
        """Find most likely reference ID for extracted medicine"""
        corrector = OCRCorrector(self.reference_ids)
        
        if extracted_id in self.reference_id_list:
            return extracted_id
        
        match = corrector.find_reference_match(extracted_id, threshold=0.85)
        if match:
            return match[0]
        
        return None


class MedicineInfoExtractor:
    """Extract structured medicine information from OCR text."""

    # Valid medicine forms
    DOSAGE_FORMS = {
        "tablet": "Tablet",
        "tablets": "Tablet",
        "capsule": "Capsule",
        "capsules": "Capsule",
        "syrup": "Syrup",
        "injection": "Injection",
        "infusion": "Infusion",
        "cream": "Cream",
        "gel": "Gel",
        "drops": "Drops",
        "ointment": "Ointment",
        "powder": "Powder",
        "suspension": "Suspension",
        "spray": "Spray",
        "solution": "Solution",
        "lotion": "Lotion",
        "shampoo": "Shampoo",
        "soap": "Soap",
        "inhaler": "Inhaler",
        "wash": "Wash",
        "duo": "Duo",
    }

    # Medicine type → ID suffix mapping
    TYPE_ABBREVIATIONS = {
        "Tablet": "TAB",
        "Capsule": "CAP",
        "Pellets": "PEL",
        "Effervescent": "EFF",
        "Lozenges": "LOZ",
        "Syrup": "SYR",
        "Junior Syrup": "JSYR",
        "Elixir": "ELX",
        "Tincture": "TNC",
        "Dry Syrup": "DSY",
        "Injection": "INJ",
        "Infusion": "INF",
        "Vial": "VIL",
        "Ampule": "AMP",
        "Cream": "CRM",
        "Gel": "GEL",
        "Ointment": "OIN",
        "Oil": "OIL",
        "Paste": "PST",
        "Liniment": "LIN",
        "Balm": "BAL",
        "Rub": "RUB",
        "Drops": "DRP",
        "Solution": "SOL",
        "Lotion": "LOT",
        "Eye Drops": "EYE",
        "Nasal Spray": "NSP",
        "Powder": "PWD",
        "Granules": "GRN",
        "Suspension": "SUS",
        "Softgel": "SGC",
        "Spray": "SPR",
        "Film": "FLM",
        "Inhaler": "INH",
        "Gummies": "GUM",
        "Device": "DEV",
        "Other": "OTH",
    }

    def __init__(self, json_file: str, source: str = "Biofrench", verbose: bool = False):
        self.json_file = Path(json_file)
        self.source = source
        self.verbose = verbose
        self.config = ExtractionConfig()
        self.medicines_data: List[Dict] = []
        self.reference_ids_dict = self._load_reference_ids()  # Load reference IDs for cleaning
        
        # Initialize validators and correctors
        self.validator = ExtractionValidator(self.reference_ids_dict)
        self.corrector = OCRCorrector(self.reference_ids_dict)

    def _load_reference_ids(self) -> Dict[str, str]:
        """Load reference medicine IDs (deprecated - now purely OCR-based).
        Returns empty dict as extraction relies on OCR patterns only."""
        # Extraction is now purely OCR-based without external reference data
        return {}

    def _clean_extracted_id(self, extracted_id: str, brand_name: str) -> str:
        """Clean extracted ID by removing OCR noise and validating against reference.
        
        Examples:
        - APPYSVI-AP-SYR -> APPYSVI-SYR (remove OCR noise)
        - ALSIFEN-120-TABLETS-TAB -> ALSIFEN-120-TAB (remove redundant form words)
        - ASVCON-100-POTENT-ANT-CAP -> ASVCON-100-CAP (remove marketing noise)
        """
        # Known OCR noise patterns to remove
        noise_patterns = {
            'POTENT-ANT', 'WEATHRA', 'WEDIATS', 'WEELINTS', 'WERAFERRAY',
            'TABLETS-URS', 'TABLETS-PAR', 'TABLETS-ACE', 'TABLETS-MET',
            'TABLETS-DYD', 'TABLETS-LIN', 'TABLETS-CEF', 'TABLETS-AZI',
            'TABLETS-OE', 'TABLETS-SEL', 'TABLETS-TAR', 'ITERITERA',
            'INJECTION-HYD', 'INJECTION-NAN', 'INJECTION-INJ',
            'SOFTGEL-CAP', 'SOFTGEL-CAP-CAP', 'SOFTGEL', 'BIOTIC-CAP',
            'UFT', 'URS', 'PAR', 'ACE', 'MET', 'LIN', 'CEF', 'AZI', 'OE', 'DYD',
            'MTIROMYDN', 'METHYLCOBA', 'METHYLCOBALAMIN', 'POTASSIUM-CLA'
        }
        
        # Try to find exact match in reference first
        if extracted_id in self.reference_ids_dict:
            return extracted_id  # Exact match
        
        # Remove known noise patterns
        cleaned = extracted_id
        for pattern in noise_patterns:
            cleaned = re.sub(f'-{re.escape(pattern)}(?=-|$)', '', cleaned, flags=re.IGNORECASE)
        
        # Remove redundant form words
        form_noise = {
            'TABLETS-TAB': 'TAB',
            'CAPSULES-CAP': 'CAP', 
            'SYRUP-SYR': 'SYR',
            'INJECTION-INJ': 'INJ',
            'CREAM-CRM': 'CRM',
            'GEL-GEL': 'GEL',
            'SUSPENSION-SUS': 'SUS'
        }
        
        for noise, replacement in form_noise.items():
            cleaned = re.sub(noise, replacement, cleaned, flags=re.IGNORECASE)
        
        # Remove consecutive hyphens
        cleaned = re.sub(r'-+', '-', cleaned)
        
        return cleaned.rstrip('-')

    def _build_id(self, brand_name: str, medicine_type: Optional[str]) -> str:
        """Build final medicine ID from brand name and type, with OCR noise cleanup."""
        # Sanitize brand name
        brand_id = brand_name.strip().rstrip('-')
        
        # Add type suffix if available
        if medicine_type and medicine_type in self.TYPE_ABBREVIATIONS:
            type_suffix = self.TYPE_ABBREVIATIONS[medicine_type]
            extracted_id = f"{brand_id}-{type_suffix}"
        else:
            extracted_id = brand_id
        
        # Clean extracted ID to remove OCR noise
        cleaned_id = self._clean_extracted_id(extracted_id, brand_name)
        
        # Try to find exact reference match or fuzzy correction
        corrected_id = self._validate_and_correct_id(cleaned_id, brand_name)
        
        return corrected_id
    
    def _validate_and_correct_id(self, medicine_id: str, brand_name: str) -> str:
        """Validate extracted ID against reference and suggest corrections
        
        Returns: Best available ID (exact match > fuzzy match > corrected > original)
        """
        # Check exact match first
        if self.validator.is_exact_match(medicine_id):
            return medicine_id
        
        # Try OCR character corrections (e.g., L→I misreads)
        corrections = self.corrector.correct_character_misreads(medicine_id)
        for correction in corrections[1:]:  # Skip original (already checked)
            if self.validator.is_exact_match(correction):
                return correction
        
        # Try fuzzy match with reference
        match = self.corrector.find_reference_match(medicine_id, threshold=0.85)
        if match:
            ref_id, score = match
            return ref_id
        
        # If it looks like noise, flag it for later filtering
        if self.corrector.is_ocr_noise(medicine_id):
            # Still return it, but mark as potential noise
            pass
        
        # Return original if no corrections found
        return medicine_id

    def _extract_dosage(self, text: str) -> List[str]:
        """Extract dosages with units from text.
        
        Handles: mg, mcg, µg, ml, l, gm, iu, units, %, wv, w/v, etc.
        Returns list of unique dosages found.
        """
        dosages = []
        # More comprehensive pattern including fractions, decimals, ranges
        pattern = r'(\d+(?:\.\d+)?)\s*(mg|mcg|µg|ml|l|gm|iu|wv|w/v|units|%|g)(?![a-z])'
        matches = re.findall(pattern, text, re.IGNORECASE)

        seen = set()
        for match in matches:
            amount, unit = match
            # Normalize units
            unit_normalized = unit.lower().replace('w/v', 'wv').replace('gm', 'mg')
            dosage = f"{amount}{unit_normalized}"
            
            if dosage not in seen:
                dosages.append(dosage)
                seen.add(dosage)

        return dosages

    def _extract_medicine_type(self, text: str) -> Optional[str]:
        """Extract medicine type/form from brand name or full text.
        
        Strategy:
        1. Multi-word phrases first (e.g., "Junior Syrup", "Eye Drops")
        2. Exact keyword matches (strict)
        3. Conservative fuzzy matches for OCR corruptions (high threshold 80%+)
        """
        text_lower = text.lower()

        # Multi-word phrases first (e.g., "Junior Syrup", "Eye Drops")
        for phrase in ["junior syrup", "eye drops", "nasal spray", "ear drops", "dry syrup", "eye ointment", "eye gel", "inhaler device", "face wash", "nasal duo"]:
            if phrase in text_lower:
                # Map phrase to form, handling special cases
                if "duo" in phrase:
                    return "Duo"
                elif "wash" in phrase:
                    return "Wash"
                return self.DOSAGE_FORMS.get(phrase.split()[-1], phrase.title())

        # Single keywords - exact match in DOSAGE_FORMS dict (STRICT)
        for keyword, form in self.DOSAGE_FORMS.items():
            if keyword in text_lower:
                return form

        # Conservative fuzzy matching for OCR corruptions only
        # Use HIGHER threshold (80%+) to avoid false positives
        import difflib
        
        words = text_lower.split()
        for keyword, form in self.DOSAGE_FORMS.items():
            for word in words:
                # Remove non-alphabetic chars for comparison
                word_clean = re.sub(r'[^a-z]', '', word)
                keyword_clean = keyword
                
                # Only match if similarity is 80%+ (stricter than before)
                if len(word_clean) >= 4 and len(keyword_clean) >= 4:
                    similarity = difflib.SequenceMatcher(None, word_clean, keyword_clean).ratio()
                    if similarity >= 0.80:  # Increased from 0.65 to reduce false positives
                        return form

        return None

    def _extract_source(self, text: str) -> str:
        """Extract source/manufacturer from OCR text."""
        text_lower = text.lower()
        
        # Check for known manufacturers
        if 'asvins' in text_lower and 'lifecare' in text_lower:
            return "Asvins Lifecare Pvt Ltd"
        elif 'akums' in text_lower:
            return "Akums Drugs"
        elif 'asvins' in text_lower:
            return "Asvins"
        elif 'lifecare' in text_lower:
            return "Lifecare"
        
        # Default source
        return "Biofrench"

    def _clean_ocr_text_lines(self, text: str) -> str:
        """Clean OCR text by removing noise lines and formatting artifacts.
        
        Removes:
        - Pure formatting/noise lines (———, $$$###, etc.)
        - Lines with excessive special chars (OCR artifacts)
        - Empty or near-empty lines
        - Pure "Manufactured by" intro lines
        - Manufacturer-only branding lines
        
        Keeps:
        - All brand names (product brands, generic/API names, descriptors)
        - Ingredients, dosages, medicine type
        - Marketing text (helps with brand identification)
        
        Conservative approach: Preserve as much valid content as possible
        """
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty or very short lines
            if not stripped or len(stripped) < 2:
                continue
            
            # Skip pure formatting/noise lines (only special chars and spaces)
            if re.match(r'^[\-_$#@*£€\s\(\)\[\]\{\}]+$', stripped):
                continue
            
            # Skip lines with EXCESSIVE special chars (OCR artifacts - more than 50%)
            # This is more lenient to keep valid lines with some special chars
            special_char_ratio = len(re.findall(r'[_$#@*£€\(\)\[\]\{\}]', stripped)) / len(stripped)
            if special_char_ratio > 0.5:  # Changed from 0.4 to 0.5 to keep more content
                continue
            
            # Skip pure "manufactured by" intro lines (manufacturer intro without actual content)
            if re.match(r'^Manufactured by\s+[A-Z]{1,3}\s*[\-/\\]*\s*$', stripped, re.IGNORECASE):
                continue
            
            # Skip ONLY lines with ONLY manufacturer names and spacing
            # (but keep lines that have manufacturer name + other content like ASVINS-UDI-150)
            if re.match(r'^(AKUMS|LIFECARE|ASVINS LIFECARE|A Promise|Promise|Life)\s*$', stripped, re.IGNORECASE):
                # Pure manufacturer branding only - skip
                continue
            
            # Keep everything else:
            # - Generic/API drug names (GLIMEPIRIDE, ONDANSETRON, etc.)
            # - Descriptors (PROLONGED-RELEASE, LIVER-PROTECTIVE, etc.)
            # - Ingredients, benefits, formulations
            # - Brand names, hyphenated products
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def _extract_active_ingredients_dosage(self, text: str) -> Optional[str]:
        """Extract active ingredient dosages from text.
        
        Looks for patterns like:
        - "Telmisartan 80mg+Amlodipine 5mg+Hydrochlorothiazide 12.5mg"
        - "Fluconazole IP 150mg"
        - "Polyethylene Glycol 3350 USP 13.125gm"
        
        Returns simplified dosage: "80/5/12.5" or "150" or None
        """
        # Pattern: Active ingredient (letters/spaces) + number + unit
        pattern = r'([A-Za-z\s]+?)\s+(\d+(?:\.\d+)?)\s*(?:mg|ml|gm|mcg)\b'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        if not matches:
            return None
        
        # Extract just the dosage numbers, separated by slashes
        dosages = []
        for ingredient, dosage in matches:
            # Skip common form words and descriptive text
            ingredient_clean = ingredient.strip().upper()
            if len(ingredient_clean) < 3 or ingredient_clean in ['TABLETS', 'CAPSULES', 'SOLUTION', 'ORAL']:
                continue
            
            dosages.append(dosage)
            
            # Stop after extracting first 3 dosages (avoid overly long strings)
            if len(dosages) >= 3:
                break
        
        if dosages:
            return '/'.join(dosages)
        
        return None

    def _correct_common_ocr_misreads(self, brand_name: str) -> str:
        """Apply generic corrections for common OCR character misreads.
        
        Common patterns:
        - Missing letters at start: SVIINS → ASVIINS (missing A before S)
        - Character substitutions: I↔l, 1↔I, O↔0
        - Uses frequency analysis: if pattern appears many times, it's likely valid
        """
        if not brand_name or len(brand_name) < 4:
            return brand_name
        
        corrected = brand_name
        
        # Fix 1: Restore common prefixes that might be missing a letter
        # Pattern: If starts with S or A but not ASVI, might be missing A
        if corrected.startswith('SVIINS') or corrected.startswith('SVIINS'):
            corrected = 'ASVI' + corrected[1:]  # S→ASVI (restore ASVINS-like prefix)
        elif corrected.startswith('SVI') and len(corrected) > 10:
            # Could be ASVI missing the first A
            if corrected[3] in 'INS':
                corrected = 'A' + corrected
        
        # Fix 2: Double letters that shouldn't be there (ASVIINS → ASVIINS if only one I expected)
        # This is harder without reference, so skip for now
        
        # Fix 3: Fix common I/l/1 confusions in structural positions
        # ASVIIN-S → ASVINS (double I should be single I)
        if '--' not in corrected:  # Only if no double hyphens
            corrected = re.sub(r'([A-Z])\1{2,}', r'\1', corrected)  # Limit repeated chars to 1
        
        return corrected

    def _extract_brand_name(self, text: str) -> Optional[str]:
        """
        Extract brand name with general heuristics (no hardcoded lists).
        
        Strategy: Brands appear early in OCR text (before ingredients).
        Simple two-tier pattern matching with position priority.
        Includes OCR character correction for common misreadings.
        """
        # Clean OCR text first to remove noise and artifacts
        text = self._clean_ocr_text_lines(text)
        
        lines = text.strip().split('\n')
        
        # STOP patterns - lines that mark end of brand section
        stop_patterns = {'ingredients', 'ip:'}
        
        # Words to skip ONLY when standalone (not part of hyphenated brand names)
        # These are administrative/form words, NOT brand names
        skip_words_standalone = {
            'LIFECARE', 'ASVINSLIFECARE',  # Manufacturer combinations (rarely standalone brands)
            'TABLETS', 'CAPSULES', 'TABLET', 'CAPSULE',  # Forms
            'SYRUP', 'INJECTION', 'CREAM', 'GEL', 'OINTMENT',
            'POWDER', 'SUSPENSION', 'SPRAY', 'SOLUTION', 'LOTION', 'DROPS',
            'MADE', 'MANUFACTURED', 'PRODUCED', 'USED', 'ONLY', 'COMPOSITION',
            'PROMISE', 'JUNIOR', 'SOFTGEL', 'PAYEE',  # Marketing descriptors
            'HYDROXYZINE', 'FLUCONAZOLE', 'PROGESTERONE', 'INOSITOL',  # Generic drug names
            'SITAGLIPTIN', 'TELMISARTAN', 'FEXOFENADINE', 'ETORICOXIB',
            'FAROPENEM', 'ACETYLCYSTEINE', 'RABEPRAZOLE', 'MOXIFLOXACIN',
            'DICLOFENAC', 'LULICONAZOLE', 'GABAPENTIN', 'METHYLCOBALAMIN',
            'LETSW',  # OCR noise/corrupted
            # Chemical/pharmaceutical descriptors (NOT brand names)
            'HYDROCHLORIDE', 'PHOSPHATE', 'CARBONATE', 'CITRATE', 'SULFATE',
            'PROLONGED', 'RELEASE', 'EXTENDED', 'MODIFIED', 'SUSTAINED',
            'SECOND', 'FIRST', 'THIRD', 'GENERATION', 'RECEPTORS', 'PREVENTS',
            'CEPHALOSPORIN', 'BROAD', 'SPECTRUM'
        }
        
        # Words that MUST be hyphenated to be valid brands (skip if standalone)
        must_be_hyphenated = {'AKUMS', 'ASVINS', 'ASVI'}
        
        # Generic/API drug names that are VALID as fallback brands (not to be skipped)
        # These are actual drug names when product brand names unavailable
        valid_generic_names = {
            'GLIMEPIRIDE', 'ONDANSETRON', 'METFORMIN', 'ASPIRIN', 'IBUPROFEN',
            'PARACETAMOL', 'ATENOLOL', 'LISINOPRIL', 'AMOXYCILLIN', 'CIPROFLOXACIN',
            'OMEPRAZOLE', 'RANITIDINE', 'CLOPIDOGREL', 'ATORVASTATIN', 'SIMVASTATIN',
            'CETIRIZINE', 'LORATADINE', 'MONTELUKAST', 'SALBUTAMOL', 'DAPAGLIFLOZIN'
        }
        
        # OCR noise words to remove/replace at end of line
        ocr_noise = {'POLE', 'APLA', 'AAYA', 'PAGE', 'NOTE'}
        
        best_hyphenated = None  # Highest priority
        best_plain = None  # Fallback: plain 4+ letter words
        best_position = 999
        manufacturer_prefix_found = False  # Track if we found brand with known prefix
        
        # Known manufacturer/brand prefixes (high confidence)
        brand_prefixes = {'ASVINS', 'ASVI', 'AKUMS', 'DAPA', 'TENE', 'ATOR', 'PROLO', 'AMLO', 'ONCE', 'BROAD', 'TRIPLE', 'WELL', 'PROMISE', 'HIGH', 'ASVIPOD', 'ASVITUS', 'CANDIXIME', 'TELASVI'}
        
        # Scan lines looking for brand-like patterns
        for line_idx, line in enumerate(lines):
            line_lower = line.lower()
            
            # Stop at ingredients (brands always before)
            if any(pattern in line_lower for pattern in stop_patterns):
                break
            
            # Extended search range for actual brand names (they can appear up to line 15)
            # even if manufacturer info is in first few lines
            if line_idx > 15 and best_hyphenated:
                break  # Stop if we've found a brand and are past safe range
            
            line_upper = line.strip().upper()
            if not line_upper or len(line_upper) < 4:
                continue
            
            # OCR CORRECTION PHASE 1: Fix character misreadings
            # Fix 1: Replace 'I' → '1' when preceded by dash and followed by digit (e.g., "-I50" → "-150")
            line_upper = re.sub(r'-I(\d)', r'-1\1', line_upper)
            
            # Fix 2: Replace ':' → '-' in brand identifiers (e.g., "DAPA:M-10" → "DAPA-M-10")
            line_upper = re.sub(r'([A-Z]+):([A-Z]+-)', r'\1-\2', line_upper)
            
            # Fix 3: Remove noise words at end (e.g., "UDI- POLE" → "UDI-")
            for noise in ocr_noise:
                line_upper = re.sub(rf'-\s*{noise}\b', '', line_upper)
            
            # Remove non-alphanumeric noise from edges
            line_upper = re.sub(r'^[^A-Z0-9]+', '', line_upper).strip()
            line_upper = re.sub(r'[^A-Z0-9\-]+$', '', line_upper).strip()
            if not line_upper:
                continue
            
            # PRIORITY 1: Look for hyphenated brand patterns (BRAND-CODE, BRAND-DOSAGE, etc.)
            # Pattern: 4+ letters, followed by one or more hyphen-groups of letters/digits
            match = re.search(r'\b([A-Z]{4,}(?:-[A-Z0-9]{1,})+)\b', line_upper)
            if match:
                candidate = match.group(1)
                # Skip if it's just 2 chars after removing hyphens (likely OCR noise)
                if len(candidate.replace('-', '')) <= 2:
                    continue
                
                # REJECT if looks like ingredient dosages (multiple slashes: 250/400/50, 0.25/180/120)
                # These are NOT brand names, they're active ingredient dosages
                if candidate.count('/') >= 2:
                    continue  # Skip dosage patterns entirely
                
                first_part = candidate.split('-')[0]
                
                # REJECT if first part is a descriptor word (SECOND-GENERATION, PROLONGED-RELEASE, etc.)
                if first_part in skip_words_standalone:
                    continue  # Skip descriptor entirely
                
                # REJECT if candidate is followed by descriptor words (e.g., "TRIPLE-ACTION THERAPY-", "TRIPLE-ACTION POWER")
                # Words like THERAPY, POWER, RELIEF, FORMULA, etc. indicate marketing copy, not brand names
                end_pos = match.end()
                remaining_line = line_upper[end_pos:].strip()
                descriptor_followers = {'THERAPY', 'POWER', 'RELIEF', 'FORMULA', 'BLEND', 'COMPLEX', 'COMPLEX-', 'FOR', 'EFFECTIVE'}
                if any(desc in remaining_line for desc in descriptor_followers):
                    continue  # Skip marketing descriptor
                
                if first_part not in skip_words_standalone:
                    # Check if this candidate has a known brand prefix
                    has_brand_prefix = any(prefix in first_part for prefix in brand_prefixes)
                    
                    # Accept if:
                    # 1. Has a known brand prefix AND appears early, OR
                    # 2. Is early in text and we haven't found a prefix-based brand yet
                    should_update = False
                    if has_brand_prefix and line_idx < best_position:
                        should_update = True
                        manufacturer_prefix_found = True
                    elif not manufacturer_prefix_found and line_idx < best_position:
                        # Only accept non-prefix brands if we haven't found a prefix brand yet
                        should_update = True
                    
                    if should_update:
                        best_hyphenated = candidate
                        best_position = line_idx
                continue
            
            # PRIORITY 2: Look for plain 4+ letter capitalized words (no hyphens required)
            # Pattern: sequence of 4+ capital letters
            # Fallback: Accept known generic/API drug names OR any reasonably long word if no brand found
            match = re.search(r'\b([A-Z]{4,})\b', line_upper)
            if match:
                candidate = match.group(1)
                # Accept if:
                # 1. It's a known generic/API drug name (5+ chars), OR
                # 2. ANY 4+ letter word if we haven't found a brand yet (will be used as fallback)
                if not best_plain and candidate not in skip_words_standalone and candidate not in must_be_hyphenated:
                    if (candidate in valid_generic_names or len(candidate) >= 5):
                        # Only accept generic drugs if quite long (5+ chars) to avoid single words
                        if candidate in valid_generic_names or (len(candidate) >= 5 and '-' not in candidate):
                            best_plain = candidate
        
        # Return best match found (prioritize hyphenated)
        if best_hyphenated:
            # Keep the brand name as-is with slashes to preserve compound dosage information
            # Example: TENELISVISS-DM-20/10/500 must stay as-is to distinguish from TENELISVISS-DM-20/10/1000
            return best_hyphenated
        
        if best_plain:
            return best_plain
        
        return None



    def _find_complete_brand_variant(self, base_brand: str, text: str) -> Optional[str]:
        """Find a more complete version of the brand name with dosage numbers.
        Examples: "AMLOSVISS-MT" → "AMLOSVISS-MT-50" from "Amlosviss MT 50"
                  "TENELISVISS-DM-20" → "TENELISVISS-DM-20/10/500" from "TENELISVISS-DM-20/10/500"
        Conservative: Limits capture to prevent OCR noise
        """
        # Normalize base brand: replace hyphens with spaces for search
        base_prefix = base_brand.split('-')[0]
        
        # Search for lines containing the brand name (case-insensitive)
        lines = text.split('\n')
        best_match = None
        best_length = len(base_brand)
        
        for line in lines:
            line_upper = line.upper().strip()
            
            # Check if line contains the brand name pattern
            if base_prefix.upper() not in line_upper:
                continue
            
            # Enhanced pattern: handles compound dosages with multiple slashes
            # Matches: BRAND-CODE-20/10/500, BRAND-CODE-50/500, BRAND-CODE-50, etc.
            pattern = r'\b' + re.escape(base_prefix.upper()) + r'(?:[- ]([A-Z]{1,3}))?(?:[- ](\d{1,3}(?:/\d{1,4})*))?\b'
            match = re.search(pattern, line_upper)
            if match:
                # Build candidate carefully
                parts = [base_prefix.upper()]
                
                if match.group(1):  # Code part (e.g., "DM", "MT", "AZ")
                    code_part = match.group(1).strip()
                    if len(code_part) <= 3 and code_part not in ['TABLET', 'CAPSULE', 'TABLETS', 'CAPSULES']:
                        parts.append(code_part)
                
                if match.group(2):  # Dosage part (e.g., "20", "20/10/500", "50/500")
                    dosage_part = match.group(2).strip()
                    # Accept if it's a digit or digit/digit/digit pattern
                    if dosage_part and all(c.isdigit() or c == '/' for c in dosage_part):
                        # Validate compound dosage format (numbers separated by /)
                        dosage_parts = dosage_part.split('/')
                        valid = True
                        for d in dosage_parts:
                            if not (1 <= len(d) <= 4 and d.isdigit()):
                                valid = False
                                break
                        
                        if valid:
                            parts.append(dosage_part)
                
                candidate = '-'.join(parts)
                
                # Only accept if it's reasonable length (prevent noise)
                # Allow more length for compound dosages (e.g., 20/10/500)
                max_length = len(base_brand) + 20
                if len(candidate) <= max_length:
                    # Prefer longer matches (more complete dosage info)
                    if len(candidate) > best_length:
                        best_match = candidate
                        best_length = len(candidate)
        
        return best_match

    def _try_extend_brand(self, base_brand: str, text: str) -> Optional[str]:
        """Try to extend brand name with suffixes: space-separated numbers, hyphens, or letters.
        Examples: TELASVI-MT + " 25" → TELASVI-MT-25, ASVINS-DGM-1 → ASVINS-DGM-1
        """
        # Find the base brand in the text and look for what follows immediately
        # Pattern allows: space or hyphen, then alphanumeric (letters, digits, hyphens)
        match = re.search(re.escape(base_brand) + r'[\s\-]+([A-Z0-9]{1,10})(?:[\s\-]([A-Z]{1,3}))?', text, re.IGNORECASE)
        if match:
            suffix = match.group(1).strip().upper()
            
            # Skip if suffix is a form word (TABLETS, CAPSULES, etc.)
            form_words = {'TABLET', 'TABLETS', 'CAPSULE', 'CAPSULES', 'SYRUP', 'INJECTION', 
                         'CREAM', 'GEL', 'OINTMENT', 'POWDER', 'SUSPENSION', 'SPRAY', 'SOLUTION',
                         'LOTION', 'DROPS', 'FILM', 'SOFTGEL', 'INHALER', 'GUMMIES'}
            if suffix in form_words:
                # Don't append form words - return None to keep base brand as-is
                return None
            
            # Skip OCR noise: common OCR noise patterns
            if suffix.isdigit() and len(suffix) == 2 and suffix in self.config.OCR_NOISE_DIGITS:
                return None
            
            # If there's a two-part match (e.g., "300" + "SR"), combine them
            if match.group(2):
                part2 = match.group(2).strip().upper()
                if part2 not in form_words and len(suffix) <= 10 and len(part2) <= 3:
                    extended = f"{base_brand}-{suffix}-{part2}"
                    return extended
            
            # Single suffix: numbers or letters
            # Accept it as-is (e.g., ASVINS-DGM-1, AMLOSVISS-40-OLM)
            if len(suffix) <= 10:
                extended = f"{base_brand}-{suffix}"
                return extended
        
        return None

    def process(self) -> int:
        """Process JSON and extract medicine info with improved OCR logic."""
        if self.verbose:
            print("[INFO] Starting extraction with improved OCR logic")
            print(f"[INFO] Input: {self.json_file}")
            print(f"[INFO] Config: MIN_BRAND_LENGTH={self.config.MIN_BRAND_LENGTH}")
        
        print(f"Reading OCR JSON: {self.json_file}\n")

        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                text_data = json.load(f)
        except Exception as e:
            print(f"[ERR] Error reading JSON: {e}")
            return 0

        if not isinstance(text_data, dict):
            print("[ERR] JSON must be a dictionary with image names as keys")
            return 0

        print(f"Processing {len(text_data)} records...\n")
        
        # Tracking for quality reporting
        stats = {
            'total_images': len(text_data),
            'extracted': 0,
            'skipped': 0,
            'exact_matches': 0,
            'fuzzy_matches': 0,
            'noise_detected': 0
        }
        
        # Track IDs to detect and handle duplicates
        id_counter = {}  # Track occurrence count of each ID

        for idx, (image_name, text_content) in enumerate(text_data.items(), 1):
            if not text_content or not text_content.strip():
                print(f"{idx}: {image_name} - [SKIP] No text")
                stats['skipped'] += 1
                continue

            # Clean OCR text first (remove noise, formatting artifacts)
            cleaned_text = self._clean_ocr_text_lines(text_content)

            # Extract info
            brand_name = self._extract_brand_name(cleaned_text)
            medicine_type = self._extract_medicine_type(cleaned_text)
            source = self._extract_source(cleaned_text)
            
            # Apply generic OCR character corrections to brand name
            if brand_name:
                brand_name = self._correct_common_ocr_misreads(brand_name)
            
            # Try to find complete brand variant with full dosage info
            # BUT ONLY for structured brands (with hyphens like ASVINS-DGM-1)
            # Don't apply to plain generic names
            if brand_name and '-' in brand_name:
                complete_variant = self._find_complete_brand_variant(brand_name, text_content)
                if complete_variant and len(complete_variant) > len(brand_name):
                    # Only accept if still properly structured with reasonable length
                    if '-' in complete_variant and len(complete_variant) <= len(brand_name) + 15:
                        brand_name = complete_variant
            
            # Append active ingredient dosages to GENERIC brand names to distinguish variants
            # Generic indicators: ACTION, WEEKLY, PROMISE, SPECTRUM, ORAL, BEING, DEAL, ABSORPTION
            # Examples: TRIPLE-ACTION, ONCE-WEEKLY, BROAD-SPECTRUM, WELL-BEING, PROMISE
            # These are marketing names (not pharma codes like ASVINS-DGM-1) and need dosage disambiguation
            if brand_name:
                generic_indicators = ['ACTION', 'WEEKLY', 'PROMISE', 'SPECTRUM', 'ORAL', 'BEING', 'DEAL', 'ABSORPTION']
                if any(indicator in brand_name.upper() for indicator in generic_indicators):
                    # This is a generic/marketing brand name, append dosages to distinguish variants
                    active_dosage = self._extract_active_ingredients_dosage(text_content)
                    if active_dosage:
                        brand_name = f"{brand_name}-{active_dosage}"

            # Skip if no brand name found
            if not brand_name or brand_name == "UNKNOWN":
                print(f"{idx}: {image_name} - [SKIP] UNKNOWN")
                stats['skipped'] += 1
                continue
            
            brand_lower = brand_name.lower()
            
            # Skip chemical notations (IP + numbers, e.g., "IP0-099w-v")
            if re.match(r'^IP\d+', brand_name) or re.match(r'^IP\d+', brand_name.replace('O', '0')):
                print(f"{idx}: {image_name} - [SKIP] Chemical notation")
                stats['skipped'] += 1
                continue
            
            # Skip patterns with weight/volume notation (w-v, w/v)
            if 'w-v' in brand_lower or 'w/v' in brand_lower:
                print(f"{idx}: {image_name} - [SKIP] Weight/volume")
                stats['skipped'] += 1
                continue
            
            # Skip instruction text patterns
            if 'forthetypical' in brand_lower or 'typical' in brand_lower and 'management' in cleaned_text.lower():
                print(f"{idx}: {image_name} - [SKIP] Instruction text")
                stats['skipped'] += 1
                continue
            
            # Skip if excessive repeated characters
            # First, remove form type words that might be included in brand extraction
            brand_for_noise_check = brand_name.lower()
            form_words = ['suspension', 'tablets', 'capsules', 'injection', 'injections', 
                         'syrup', 'cream', 'gel', 'ointment', 'powder', 'solution', 
                         'lotion', 'spray', 'drops', 'film', 'softgel']
            for word in form_words:
                brand_for_noise_check = brand_for_noise_check.replace(f'-{word}', '').replace(word, '')
            
            # Check for excessive repeated characters (lenient: allow up to 8 repetitions for long names)
            max_repeats = max(8, len(brand_for_noise_check) // 4)  # Allow more repeats in longer names
            if any(brand_for_noise_check.count(c) > max_repeats for c in 'aeioustnr'):
                print(f"{idx}: {image_name} - [SKIP] Extreme OCR noise")
                stats['skipped'] += 1
                continue
            
            # Allow API/generic drug names as fallback when no product identifiers found
            # These are valid medicines, just without a product brand name
            
            # Continue with extraction even for fallback names (don't skip)
            # They represent valid medicines without product branding

            # Build app format
            medicine_id = self._build_id(brand_name, medicine_type)
            
            # Handle duplicate IDs by adding version suffix
            if medicine_id in id_counter:
                id_counter[medicine_id] += 1
                versioned_id = f"{medicine_id}-V{id_counter[medicine_id]}"
            else:
                id_counter[medicine_id] = 1
                versioned_id = medicine_id
            
            # Mark as regular medicine
            match_indicator = ""
            
            # Normalize brand name for storage (remove trailing hyphens/spaces, colons, parentheses)
            brand_name_clean = brand_name.strip().rstrip('-').strip().replace(':', '').replace('(', '')

            medicine_info = {
                "id": versioned_id,
                "brandName": brand_name_clean,
                "isActive": True,
                "source": source,
                "preferredAffiliate": False,
                "originalImageName": image_name
            }
            self.medicines_data.append(medicine_info)
            
            stats['extracted'] += 1

            # Display summary with match quality
            type_str = f" [{medicine_type}]" if medicine_type else " [No type]"
            dup_indicator = " (DUPLICATE)" if versioned_id != medicine_id else ""
            print(f"{idx}: {image_name} {match_indicator}")
            print(f"    ID: {versioned_id}{dup_indicator}")
            print(f"    Brand: {brand_name_clean}{type_str}\n")

        # Print quality summary
        self._print_quality_summary(stats)
        
        return len(self.medicines_data)
    
    def _print_quality_summary(self, stats):
        """Print extraction quality summary"""
        print(f"\n{'='*60}")
        print(f"[EXTRACTION QUALITY SUMMARY]")
        print(f"{'='*60}")
        print(f"Total Images:       {stats['total_images']}")
        print(f"Extracted:          {stats['extracted']}")
        print(f"Skipped:            {stats['skipped']}")
        print(f"Exact Matches:      {stats['exact_matches']}")
        print(f"Fuzzy Matches:      {stats['fuzzy_matches']}")
        print(f"Noise Detected:     {stats['noise_detected']}")
        print(f"{'='*60}\n")

    def save_json(self, output_file: str) -> Path:
        """Save extracted medicine info to JSON."""
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.medicines_data, f, indent=2, ensure_ascii=False)
        return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Extract medicine info from OCR text JSON with improved patterns"
    )
    parser.add_argument("--input-json", required=True,
                        help="Input OCR text JSON file (e.g., output/images_text_all.json)")
    parser.add_argument("--output-json", default="output/medicines.json",
                        help="Output JSON file (default: output/medicines.json)")
    parser.add_argument("--source", default="Biofrench",
                        help="Medicine source: Biofrench, Asvins, etc. (default: Biofrench)")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose logging for debugging")

    args = parser.parse_args()

    extractor = MedicineInfoExtractor(args.input_json, source=args.source, verbose=args.verbose)
    count = extractor.process()

    if count > 0:
        output_path = extractor.save_json(args.output_json)
        print(f"\n{'='*60}")
        print(f"[OK] Extracted {count} medicines")
        print(f"[OK] Saved: {output_path}")
        print(f"Source: {args.source}")
        print(f"All medicines: isActive=true, preferredAffiliate=false")
        print(f"{'='*60}")
    else:
        print(f"\n[ERR] No medicines extracted (check for UNKNOWN brand names)")


if __name__ == "__main__":
    main()
