# Import medicines (JSON + images)

This guide explains how to import a set of medicines into BioFrench using a JSON file **and** attach images for each medicine.

> Audience: end users (non-developers)

## What you need

- A **JSON file** containing your medicines.
- A folder containing your **image files** (JPG/PNG/WebP recommended).
- (Optional) A spreadsheet (Excel/Google Sheets) if you want to prepare data first, then export to JSON.

## Before you start: prepare your images

1. Put all medicine images in a single folder on your computer.
2. Use clear, unique filenames. Avoid special characters.

**Recommended filename pattern**

- `brand-or-medicine-name_strength_form.jpg`
- Examples:
  - `paracetamol_500mg_tablet.jpg`
  - `amoxicillin_250mg_suspension.png`

**Tips**

- Use the same image file extension consistently when possible.
- Keep filenames stable—if you rename an image after creating your JSON, you must update the JSON too.

## JSON format

Your import JSON must be an **array** of medicine objects.

### Minimal example

```json
[
  {
    "name": "Paracetamol",
    "strength": "500 mg",
    "form": "Tablet",
    "images": [
      {
        "fileName": "paracetamol_500mg_tablet.jpg",
        "alt": "Paracetamol 500 mg tablet box"
      }
    ]
  }
]
```

### Supported fields (common)

Field names can vary depending on your instance configuration, but commonly supported fields include:

- `name` *(required)*: Display name of the medicine.
- `strength` *(recommended)*: e.g., `500 mg`, `250 mg/5 mL`.
- `form` *(recommended)*: e.g., `Tablet`, `Capsule`, `Syrup`.
- `manufacturer` *(optional)*
- `barcode` *(optional)*
- `description` *(optional)*

### Images field

Provide an `images` array. Each item should include:

- `fileName` *(required)*: Must match the **exact** filename in your image folder.
- `alt` *(recommended)*: Short description for accessibility.

Example with multiple images:

```json
[
  {
    "name": "Amoxicillin",
    "strength": "250 mg/5 mL",
    "form": "Suspension",
    "images": [
      { "fileName": "amoxicillin_front.jpg", "alt": "Amoxicillin bottle front" },
      { "fileName": "amoxicillin_back.jpg", "alt": "Amoxicillin bottle back" }
    ]
  }
]
```

## Importing in the app (step-by-step)

1. Sign in to BioFrench.
2. Go to **Medicines** (or **Inventory**) from the main menu.
3. Select **Import**.
4. Choose **JSON import**.
5. Upload your JSON file.
6. When prompted for images, select the folder (or select all image files) that matches the `fileName` values in your JSON.
7. Start the import.

During import you should see:

- How many medicines were detected.
- How many images were matched.
- Any errors (missing required fields, unknown fields, or missing images).

## How image matching works

- The app matches images by **exact filename**.
- Matching is **case-sensitive** on some systems.
  - `Paracetamol.jpg` is different from `paracetamol.jpg`.
- If the JSON references an image that is not provided, the medicine can still import, but the image will be skipped and listed in the import report.

## Validate your JSON before importing

Common JSON mistakes:

- Missing commas
- Using smart quotes (“ ”) instead of regular quotes (`"`)
- Trailing commas

You can validate your JSON using any online JSON validator or an editor like VS Code.

## Troubleshooting

### “Image not found” or “0 images matched”

- Confirm the JSON `fileName` matches the actual image filenames **exactly**.
- Confirm you selected the correct image folder/files during import.
- Check file extensions: `.jpg` vs `.jpeg`.

### “Invalid JSON”

- Ensure the file is valid JSON (not CSV).
- Ensure the top-level is an array: `[` ... `]`.

### Some medicines imported, others failed

- Open the import report and look for the first failing record.
- Check for missing required fields (often `name`).

## Best practices

- Start with 2–3 medicines as a test import.
- Keep a copy of the JSON you imported for auditing.
- Use consistent naming and formatting for `strength` and `form`.

---

If you want, share a sample of your JSON (with any sensitive data removed) and I can help you confirm the format matches what the app expects.
