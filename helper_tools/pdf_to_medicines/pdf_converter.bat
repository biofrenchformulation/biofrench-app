@echo off
REM PDF to Medicines Converter - Windows Batch Wrapper
REM Usage: pdf_converter.bat MEDICINES.pdf [output_dir] [source]

setlocal enabledelayedexpansion

if "%1"=="" (
    echo Usage: pdf_converter.bat ^<pdf_path^> [output_dir] [source]
    echo.
    echo Example:
    echo   pdf_converter.bat ..\MEDICINES.pdf
    echo   pdf_converter.bat ..\MEDICINES.pdf output_folder "Asvins"
    exit /b 1
)

set PDF_PATH=%1
set OUTPUT_DIR=%2
set SOURCE=%3

if "%OUTPUT_DIR%"=="" set OUTPUT_DIR=output
if "%SOURCE%"=="" set SOURCE=Biofrench

echo PDF to Medicines Converter
echo PDF: %PDF_PATH%
echo Output Directory: %OUTPUT_DIR%
echo Source: %SOURCE%
echo.

python pdf_to_medicines_converter.py "%PDF_PATH%" --output-dir "%OUTPUT_DIR%" --source "%SOURCE%"

if errorlevel 1 (
    echo.
    echo Error: Make sure you have installed dependencies:
    echo   pip install -r pdf_converter_requirements.txt
    echo And Tesseract OCR:
    echo   winget install --id UB-Mannheim.TesseractOCR -e
    exit /b 1
)

echo.
echo Done! Check %OUTPUT_DIR% directory for results.
pause
