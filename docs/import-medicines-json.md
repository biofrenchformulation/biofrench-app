# Import medicines from a JSON file (with images)

This guide shows the **simple steps** to import medicines into BioFrench using a **JSON file** and (optionally) add **images**.

> Audience: end users (non-developers)

---

## Step-by-step

### 1) Prepare your files

1. Put your **JSON file** somewhere easy to find (for example: **Downloads**).
2. Put **all medicine images** in **one folder**.
   - Keep filenames simple.
   - Don’t rename images after you prepare your JSON.

---

### 2) Open the import screen in BioFrench

1. Sign in to **BioFrench**.
2. Open **Medicines** (sometimes called **Inventory**) from the main menu.
3. Click **Import**.
4. Choose **JSON import**.

---

### 3) Upload your JSON file

1. Click **Choose file** (or **Upload**).
2. Select your JSON file.
3. Continue.

---

### 4) Add images (optional but recommended)

When the app asks for images:

1. Select the **folder** that contains your medicine images (or select all image files).
2. Continue.

**Important:** images are matched by **exact filename**.
- Example: if your JSON says `"fileName": "paracetamol_500mg_tablet.jpg"`, your image must be named exactly `paracetamol_500mg_tablet.jpg`.

---

### 5) Start the import

1. Click **Start import**.
2. Wait for the import to finish.

You should see a summary like:
- How many medicines were found
- How many images were matched
- Any errors

---

## If images don’t show up

- Make sure you selected the correct folder / files.
- Check spelling and file extension (`.jpg` vs `.jpeg` vs `.png`).
- Check capitalization: `Paracetamol.jpg` is different from `paracetamol.jpg` on some systems.
