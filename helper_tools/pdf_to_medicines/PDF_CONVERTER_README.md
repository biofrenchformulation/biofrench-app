# PDF to Medicines Converter

A Python helper tool that extracts medicines from a PDF where **each page contains one
medicine** (a product/packaging image with the brand name printed on it).

It generates:
- `medicines.json` — Compatible with the BioFrench app's MedicineJson format
- `images/` — One image per medicine, named `{stringId}-1.png` (e.g. `med001-1.png`)

## How It Works

1. **Renders each page** as a single high-resolution image (1 medicine per page)
2. **Auto-crops** white margins to keep just the product image
3. **Extracts the brand name** via OCR — picks the largest/most prominent text on the page
4. **Generates** `medicines.json` and the matching images

## Installation

### Prerequisites
- Python 3.8+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract) (for brand-name extraction)

### Install Tesseract (Windows)
```powershell
winget install --id UB-Mannheim.TesseractOCR -e
```
The tool auto-detects Tesseract at `C:\Program Files\Tesseract-OCR\tesseract.exe`.

### Install Python Dependencies
```bash
pip install -r pdf_converter_requirements.txt
```

## Usage

### Basic Usage
```bash
cd helper_tools/pdf_to_medicines
python pdf_to_medicines_converter.py ../MEDICINES.pdf --source "Asvins"
```

This creates:
- `output/medicines.json`
- `output/images/med001-1.png`, `med002-1.png`, ...

### Options
| Option | Description | Default |
|---|---|---|
| `pdf_path` | Path to the PDF file (required) | — |
| `--output-dir` | Output directory | `output` |
| `--source` | Source name for medicines | `Biofrench` |
| `--dpi` | Render resolution | `200` |
| `--start-page` | First page to process (1-based) | `1` |
| `--end-page` | Last page (inclusive) | last page |
| `--no-ocr` | Disable OCR; use placeholder names | off |
| `--no-crop` | Disable auto-cropping of margins | off |

### Examples
```bash
# Higher resolution and custom source
python pdf_to_medicines_converter.py ../MEDICINES.pdf --source "Asvins" --dpi 250

# Process a page range (useful for testing)
python pdf_to_medicines_converter.py ../MEDICINES.pdf --start-page 2 --end-page 10

# Skip OCR (faster, names become med001, med002, ...)
python pdf_to_medicines_converter.py ../MEDICINES.pdf --no-ocr
```

## Output Format

### medicines.json
```json
[
  {
    "id": "med002",
    "brandName": "AMLOSVISS-AT-50",
    "isActive": true,
    "source": "Asvins",
    "preferredAffiliate": false
  }
]
```

### Images
Saved as `output/images/{stringId}-1.png`, matching the app's asset convention.
The JSON `id` maps to `MedicineEntity.stringId`, which links the image automatically
via `findMedicineImageAsset()`.

## After Extraction

1. **Review `medicines.json`** — OCR may misread some brand names; fix them manually.
2. **Verify images** in `output/images/`.
3. **Copy images** to `app/src/main/assets/images/`.
4. **Import** `medicines.json` via the admin screen.

## Troubleshooting

### Brand names are wrong or empty
- OCR depends on print clarity. Increase `--dpi` (e.g. `--dpi 300`) for sharper text.
- Manually correct names in `medicines.json` afterwards.
- The first/cover page often has no real brand name — delete that entry.

### "pytesseract not installed" warning
Install Tesseract (see above) and `pip install pytesseract`.
Without OCR, names fall back to `med001`, `med002`, etc.

### Tesseract not found
If installed elsewhere, set the path at the top of the script:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\path\to\tesseract.exe"
```
