#!/usr/bin/env python3
"""
Medicines Delta Sync & Verification Tool

Compares current medicines.json with extracted medicines, shows diffs, and allows
controlled updates. Consolidates all verification logic in one place.

Usage:
    python medicines_delta_sync.py [--current <path>] [--new <path>] [--apply]

Example:
    python medicines_delta_sync.py --current ../../app/src/main/assets/medicines.json --new output/medicines.json --show
    python medicines_delta_sync.py --current ../../app/src/main/assets/medicines.json --new output/medicines.json --apply
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime


class MedicinesDeltaSync:
    """Compare, verify, and sync medicines.json with extracted data."""

    def __init__(self, current_path: str, new_path: str):
        self.current_path = Path(current_path)
        self.new_path = Path(new_path)
        
        self.current_medicines = self._load_json(self.current_path)
        self.new_medicines = self._load_json(self.new_path)
        
        self.current_ids = {m["id"] for m in self.current_medicines}
        self.new_ids = {m["id"] for m in self.new_medicines}
        
        self.added = self.new_ids - self.current_ids
        self.removed = self.current_ids - self.new_ids
        self.common = self.current_ids & self.new_ids
        
    def _load_json(self, path: Path) -> List[Dict]:
        """Load medicines from JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] File not found: {path}")
            return []
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in {path}: {e}")
            return []

    def verify_integrity(self) -> Dict[str, List[str]]:
        """
        Verify data integrity: duplicates, missing fields, invalid IDs.
        Returns issues dict with severity level.
        """
        issues = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Check current medicines
        current_names = {}
        for med in self.current_medicines:
            if not med.get("id") or not med.get("brandName"):
                issues["errors"].append(f"Current: Missing id/brandName in {med}")
                continue
            
            if med["id"] in current_names:
                issues["errors"].append(f"Current: Duplicate ID '{med['id']}'")
            current_names[med["id"]] = med.get("brandName", "")
        
        # Check new medicines
        new_names = {}
        for med in self.new_medicines:
            if not med.get("id") or not med.get("brandName"):
                issues["errors"].append(f"New: Missing id/brandName in {med}")
                continue
            
            if med["id"] in new_names:
                issues["errors"].append(f"New: Duplicate ID '{med['id']}'")
            new_names[med["id"]] = med.get("brandName", "")
            
            # Validate source
            if med.get("source") != "Asvins Lifecare Pvt Ltd":
                issues["warnings"].append(f"New: '{med['id']}' has incorrect source: '{med.get('source')}'")
        
        return issues

    def show_delta(self) -> None:
        """Display detailed delta comparison."""
        print("\n" + "="*80)
        print("MEDICINES DELTA COMPARISON")
        print("="*80)
        
        # Verify integrity
        issues = self.verify_integrity()
        
        if issues["errors"]:
            print("\n[ERRORS]:")
            for error in issues["errors"]:
                print(f"   [ERROR] {error}")
        
        if issues["warnings"]:
            print("\n[WARNINGS]:")
            for warning in issues["warnings"]:
                print(f"   [WARN] {warning}")
        
        # Summary
        print("\n" + "-"*80)
        print(f"SUMMARY:")
        print(f"  Current medicines: {len(self.current_medicines)}")
        print(f"  New medicines:     {len(self.new_medicines)}")
        print(f"  Added:             {len(self.added):3d}")
        print(f"  Removed:           {len(self.removed):3d}")
        print(f"  Updated/Changed:   {len(self.common):3d}")
        print(f"  Net change:        {len(self.added) - len(self.removed):+3d}")
        print("-"*80)
        
        # Show added medicines
        if self.added:
            print(f"\n[ADDED] ({len(self.added)} medicines):")
            for med_id in sorted(list(self.added))[:10]:
                med = next((m for m in self.new_medicines if m["id"] == med_id), None)
                if med:
                    print(f"   + {med_id:35s} -> {med.get('brandName', 'N/A')}")
            if len(self.added) > 10:
                print(f"   ... and {len(self.added) - 10} more")
        
        # Show removed medicines
        if self.removed:
            print(f"\n[REMOVED] ({len(self.removed)} medicines):")
            for med_id in sorted(list(self.removed))[:10]:
                med = next((m for m in self.current_medicines if m["id"] == med_id), None)
                if med:
                    print(f"   - {med_id:35s} <- {med.get('brandName', 'N/A')}")
            if len(self.removed) > 10:
                print(f"   ... and {len(self.removed) - 10} more")
        
        # Show changed medicines
        if self.common:
            print(f"\n[SYNC] CHECKING UPDATES ON {len(self.common)} COMMON MEDICINES...")
            changed = []
            for med_id in self.common:
                current_med = next((m for m in self.current_medicines if m["id"] == med_id), {})
                new_med = next((m for m in self.new_medicines if m["id"] == med_id), {})
                
                # Check what changed
                changes = []
                if current_med.get("brandName") != new_med.get("brandName"):
                    changes.append(f"name: '{current_med.get('brandName')}' -> '{new_med.get('brandName')}'")
                if current_med.get("source") != new_med.get("source"):
                    changes.append(f"source: '{current_med.get('source')}' -> '{new_med.get('source')}'")
                if current_med.get("isActive") != new_med.get("isActive"):
                    changes.append(f"active: {current_med.get('isActive')} -> {new_med.get('isActive')}")
                
                if changes:
                    changed.append((med_id, changes))
            
            if changed:
                print(f"   {len(changed)} medicines have changes:")
                for med_id, changes in changed[:5]:
                    print(f"   [SYNC] {med_id:35s}")
                    for change in changes:
                        print(f"      ? {change}")
                if len(changed) > 5:
                    print(f"   ... and {len(changed) - 5} more")
            else:
                print(f"   [OK] All {len(self.common)} common medicines are identical")
        
        print("\n" + "="*80)
        print(f"Comparison at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")

    def apply_sync(self, backup: bool = True) -> bool:
        """
        Apply changes: merge new medicines into current, backup old file.
        Returns True if successful.
        """
        try:
            # Create backup
            if backup and self.current_path.exists():
                backup_path = self.current_path.with_suffix('.json.bak')
                with open(self.current_path, 'r', encoding='utf-8') as f:
                    backup_data = f.read()
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(backup_data)
                print(f"[OK] Backup created: {backup_path.name}")
            
            # Write updated medicines
            with open(self.current_path, 'w', encoding='utf-8') as f:
                json.dump(self.new_medicines, f, indent=2, ensure_ascii=False)
            
            print(f"[OK] Updated {self.current_path.name} ({len(self.new_medicines)} medicines)")
            print(f"  ? Added:   {len(self.added)}")
            print(f"  ? Removed: {len(self.removed)}")
            print(f"  ? Updated: {sum(1 for m in self.new_medicines if m['id'] in self.common)}")
            
            return True
        except Exception as e:
            print(f"[ERROR] Sync failed: {e}")
            return False

    def export_summary(self, output_path: str = "delta_summary.json") -> None:
        """Export delta summary as JSON for review."""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "current_count": len(self.current_medicines),
            "new_count": len(self.new_medicines),
            "added": list(sorted(self.added)),
            "removed": list(sorted(self.removed)),
            "added_count": len(self.added),
            "removed_count": len(self.removed),
            "integrity_issues": self.verify_integrity()
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            print(f"[OK] Summary exported to: {output_path}")
        except Exception as e:
            print(f"[ERROR] Export failed: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Compare and sync medicines.json with extracted data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show delta without applying
  python medicines_delta_sync.py --current app.json --new extracted.json --show
  
  # Apply changes with backup
  python medicines_delta_sync.py --current app.json --new extracted.json --apply
  
  # Export summary for review
  python medicines_delta_sync.py --current app.json --new extracted.json --export
        """
    )
    
    parser.add_argument("--current", type=str, required=True,
                       help="Path to current medicines.json (in app)")
    parser.add_argument("--new", type=str, required=True,
                       help="Path to newly extracted medicines.json (from converter)")
    parser.add_argument("--show", action="store_true",
                       help="Show delta comparison (default)")
    parser.add_argument("--apply", action="store_true",
                       help="Apply changes to current medicines.json (creates backup)")
    parser.add_argument("--export", action="store_true",
                       help="Export summary to JSON for review")
    parser.add_argument("--no-backup", action="store_true",
                       help="Don't create backup when applying (dangerous!)")
    
    args = parser.parse_args()
    
    syncer = MedicinesDeltaSync(args.current, args.new)
    
    # Always show delta first
    syncer.show_delta()
    
    # Check for errors before allowing apply
    issues = syncer.verify_integrity()
    if issues["errors"]:
        print("[WARN] CANNOT APPLY: Integrity errors found above. Fix them first.")
        return
    
    if args.apply:
        print("Applying changes...")
        if syncer.apply_sync(backup=not args.no_backup):
            print("[OK] Sync completed successfully!")
            syncer.export_summary()
        else:
            print("[ERROR] Sync failed!")
    elif args.export:
        syncer.export_summary()
    else:
        print("(Use --apply to update, --export to save summary)")


if __name__ == "__main__":
    main()
