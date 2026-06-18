#!/usr/bin/env python3
"""Fix source field in medicines.json"""
import json
from pathlib import Path

output_dir = Path("output")
json_path = output_dir / "medicines.json"

if not json_path.exists():
    print("Error: medicines.json not found")
    exit(1)

with open(json_path) as f:
    medicines = json.load(f)

print(f"Total medicines: {len(medicines)}")
print(f"Sample source before: {medicines[0].get('source')}")

# Update all sources to correct one
for med in medicines:
    med["source"] = "Asvins Lifecare Pvt Ltd"

# Save back
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(medicines, f, indent=2, ensure_ascii=False)

print(f"Sample source after: {medicines[0].get('source')}")
print(f"✓ Updated {len(medicines)} medicines with correct source")
