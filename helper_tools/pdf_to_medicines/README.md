# Medicine Extraction & Update (Simple Workflow)

## Quick Start

```bash
# 1. Extract medicines from PDF
python pdf_to_medicines_converter.py ../MEDICINES.pdf --source "Asvins Lifecare Pvt Ltd"

# 2. Review changes
python medicines_delta_sync.py \
  --current ../../app/src/main/assets/medicines.json \
  --new output/medicines.json \
  --show

# 3. Apply (if approved)
python medicines_delta_sync.py \
  --current ../../app/src/main/assets/medicines.json \
  --new output/medicines.json \
  --apply
```

---

## What Each Script Does

### **pdf_to_medicines_converter.py**
Extracts medicines from PDF.

- Renders each page as image
- Extracts brand name via OCR
- Saves images + medicines.json

**Output:**
- `output/medicines.json` - All medicines (id, name, source, etc.)
- `output/images/` - All images as JPG files

---

### **medicines_delta_sync.py**
Compares extracted medicines with current app data.

Shows:
- ✅ What medicines were added
- ❌ What medicines were removed
- 🔄 What medicines changed
- ⚠️ Any data errors

Then applies changes with automatic backup.

---

## Complete Workflow

### Step 1: Extract (takes 10-30 minutes)
```bash
python pdf_to_medicines_converter.py ../MEDICINES.pdf --source "Asvins Lifecare Pvt Ltd" --dpi 150
```

Output: `output/medicines.json` (335 medicines) + `output/images/` (335 JPG files)

### Step 2: Review (safe, read-only)
```bash
python medicines_delta_sync.py \
  --current ../../app/src/main/assets/medicines.json \
  --new output/medicines.json \
  --show
```

Shows you exactly what will change. **Does NOT modify anything.**

Output example:
```
SUMMARY:
  Current medicines: 270
  New medicines:     335
  Added:              100
  Removed:             35
  Updated:             170

✅ ADDED (100 medicines):
   + MEDICINE-001 → Medicine Name
   + MEDICINE-002 → Another Medicine
   ...

❌ REMOVED (35 medicines):
   - OLD-MEDICINE-001 ← Old Name
   ...
```

### Step 3: Apply (with backup)
```bash
python medicines_delta_sync.py \
  --current ../../app/src/main/assets/medicines.json \
  --new output/medicines.json \
  --apply
```

Actions:
1. Creates backup: `medicines.json.bak`
2. Updates: `medicines.json` with 335 medicines
3. Reports: What was added/removed/changed

### Step 4: Copy Images to App
```bash
copy output\images\* ..\..\app\src\main\assets\images\
```

### Step 5: Build & Test
```bash
gradlew assembleBiofrenchRelease assembleAsvinsRelease
```

---

## Image Naming

**Format:** `{BrandName}.jpg` (NO "-1" suffix)

Examples:
- ✓ `ASVINS-DGM.jpg`
- ✓ `ALSIFEN-120.jpg`
- ✓ `biodac.png`

---

## Troubleshooting

**Q: Extraction is slow**
A: Run with lower DPI: `--dpi 150` instead of 200

**Q: Some brand names look wrong**
A: OCR can fail on blurry pages. Review `--show` output and decide if acceptable.

**Q: Can I see the changes before applying?**
A: Yes! Always run `--show` first to review.

**Q: How do I undo changes?**
A: Restore from backup: `copy medicines.json.bak medicines.json`

---

## That's it!

Two scripts, simple workflow, user review built-in. No confusion.
