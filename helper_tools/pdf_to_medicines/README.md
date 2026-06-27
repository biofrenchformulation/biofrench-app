# Medicine Extraction & Update (5-Step Workflow)

## Quick Start

### Step 1: Extract Images from PDF
```bash
python pdf_to_images.py ../MEDICINES.pdf --output-dir output --dpi 200
```
**Output:** `output/images/med001.jpg`, `med002.jpg`, etc. (temporary names)

---

### Step 2: Extract Names & Create JSON (No Auto-Rename)
```bash
python images_to_json.py --input-dir output/images --output-dir output --source "Asvins Lifecare Pvt Ltd" --threads 32
```

**Creates (images NOT renamed yet):**
- `output/medicines.json` - Extracted medicines with IDs & types
- `output/extraction_successful.json` - Log of successful extractions (brand name, type, ID for each)
- `output/extraction_failed.json` - Log of failed/skipped images (for troubleshooting)
- `output/validation_report.json` - Quality validation findings
- Images remain as: `med001.jpg`, `med002.jpg`, etc.

---

### Step 2b: Manual Verification
Review the extracted data:
```bash
cat output/validation_report.json        # Check for validation issues
cat output/extraction_successful.json    # Check successful extractions (brand names, types)
cat output/extraction_failed.json        # Check failed/skipped images (for troubleshooting)
head -20 output/medicines.json           # Preview extracted medicines
ls output/images/ | head -10             # Verify images exist
```

**Fix issues if needed:**
- Edit `output/medicines.json` directly with any corrections

**Then re-validate after editing:**
```bash
python images_to_json.py --validate-only output/medicines.json --output-dir output
```

### Step 2c: Rename Images (After Verification)
Once `medicines.json` is correct, trigger rename:
```bash
python rename_images.py --json-path output/medicines.json --images-dir output/images
```

**Cleanup mapping (optional):**
After rename, remove the `originalImageName` field from JSON:
```bash
python rename_images.py --json-path output/medicines.json --images-dir output/images --cleanup-json
```

**How it works:**
- Uses explicit **mapping field**: Each medicine entry has `"originalImageName": "med001.jpg"` 
- Looks up the original image file for each medicine and renames it to the final ID
- **Safe for manual edits**: You can reorder, add, or remove rows in `medicines.json` — mapping still works
- **Optional cleanup**: Use `--cleanup-json` to remove mapping field after rename (reduces JSON size)

**Result:** Images renamed → `AMLOSVISS-40-OLM-TAB.jpg`, `ASVINS-DGM-SYR.jpg`, etc.

---

### Step 3: Extract Old Medicines (App Assets)
Use `images_to_json_old.py` with the app's existing images:
```bash
python images_to_json_old.py --images-dir ../../app/src/main/assets/images --output-dir output --threads 32
```
**Creates:** `output/old_medicines.json` - Extracted medicines from current app assets

---

### Step 3b: Review Old Medicines
Validate the extracted old medicines (same as Step 2b):
```bash
cat output/validation_report.json        # Check for validation issues
head -20 output/old_medicines.json       # Preview old medicines
```

**Fix issues if needed:**
- Edit `output/old_medicines.json` directly with corrections

**Then re-validate after editing:**
```bash
python images_to_json.py --validate-only output/old_medicines.json --output-dir output
```

### Step 3c: Cleanup Old Medicines (Optional)
Rename images to final names (optional, mirrors Step 2c):
```bash
python rename_images.py --json-path output/old_medicines.json --images-dir ../../app/src/main/assets/images --cleanup-json
```
**Note:** This removes `originalImageName` mapping field from JSON (reduces size)

---

### Step 4: Compare & Review Delta
```bash
python medicines_delta_sync.py   --current output/old_medicines.json   --new output/medicines.json   --show
```
**Compares:** `old_medicines.json` vs `medicines.json` - Shows additions/removals/changes

---

### Step 5: Finalize Sync (After Approval)
```bash
cp output/medicines.json output/approved_medicines.json
python finalize_sync.py --approved-json output/approved_medicines.json --extracted-images output/images --app-images ../../app/src/main/assets/images --app-json ../../app/src/main/assets/medicines.json
```
**Writes:** Updated app `medicines.json` + backup `medicines.json.bak`

---

