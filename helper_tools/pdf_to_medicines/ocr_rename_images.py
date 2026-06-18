#!/usr/bin/env python3
"""
OCR-rename medicine images and optionally sync medicines.json IDs.

Usage:
  python ocr_rename_images.py --images-dir <dir> [--json <medicines.json>] [--apply]

Notes:
- Dry-run by default.
- Uses OCR logic from pdf_to_medicines_converter.py for consistent naming behavior.
- On apply, creates backup files before modifications.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image

import pdf_to_medicines_converter as conv

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".svg", ".webp"}
GENERIC_ONLY = {
    "AKUMS",
    "ASVINS",
    "ASVINS-LIFECARE",
    "LIFECARE",
    "TABLETS",
    "CAPSULE",
    "CAPSULES",
    "SYRUP",
    "BENEFITS",
    "MANUFACTURED-BY",
}


def norm_key(text: str) -> str:
    return "".join(ch for ch in text.upper() if ch.isalnum())


@dataclass
class RenameRow:
    old_name: str
    new_name: str
    ocr_name: str
    status: str
    reason: str = ""


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_ocr_engine() -> object:
    """
    Build a PDFMedicinesExtractor instance without running __init__,
    so we can reuse OCR methods for image files.
    """
    if not conv.OCR_AVAILABLE:
        raise RuntimeError("pytesseract is not available. Install pytesseract + Tesseract OCR.")

    engine = object.__new__(conv.PDFMedicinesExtractor)
    return engine


def ocr_name_from_image(engine: object, image_path: Path) -> Optional[str]:
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            name = engine._extract_brand_name(img)
            if not name:
                return None
            return conv.PDFMedicinesExtractor._sanitize_id(name)
    except Exception:
        return None


def normalize_name_candidate(raw: str) -> Optional[str]:
    """Normalize OCR/current filename text to a medicine-like ID."""
    if not raw:
        return None

    s = conv.PDFMedicinesExtractor._sanitize_id(raw).upper()
    s = s.replace("_", " ")
    s = " ".join(s.split())

    # Remove common leading page-number artifact (e.g., "27 ").
    s = s.lstrip()
    parts = s.split(" ")
    if parts and parts[0].isdigit() and len(parts[0]) <= 2:
        s = " ".join(parts[1:]).strip()

    # Strip manufacturer/company prefixes.
    for prefix in ["AKUMS ", "AKUMS-", "ASVINS LIFECARE ", "ASVINS-LIFECARE "]:
        if s.startswith(prefix):
            s = s[len(prefix):].strip()

    # Normalize separators to hyphen-style IDs.
    s = s.replace(" ", "-")
    while "--" in s:
        s = s.replace("--", "-")
    s = s.strip("-")

    if not s or s in GENERIC_ONLY:
        return None

    # Reject obvious junk
    if s.isdigit() or len(s) < 4:
        return None
    if s in {"AS", "OF", "NS", "BY", "FOR", "WITH"}:
        return None

    return s


def build_json_matcher(json_path: Optional[Path]) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Build normalized lookup maps from medicines.json:
    - id_norm -> id
    - brand_norm -> id (first occurrence wins)
    """
    if not json_path or not json_path.exists():
        return {}, {}

    with json_path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    id_map: Dict[str, str] = {}
    brand_map: Dict[str, str] = {}
    for row in data:
        if not isinstance(row, dict):
            continue
        med_id = row.get("id")
        brand = row.get("brandName")
        if isinstance(med_id, str) and med_id.strip():
            id_map.setdefault(norm_key(med_id), med_id)
        if isinstance(brand, str) and brand.strip() and isinstance(med_id, str) and med_id.strip():
            brand_map.setdefault(norm_key(brand), med_id)

    return id_map, brand_map


def map_candidate_to_id(candidate: str, id_map: Dict[str, str], brand_map: Dict[str, str]) -> Optional[str]:
    """Map OCR candidate to a valid medicines.json ID."""
    if not candidate:
        return None

    nk = norm_key(candidate)
    if not nk:
        return None

    if nk in id_map:
        return id_map[nk]
    if nk in brand_map:
        return brand_map[nk]

    # Fuzzy fallback against known brand keys
    keys = list(brand_map.keys())
    if keys:
        match = difflib.get_close_matches(nk, keys, n=1, cutoff=0.86)
        if match:
            return brand_map[match[0]]

    # Fuzzy fallback against known id keys
    id_keys = list(id_map.keys())
    if id_keys:
        match = difflib.get_close_matches(nk, id_keys, n=1, cutoff=0.90)
        if match:
            return id_map[match[0]]

    return None


