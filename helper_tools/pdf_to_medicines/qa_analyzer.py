#!/usr/bin/env python3
"""
QA Analyzer - Identify problematic brand name extractions
"""
import json
from pathlib import Path

output_dir = Path("output")
json_path = output_dir / "medicines.json"

if not json_path.exists():
    print("Error: output/medicines.json not found. Run converter first.")
    exit(1)

with open(json_path) as f:
    medicines = json.load(f)

issues = {
    "fallback_ids": [],           # med### instead of extracted names
    "short_names": [],            # < 5 chars
    "likely_descriptors": [],     # marketing/medical text
    "suspicious_names": [],       # names with patterns suggesting OCR errors
    "duplicates": [],             # same name on multiple pages
}

name_counts = {}
for med in medicines:
    name = med["brandName"]
    
    # Track duplicates
    if name in name_counts:
        name_counts[name].append(med["id"])
    else:
        name_counts[name] = [med["id"]]
    
    # Fallback IDs
    if med["id"].startswith("med"):
        issues["fallback_ids"].append((med["id"], med["brandName"]))
    
    # Short names (likely fragments)
    if len(med["brandName"]) < 5 and not med["id"].startswith("med"):
        issues["short_names"].append((med["id"], med["brandName"]))
    
    # Likely descriptors
    descriptors = [
        "efficacy", "proven", "action", "tablet", "manufactured",
        "promise", "life", "blood", "pressure", "release", "therapy",
        "control", "secretion", "cells", "sugar", "from", "power",
        "heart", "bones", "cholecalciferol"
    ]
    if any(desc in med["brandName"].lower() for desc in descriptors):
        issues["likely_descriptors"].append((med["id"], med["brandName"]))
    
    # Suspicious patterns
    if med["brandName"].count(" ") > 3 or med["brandName"].startswith("Manufactured"):
        issues["suspicious_names"].append((med["id"], med["brandName"]))

# Find duplicates
for name, ids in name_counts.items():
    if len(ids) > 1:
        issues["duplicates"].append((name, ids))

# Print report
print("\n" + "="*70)
print("QA ANALYSIS REPORT")
print("="*70)

print(f"\nFALLBACK IDs (should extract names): {len(issues['fallback_ids'])}")
for mid, name in issues["fallback_ids"][:10]:
    print(f"  {mid} -> '{name}'")
if len(issues["fallback_ids"]) > 10:
    print(f"  ... and {len(issues['fallback_ids']) - 10} more")

print(f"\nSHORT NAMES (likely fragments): {len(issues['short_names'])}")
for mid, name in issues["short_names"][:10]:
    print(f"  {mid} -> '{name}'")

print(f"\nLIKELY DESCRIPTORS (marketing/medical text): {len(issues['likely_descriptors'])}")
for mid, name in issues["likely_descriptors"][:10]:
    print(f"  {mid} -> '{name}'")

print(f"\nSUSPICIOUS PATTERNS (multi-word or odd): {len(issues['suspicious_names'])}")
for mid, name in issues["suspicious_names"][:10]:
    print(f"  {mid} -> '{name}'")

print(f"\nDUPLICATE NAMES: {len(issues['duplicates'])}")
for name, ids in issues["duplicates"][:5]:
    print(f"  '{name}' -> {ids}")

print(f"\n{'='*70}")
print(f"TOTAL ISSUES: {sum(len(v) for v in issues.values())}")
print(f"TOTAL MEDICINES: {len(medicines)}")
print(f"{'='*70}\n")