## Workflow Summary

**New Medicines (Steps 1-2c):**
1. Extract images from PDF
2. Extract names & create JSON (auto-validation)
2b. Review & fix if needed
2c. Rename images to final format

**Old Medicines (Steps 3-3c) — Same logic:**
3. Extract from app assets via OCR
3b. Review & fix if needed
3c. Optional: Cleanup JSON mapping

**Compare & Finalize (Steps 4-5):**
4. Compare old vs new medicines (delta report)
5. Sync approved medicines to app (creates backup)

---

## Type Abbreviations

**Basic:** Tablet/Tablets → `TAB` | Capsule/Capsules → `CAP` | Pellets → `PEL` | Effervescent → `EFF` | Lozenges → `LOZ`  
**Syrups:** Junior Syrup → `JSYR` | Syrup → `SYR` | Dry Syrup → `DSY` | Elixir → `ELX` | Tincture → `TNC`  
**Injectables:** Injection → `INJ` | Infusion → `INF` | Vial → `VIL` | Ampule → `AMP`  
**Topical:** Cream → `CRM` | Gel → `GEL` | Ointment → `OIN` | Oil → `OIL` | Paste → `PST` | Liniment → `LIN` | Balm → `BAL` | Rub → `RUB`  
**Liquids:** Drops → `DRP` | Liquid → `LIQ` | Solution → `SOL` | Lotion → `LOT` | Emulsion → `EMU` | Wash → `WSH` | Mouthwash → `MWH` | Gargle → `GAR`  
**Other:** Powder → `PWD` | Granules → `GRN` | Suspension → `SUS` | Softgel → `SGC` | Spray → `SPR` | Film → `FLM` | Inhaler → `INH` | Gummies → `GUM`  
**Special:** Suppository → `SUP` | Pessary → `PES` | Enema → `ENM` | Basti → `BAS` | Nasal Spray → `NSP` | Eye Drops → `EYE` | Eye Ointment → `EYO` | Eye Gel → `EYG` | Ear Drops → `EAR`  
**Supplements:** Patch → `PTH` | Device → `DEV` | Tonic → `TON` | Soap → `SOP` | Sachet → `SAC`  
**Ayurvedic:** Churna → `CHR` | Ghee → `GHE` | Kwath → `KWA` | Ras → `RAS`

---

## Quick Reference

| Step | Script | Input | Output | Action |
|------|--------|-------|--------|--------|
| 1 | `pdf_to_images.py` | PDF file | `med001.jpg`, etc. | Render & crop |
| 2 | `images_to_json.py` | Images | `medicines.json`, `extraction_log.json`, `validation_report.json` | Extract names |
| 2b | Manual | Validation reports | — | Review & fix |
| 2c | `rename_images.py` | `medicines.json` | Renamed images | Rename when ready |
| 3 | `images_to_json_old.py` | App assets images | `old_medicines.json` | Extract existing data |
| 3b | Manual | Validation reports | — | Review & fix |
| 3c | `rename_images.py` | `old_medicines.json` | Images + JSON cleanup | Rename & cleanup (optional) |
| 4 | `medicines_delta_sync.py` | Old vs new JSON | Delta report | Compare changes |
| 5 | `finalize_sync.py` | Approved JSON | Updated app assets | Sync to app |

---

## Complete Example

```bash
# Step 1: Extract
python pdf_to_images.py ../MEDICINES.pdf --dpi 150

# Step 2: Extract names
python images_to_json.py --input-dir output/images --output-dir output --source "Asvins Lifecare Pvt Ltd"

# Step 2b: Review & edit
cat output/validation_report.json
cat output/extraction_successful.json
cat output/extraction_failed.json
# Edit output/medicines.json if needed

# Optional: Re-validate after edits
python images_to_json.py --validate-only output/medicines.json --output-dir output

# Step 2c: Rename when ready
python rename_images.py --json-path output/medicines.json --images-dir output/images

# Optional: Clean up JSON (remove originalImageName field)
python rename_images.py --json-path output/medicines.json --images-dir output/images --cleanup-json

# Step 3: Extract old medicines from app assets
python images_to_json_old.py --images-dir ../../app/src/main/assets/images --output-dir output --threads 32

# Step 3b: Review & validate old medicines
cat output/validation_report.json
head -20 output/old_medicines.json

# Step 3c: Cleanup old medicines (optional)
python rename_images.py --json-path output/old_medicines.json --images-dir ../../app/src/main/assets/images --cleanup-json

# Step 4: Compare
python medicines_delta_sync.py --current output/old_medicines.json --new output/medicines.json --show

# Step 5: Finalize (after approval)
cp output/medicines.json output/approved_medicines.json
python finalize_sync.py --approved-json output/approved_medicines.json --extracted-images output/images --app-images ../../app/src/main/assets/images --app-json ../../app/src/main/assets/medicines.json
```