def collect_plan(images_dir: Path, json_path: Optional[Path] = None) -> Tuple[List[RenameRow], Dict[str, str]]:
    engine = build_ocr_engine()
    rows: List[RenameRow] = []
    rename_map: Dict[str, str] = {}
    id_map, brand_map = build_json_matcher(json_path)

    files = sorted([p for p in images_dir.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS])

    reserved_targets = set()

    for p in files:
        ocr_raw = ocr_name_from_image(engine, p)
        ocr_name = normalize_name_candidate(ocr_raw) if ocr_raw else None
        if not ocr_name:
            rows.append(RenameRow(p.name, p.name, ocr_raw or "", "skipped", "ocr-empty-or-generic"))
            continue

        # If JSON is available, force mapping to known medicine IDs only.
        if id_map or brand_map:
            mapped = map_candidate_to_id(ocr_name, id_map, brand_map)
            if not mapped:
                rows.append(RenameRow(p.name, p.name, ocr_name, "skipped", "no-json-id-match"))
                continue
            target_stem = mapped
        else:
            target_stem = ocr_name

        new_name = f"{target_stem}{p.suffix.lower()}"
        target = images_dir / new_name

        if p.name == new_name:
            rows.append(RenameRow(p.name, p.name, ocr_name, "unchanged", "already-correct"))
            continue

        # Conflict if two files want same target in one batch
        if new_name in reserved_targets:
            rows.append(RenameRow(p.name, new_name, ocr_name, "conflict", "batch-target-duplicate"))
            continue

        if target.exists() and target.resolve() != p.resolve():
            # If content is identical, we can safely mark duplicate and skip rename.
            try:
                if file_hash(target) == file_hash(p):
                    rows.append(RenameRow(p.name, new_name, ocr_name, "duplicate", "target-exists-same-content"))
                else:
                    rows.append(RenameRow(p.name, new_name, ocr_name, "conflict", "target-exists-different-content"))
                continue
            except Exception:
                rows.append(RenameRow(p.name, new_name, ocr_name, "conflict", "target-exists-unreadable"))
                continue

        reserved_targets.add(new_name)
        rows.append(RenameRow(p.name, new_name, ocr_name, "rename", ""))
        rename_map[p.stem] = target_stem

    return rows, rename_map


def apply_renames(images_dir: Path, rows: List[RenameRow]) -> int:
    renamed = 0
    for r in rows:
        if r.status != "rename":
            continue
        src = images_dir / r.old_name
        dst = images_dir / r.new_name
        if src.exists() and not dst.exists():
            src.rename(dst)
            renamed += 1
    return renamed


def update_json_ids(json_path: Path, rename_map: Dict[str, str]) -> Tuple[int, int]:
    with json_path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    existing = {m.get("id") for m in data if isinstance(m, dict)}
    updated = 0
    skipped_collision = 0

    for m in data:
        if not isinstance(m, dict):
            continue
        old_id = m.get("id")
        if not isinstance(old_id, str):
            continue
        new_id = rename_map.get(old_id)
        if not new_id or new_id == old_id:
            continue

        if new_id in existing:
            skipped_collision += 1
            continue

        existing.discard(old_id)
        existing.add(new_id)
        m["id"] = new_id
        updated += 1

    with json_path.open("w", encoding="utf-8-sig") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return updated, skipped_collision


def write_report(report_path: Path, rows: List[RenameRow]) -> None:
    with report_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["old_name", "new_name", "ocr_name", "status", "reason"])
        for r in rows:
            w.writerow([r.old_name, r.new_name, r.ocr_name, r.status, r.reason])


def main() -> int:
    parser = argparse.ArgumentParser(description="OCR rename images and optionally sync medicines.json")
    parser.add_argument("--images-dir", required=True, help="Path to app/src/main/assets/images")
    parser.add_argument("--json", help="Optional path to medicines.json to sync IDs")
    parser.add_argument("--apply", action="store_true", help="Apply changes. Default is dry-run")
    parser.add_argument("--report", default="ocr_image_rename_report.csv", help="CSV report output path")
    args = parser.parse_args()

    images_dir = Path(args.images_dir)
    if not images_dir.exists() or not images_dir.is_dir():
        print(f"Error: images dir not found: {images_dir}")
        return 1

    report_path = Path(args.report)

    json_path = Path(args.json) if args.json else None
    rows, rename_map = collect_plan(images_dir, json_path)
    write_report(report_path, rows)

    plan_total = len(rows)
    plan_rename = sum(1 for r in rows if r.status == "rename")
    plan_conflict = sum(1 for r in rows if r.status == "conflict")
    plan_duplicate = sum(1 for r in rows if r.status == "duplicate")
    plan_skipped = sum(1 for r in rows if r.status == "skipped")
    plan_unchanged = sum(1 for r in rows if r.status == "unchanged")

    print(f"Scanned images: {plan_total}")
    print(f"Planned renames: {plan_rename}")
    print(f"Unchanged: {plan_unchanged}")
    print(f"Skipped (ocr-empty): {plan_skipped}")
    print(f"Conflicts: {plan_conflict}")
    print(f"Duplicates (same content target exists): {plan_duplicate}")
    print(f"Report: {report_path}")

    if not args.apply:
        print("Dry-run only. Re-run with --apply to execute.")
        return 0

    # Apply phase
    renamed = apply_renames(images_dir, rows)
    print(f"Applied renames: {renamed}")

    if args.json:
        json_path = Path(args.json)
        if not json_path.exists():
            print(f"Warning: JSON not found, skipping JSON sync: {json_path}")
            return 0

        backup = json_path.with_suffix(json_path.suffix + ".ocr-rename.bak")
        shutil.copy2(json_path, backup)
        updated, skipped_collision = update_json_ids(json_path, rename_map)
        print(f"JSON backup: {backup}")
        print(f"JSON IDs updated: {updated}")
        print(f"JSON updates skipped due collisions: {skipped_collision}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
