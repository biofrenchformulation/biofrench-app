#!/usr/bin/env python3
"""
Standalone validation tool for medicines.json
Runs validation and generates validation_report.json
"""

import json
import sys
from pathlib import Path
imagefrom typing import Dict, List


def validate_medicines(json_path: str, output_dir: str = None) -> bool:
    """Validate medicines.json and generate report."""
    
    json_path = Path(json_path)
    if not json_path.exists():
        print(f"Error: File not found: {json_path}")
        return False
    
    if output_dir is None:
        output_dir = json_path.parent
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            medicines = json.load(f)
    except Exception as e:
        print(f"Error: Could not load JSON: {e}")
        return False
    
    if not isinstance(medicines, list):
        print("Error: JSON must be an array of medicines")
        return False
    
    print(f"\nValidating {len(medicines)} medicines from {json_path}...\n")
    
    # Run validation checks
    issues = {
        "duplicates": [],
        "missing_type": [],
        "suspicious_name": [],
        "bad_id": [],
        "warnings": []
    }
    
    seen_ids = set()
    
    for med in medicines:
        med_id = med.get("id", "")
        brand = med.get("brandName", "")
        
        # Check for duplicates
        if med_id in seen_ids:
            issues["duplicates"].append(med_id)
        seen_ids.add(med_id)
        
        # Check for missing medicine type
        if not med_id.endswith(("-TAB", "-TABS", "-CAP", "-CAPS", "-SYR", "-INJ", 
                                "-CRM", "-GEL", "-DRP", "-OIN", "-PWD", "-SUS", 
                                "-SGC", "-SPR", "-LIQ", "-SOL")):
            issues["missing_type"].append(med_id)
        
        # Check for suspicious brand names
        if len(brand) < 2:
            issues["suspicious_name"].append((med_id, brand, "Too short"))
        elif len(brand) > 80:
            issues["suspicious_name"].append((med_id, brand, "Too long (>80 chars)"))
        elif not any(c.isalnum() for c in brand):
            issues["suspicious_name"].append((med_id, brand, "No alphanumeric chars"))
        elif brand.count("-") > 3:
            issues["suspicious_name"].append((med_id, brand, "Too many hyphens (>3)"))
        
        # Check for bad ID format
        if len(med_id) < 2:
            issues["bad_id"].append((med_id, "Too short"))
        elif len(med_id) > 100:
            issues["bad_id"].append((med_id, "Too long (>100 chars)"))
        elif med_id.startswith("-") or med_id.endswith("-"):
            issues["bad_id"].append((med_id, "Starts or ends with hyphen"))
    
    # Generate report
    print(f"{'='*60}")
    print("VALIDATION REPORT")
    print(f"{'='*60}")
    
    critical_issues = len(set(issues["duplicates"])) + len(issues["bad_id"])
    total_issues = sum(len(v) if isinstance(v, list) else 0 for v in issues.values())
    
    validation_ok = True
    
    if total_issues == 0:
        print("✅ VALIDATION PASSED - All medicines are valid!")
    else:
        print(f"⚠️  Found {total_issues} issue(s):\n")
        validation_ok = critical_issues == 0
        
        if issues["duplicates"]:
            print(f"❌ DUPLICATES ({len(set(issues['duplicates']))}): CRITICAL")
            for dup_id in set(issues["duplicates"]):
                print(f"   {dup_id}")
        
        if issues["bad_id"]:
            print(f"\n❌ BAD ID FORMAT ({len(issues['bad_id'])}): CRITICAL")
            for bad_id, reason in issues["bad_id"]:
                print(f"   {bad_id}: {reason}")
        
        if issues["missing_type"]:
            print(f"\n❌ MISSING MEDICINE TYPE ({len(issues['missing_type'])}): WARNING")
            for med_id in issues["missing_type"][:10]:
                print(f"   {med_id}")
            if len(issues["missing_type"]) > 10:
                print(f"   ... and {len(issues['missing_type']) - 10} more")
        
        if issues["suspicious_name"]:
            print(f"\n⚠️  SUSPICIOUS NAMES ({len(issues['suspicious_name'])}): WARNING")
            for med_id, brand, reason in issues["suspicious_name"][:10]:
                print(f"   {med_id}: '{brand}' ({reason})")
            if len(issues["suspicious_name"]) > 10:
                print(f"   ... and {len(issues['suspicious_name']) - 10} more")
    
    print(f"\n{'='*60}")
    print("SUMMARY:")
    print(f"  Total medicines: {len(medicines)}")
    print(f"  Duplicates: {len(set(issues['duplicates']))}")
    print(f"  Bad ID format: {len(issues['bad_id'])}")
    print(f"  Missing type: {len(issues['missing_type'])}")
    print(f"  Suspicious names: {len(issues['suspicious_name'])}")
    print(f"{'='*60}\n")
    
    if critical_issues > 0:
        print(f"❌ VALIDATION FAILED ({critical_issues} critical issue(s))")
        print("   Fix duplicates and bad IDs before proceeding.\n")
    else:
        print("✅ OK to proceed (warnings are non-critical)\n")
    
    # Save report
    report_path = output_dir / "validation_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(issues, f, indent=2)
    print(f"✓ Report saved: {report_path}")
    
    return validation_ok


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate medicines.json")
    parser.add_argument("--json-path", required=True, help="Path to medicines.json to validate")
    parser.add_argument("--output-dir", help="Output directory for validation_report.json (default: same as json-path)")
    
    args = parser.parse_args()
    
    validation_ok = validate_medicines(args.json_path, args.output_dir)
    sys.exit(0 if validation_ok else 1)


if __name__ == "__main__":
    main()
