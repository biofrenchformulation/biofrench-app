#!/usr/bin/env python3
"""
Finalize Sync - Rename Images & Update JSON (Step 5 of 5)

After delta review and approval, this script:
1. Renames extracted images to final IDs
2. Copies to app assets directory
3. Updates medicines.json in app
4. Creates backup

Usage:
    python finalize_sync.py \
      --approved-json <path> \
      --extracted-images <dir> \
      --app-images <dir> \
      --app-json <path>

Example:
    python finalize_sync.py \
      --approved-json output/approved_medicines.json \
      --extracted-images output/images \
      --app-images ../../app/src/main/assets/images \
      --app-json ../../app/src/main/assets/medicines.json
"""

import argparse
import json
import shutil
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class FinalizeSync:
    """Finalize sync: rename images and update app JSON."""

    def __init__(self, approved_json: str, extracted_images: str,
                 app_images: str, app_json: str):
        self.approved_json = Path(approved_json)
        self.extracted_images = Path(extracted_images)
        self.app_images = Path(app_images)
        self.app_json = Path(app_json)

        # Validate inputs
        if not self.approved_json.exists():
            raise FileNotFoundError(f"Approved JSON not found: {self.approved_json}")
        if not self.extracted_images.exists():
            raise FileNotFoundError(f"Extracted images dir not found: {self.extracted_images}")
        if not self.app_json.exists():
            raise FileNotFoundError(f"App JSON not found: {self.app_json}")

        self.app_images.mkdir(parents=True, exist_ok=True)

    def execute(self) -> bool:
        """Execute final sync: rename images and update JSON."""
        print(f"\n{'='*70}")
        print("FINALIZING SYNC: Rename Images & Update JSON")
        print(f"{'='*70}\n")

        # Load approved medicines
        with open(self.approved_json, 'r', encoding='utf-8') as f:
            medicines = json.load(f)

        print(f"Processing {len(medicines)} approved medicines...")

        # Map old sequential names to final IDs
        renamed_count = 0
        copy_count = 0
        failed = []

        # Load old extracted images (to find med001.jpg, med002.jpg, etc.)
        extracted_files = list(self.extracted_images.glob("med*.jpg"))
        extracted_files.sort()

        for idx, med in enumerate(medicines):
            try:
                final_id = med.get("id", "")
                if not final_id:
                    failed.append(f"Missing ID in {med}")
                    continue

                # Find corresponding extracted image (med001.jpg → FINAL-ID.jpg)
                if idx < len(extracted_files):
                    source_file = extracted_files[idx]
                    final_filename = f"{final_id}.jpg"
                    dest_file = self.app_images / final_filename

                    # Copy and rename
                    shutil.copy2(source_file, dest_file)
                    copy_count += 1
                    print(f"  ✓ {source_file.name} → {final_filename}")

            except Exception as e:
                failed.append(f"{med.get('id', 'unknown')}: {str(e)}")
                print(f"  ❌ {med.get('id', 'unknown')}: {str(e)}")

        print(f"\n{copy_count} images renamed and copied to app")

        if failed:
            print(f"\n⚠️  {len(failed)} errors:")
            for error in failed:
                print(f"  - {error}")
            return False

        # Create backup of app JSON
        backup_path = self.app_json.with_suffix(".json.bak")
        backup_path.write_text(self.app_json.read_text(encoding='utf-8'), encoding='utf-8')
        print(f"\n✓ Backup created: {backup_path.name}")

        # Update app JSON
        with open(self.app_json, 'w', encoding='utf-8') as f:
            json.dump(medicines, f, indent=2, ensure_ascii=False)

        print(f"✓ Updated: {self.app_json.name}")
        print(f"  Total medicines: {len(medicines)}")

        print(f"\n{'='*70}")
        print("✓ SYNC COMPLETE!")
        print(f"{'='*70}")
        print(f"\nNext steps:")
        print(f"  1. Verify files in: {self.app_images.name}/")
        print(f"  2. Review: {self.app_json.name}")
        print(f"  3. Build and test the app")
        print(f"  4. If issues, restore backup: cp {backup_path.name} {self.app_json.name}")

        return True


def main():
    parser = argparse.ArgumentParser(description="Finalize sync (Step 5)")
    parser.add_argument("--approved-json", required=True,
                       help="Approved medicines.json")
    parser.add_argument("--extracted-images", required=True,
                       help="Directory with extracted images")
    parser.add_argument("--app-images", required=True,
                       help="App assets images directory")
    parser.add_argument("--app-json", required=True,
                       help="App medicines.json path")
    parser.add_argument("--no-backup", action="store_true",
                       help="Don't create backup (dangerous!)")

    args = parser.parse_args()

    try:
        syncer = FinalizeSync(
            approved_json=args.approved_json,
            extracted_images=args.extracted_images,
            app_images=args.app_images,
            app_json=args.app_json
        )
        if syncer.execute():
            print(f"\n✓ Step 5 complete!")
        else:
            print(f"\n❌ Step 5 failed with errors")
            exit(1)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