---

---

## Output Files Explained

### medicines.json
Array of medicine objects with extracted data. Ready for finalization or editing.
```json
[
  {
    "id": "AMLOSVISS-40-OLM-TAB",
    "brandName": "AMLOSVISS 40 OLM TABLET",
    "isActive": true,
    "source": "Asvins Lifecare Pvt Ltd",
    "preferredAffiliate": false,
    "originalImageName": "med001.jpg"
  }
]
```

### extraction_successful.json
Log of all successfully extracted medicines (brand name, type detected, ID created).
```json
[
  {
    "index": 1,
    "imageName": "med001.jpg",
    "brandName": "AMLOSVISS 40 OLM TABLET",
    "medicineType": "Tablet",
    "medicineId": "AMLOSVISS-40-OLM-TAB"
  },
  {
    "index": 3,
    "imageName": "med003.jpg",
    "brandName": "ASVINS DGM SYRUP",
    "medicineType": "Syrup",
    "medicineId": "ASVINS-DGM-SYR"
  }
]
```

### extraction_failed.json
Log of images that failed to process (with error details for troubleshooting).
```json
[
  {
    "index": 2,
    "imageName": "med002.jpg",
    "brandName": null,
    "medicineType": null,
    "medicineId": null,
    "error": "Failed to load image"
  }
]
```

### extraction_log.json
Combined log of each image processed. Use for debugging and tracing extraction.
```json
[
  {
    "index": 1,
    "imageName": "med001.jpg",
    "brandName": "AMLOSVISS 40 OLM TABLET",
    "medicineType": "Tablet",
    "medicineId": "AMLOSVISS-40-OLM-TAB",
    "error": null
  }
]
```

### validation_report.json
Quality checks results. Shows duplicates, missing types, suspicious names, bad IDs.

---

**OCR extracts wrong names or misses types?**
- Review `extraction_successful.json` to see what was extracted for each image
- Review `extraction_failed.json` to see which images failed and why
- Edit `output/medicines.json` directly
- Run `python images_to_json.py --validate-only output/medicines.json --output-dir output` to re-validate after edits

**Can I see what happened during extraction?**
- Check `extraction_successful.json` — contains successful extractions with brand names and types
- Check `extraction_failed.json` — contains failed images with error details
- Check `validation_report.json` — contains validation issues
- Use these logs to debug extraction problems

**Can I edit medicines.json manually?**
- Yes! Edit anytime in Step 2b
- Run `python images_to_json.py --validate-only output/medicines.json --output-dir output` to verify, then run `rename_images.py` in Step 2c
- Use `--cleanup-json` flag to remove mapping field after rename

**Can I stop after Step 4?**
- Yes! Step 5 is the only step that modifies app files

**Processing is slow?**
- Use `--threads` to run more parallel workers
- Default: 4 threads | Recommended: 8-16 | Max: 32
- Example: `python images_to_json.py --threads 16` for 334 images

**Need to rollback?**
```bash
cp ../../app/src/main/assets/medicines.json.bak ../../app/src/main/assets/medicines.json
```

---

## Key Files

- `pdf_to_images.py` - PDF → images
- `images_to_json.py` - Images → JSON + validation (Step 2 and Step 3)
- `rename_images.py` - Manually trigger image rename
- `medicines_delta_sync.py` - Compare old vs new
- `finalize_sync.py` - Copy to app assets (creates backup)

## Output Files (from Step 2)

- `medicines.json` - Extracted medicines ready for finalization
- `extraction_successful.json` - Detailed log of successful extractions (for review)
- `extraction_failed.json` - Log of failed/skipped images (for troubleshooting)
- `validation_report.json` - Quality check results


