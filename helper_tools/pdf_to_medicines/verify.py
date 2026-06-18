#!/usr/bin/env python3
"""Verify medicines.json is correct"""
import json
from pathlib import Path

output_dir = Path("output")
json_path = output_dir / "medicines.json"

with open(json_path) as f:
    medicines = json.load(f)

print(f"✓ Total medicines: {len(medicines)}")
print(f"\nSample medicines:")
for med in medicines[:3]:
    print(f"  {med['id']}: {med['brandName']}")
    print(f"    Source: {med['source']}")
    print(f"    Active: {med['isActive']}")

# Verify all have correct source
sources = set(med['source'] for med in medicines)
print(f"\nUnique sources: {sources}")

if sources == {"Asvins Lifecare Pvt Ltd"}:
    print("✓ All medicines have correct source")
else:
    print("⚠ Warning: Found unexpected sources:", sources)
