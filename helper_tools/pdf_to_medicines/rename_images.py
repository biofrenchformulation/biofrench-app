#!/usr/bin/env python3
"""
Manual Image Rename Utility

Renames extracted images based on medicines.json after validation fixes.

Usage:
    python rename_images.py --json-path medicines.json --images-dir output/images

Example:
    python rename_images.py --json-path output/medicines.json --images-dir output/images
"""

import argparse
import json
import sys
from pathlib import Path


def rename_images(json_path: str, images_dir: str, cleanup_json: bool = False) -> bool:
    """
    Rename images from med001.jpg to final {id}.jpg format based on medicines.json.
    
    Uses explicit mapping: each medicine entry has 'originalImageName' field
    that identifies which image file to rename (med001.jpg, med002.jpg, etc.)
    
    This allows manual reordering of medicines.json without breaking the mapping.
    
    Args:
        json_path: Path to medicines.json (contains originalImageName for each entry)
        images_dir: Directory containing images (med001.jpg, etc.)
        cleanup_json: If True, remove 'originalImageName' field from JSON after rename
    
    Returns:
        True if successful, False otherwise
    """
    json_path = Path(json_path)
    images_dir = Path(images_dir)

    # Load medicines.json
    if not json_path.exists():
        print(f"❌ Error: medicines.json not found: {json_path}")
        return False

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            medicines = json.load(f)
    except Exception as e:
        print(f"❌ Error loading medicines.json: {e}")
        return False

    if not isinstance(medicines, list):
        print(f"❌ Error: medicines.json must contain a list, not {type(medicines).__name__}")
        return False

    # Get all images for validation
    all_images = sorted(images_dir.glob("med*.jpg")) + sorted(images_dir.glob("med*.png"))

    # Check if cleanup-only mode (no images to rename, just clean JSON)
    if not all_images and cleanup_json:
        print("ℹ️  No med*.jpg images found (already renamed?)")
        print("Running in CLEANUP-ONLY mode to remove originalImageName field...\n")
        
        # Cleanup JSON if requested
        print("Cleaning up JSON (removing originalImageName field)...\n")
        for medicine in medicines:
            if "originalImageName" in medicine:
                del medicine["originalImageName"]
        
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(medicines, f, indent=2, ensure_ascii=False)
            print(f"✓ JSON cleaned: {json_path}\n")
            return True
        except Exception as e:
            print(f"❌ Error: Could not clean JSON: {e}\n")
            return False
    
    if not all_images:
        print(f"❌ Error: No images found in {images_dir}")
        return False

    print(f"Found {len(all_images)} images in {images_dir}")
    print(f"Renaming based on medicines.json mappings...\n")

    # Rename images using explicit mapping
    renamed_count = 0
    errors = []
    skipped = []

    for medicine in medicines:
        if "id" not in medicine:
            errors.append("Medicine entry missing 'id' field")
            continue
        
        if "originalImageName" not in medicine:
            errors.append(f"{medicine['id']}: Missing 'originalImageName' field")
            continue
        
        original_name = medicine["originalImageName"]
        old_path = images_dir / original_name
        
        if not old_path.exists():
            errors.append(f"{medicine['id']}: Original image not found: {original_name}")
            continue
        
        final_id = medicine["id"]
        new_name = f"{final_id}{old_path.suffix}"
        new_path = images_dir / new_name
        
        try:
            # Handle existing file
            if new_path.exists():
                print(f"  ⚠️  {original_name} → {new_name} (exists, skipping)")
                skipped.append(new_name)
                continue
            
            # Rename
            old_path.rename(new_path)
            print(f"  ✅ {original_name} → {new_name}")
            renamed_count += 1
        
        except Exception as e:
            errors.append(f"Error renaming {original_name}: {e}")
            print(f"  ❌ {original_name} → ERROR: {e}")

    # Summary
    print(f"\n{'='*60}")
    print(f"RENAME SUMMARY")
    print(f"{'='*60}")
    print(f"  Total medicines: {len(medicines)}")
    print(f"  Renamed: {renamed_count}")
    print(f"  Skipped: {len(skipped)}")
    if errors:
        print(f"  Errors: {len(errors)}")
        for error in errors:
            print(f"    - {error}")
    print(f"{'='*60}\n")

    # Cleanup JSON if requested
    if cleanup_json and len(errors) == 0:
        print("Cleaning up JSON (removing originalImageName field)...\n")
        for medicine in medicines:
            if "originalImageName" in medicine:
                del medicine["originalImageName"]
        
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(medicines, f, indent=2, ensure_ascii=False)
            print(f"✓ JSON cleaned: {json_path}\n")
        except Exception as e:
            print(f"⚠️  Warning: Could not clean JSON: {e}\n")

    return len(errors) == 0


def main():
    parser = argparse.ArgumentParser(
        description="Manually rename extracted images based on medicines.json"
    )
    parser.add_argument(
        "--json-path",
        default="output/medicines.json",
        help="Path to medicines.json (default: output/medicines.json)"
    )
    parser.add_argument(
        "--images-dir",
        default="output/images",
        help="Directory with images to rename (default: output/images)"
    )
    parser.add_argument(
        "--cleanup-json",
        action="store_true",
        help="Remove 'originalImageName' field from JSON after successful rename"
    )

    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("MANUAL IMAGE RENAME")
    print(f"{'='*60}\n")

    success = rename_images(args.json_path, args.images_dir, cleanup_json=args.cleanup_json)

    if success:
        print("✅ Rename completed successfully!")
        return 0
    else:
        print("❌ Rename completed with errors.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
