# Image Naming & Source Updates

## Summary
Updated the entire BioFrench app to use new image naming convention and correct source attribution.

## Changes Made

### 1. Image Naming Convention
**Before:** `{medicineId}-1.jpg` (e.g., `ASVINS-DGM-1.jpg`)
**After:** `{medicineId}.jpg` (e.g., `ASVINS-DGM.jpg`)

### 2. Default Source
**Before:** "Biofrench" or "Asvins Medicines Catalog"
**After:** "Asvins Lifecare Pvt Ltd"

### 3. Files Updated

#### PDF Converter
- `pdf_to_medicines_converter.py`
  - Image path: `f"{string_id}-1.jpg"` → `f"{string_id}.jpg"`
  - Default source: `"Biofrench"` → `"Asvins Lifecare Pvt Ltd"`
  - Updated docstring example

#### Android App (Kotlin)
- `AppConfig.kt`
  - `IMAGE_SUFFIX = "-1"` → `IMAGE_SUFFIX = ""`
  - Comment: Updated to reflect new naming

- `ImageImportHandler.kt`
  - `IMAGE_SUFFIX = "-1"` → `IMAGE_SUFFIX = ""`
  - Comments: Updated to reflect new naming pattern
  - Logic automatically updated via constant (all usages: `$medicineId$IMAGE_SUFFIX.$ext`)

- `MedicineCard.kt`
  - Log message: `"${medicine.id}-1"` → `"${medicine.id}"`

#### Tests
- `ImageUtilsTest.kt`
  - Updated test comments to reflect new naming

### 4. Current Database
- `output/medicines.json`
  - All 335 medicines updated to source: "Asvins Lifecare Pvt Ltd"
  - Ready for import into BioFrench Android app

## How It Works

### Image Discovery
The app now looks for images using:
```
{medicineId}.{extension}
```

Supported extensions checked in order:
1. `.svg`
2. `.png`
3. `.jpg`
4. `.jpeg`

### Naming Examples
- `ASVINS-DGM.jpg` (instead of `ASVINS-DGM-1.jpg`)
- `TELASVI-AZ-408.png` (instead of `TELASVI-AZ-408-1.png`)
- `ASVICEF-250.svg` (instead of `ASVICEF-250-1.svg`)

## Integration Steps

1. **Export images** from PDF converter:
   ```bash
   python pdf_to_medicines_converter.py ../MEDICINES.pdf --source "Asvins Lifecare Pvt Ltd"
   ```

2. **Copy images** to app assets:
   ```bash
   cp -r output/images/* ../../../app/src/main/assets/images/
   ```

3. **Import medicines** via Admin Screen:
   - Open Admin screen in app
   - Click "Import from JSON"
   - Select `output/medicines.json`

## Verification
Run the converter and verify:
- All images are named `{id}.jpg` (no `-1`)
- All medicines have source: "Asvins Lifecare Pvt Ltd"
- All medicines have `isActive: true`
- `preferredAffiliate: false` (set to true only when needed)

## Notes
- IMAGE_SUFFIX constant is empty string (""), not a field containing "-1"
- Existing images with `-1` naming can be renamed or left as-is (old images won't be found, but won't cause errors)
- To migrate existing database: manually update image filenames or re-import with new converter
