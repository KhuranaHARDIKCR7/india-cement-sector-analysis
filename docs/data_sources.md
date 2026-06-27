# Data Sources

## Annual Survey of Industries (ASI) — Raw Data

The raw ASI microdata used by this project is published by the **Ministry of Statistics & Programme Implementation (MoSPI)**, Government of India.

### Where to Download

1. Visit the [MoSPI ASI page](https://www.mospi.gov.in/annual-survey-industries)
2. Download the **unit-level data** for each financial year (2009-10 through 2023-24)
3. Each year is distributed as a ZIP containing CSV files for each ASI block (A through J)

### Expected Folder Structure

After downloading, extract the CSVs into `data/raw/` with the following structure:

```
data/raw/
├── ASI_DATA_2009_10_CSV/
│   ├── A-IDENTIFICATION PARTICULARS.csv
│   ├── H-INPUT ITEMS INDIGENOUS.csv
│   ├── I-INPUT ITEMS IMPORTED.csv
│   ├── J-PRODUCTS AND BY-PRODUCTS.csv
│   └── ... (other blocks)
├── ASI_DATA_2010_11_CSV/
│   ├── blka201011.csv
│   ├── blkh201011.csv
│   └── ...
├── ASI_DATA_2011_12_CSV/
│   └── ...
└── ... (through ASI_DATA_2023_24_CSV)
```

> **Note:** The 2009-10 year uses a different CSV naming convention (e.g. `A-IDENTIFICATION PARTICULARS.csv` instead of `blka200910.csv`). The processing scripts handle both formats automatically.

### Processing Raw Data

To regenerate the consolidated Excel workbooks from raw CSVs:

```bash
# Cross-platform (requires openpyxl)
python scripts/process_asi_openpyxl.py

# Windows only (requires Excel installed)
python scripts/process_asi_win32.py
```

These scripts read from `data/raw/`, use template workbooks from `data/processed/ASI_DATA_2014_15_CSV/` as a reference, and output processed Excel files to `data/processed/`.

### Why Raw Data Is Not Included

The raw ASI CSV files total over **100 MB per year** (11 years ≈ 1+ GB). GitHub has a 100 MB per-file limit and discourages repositories larger than 1 GB. The raw data is therefore excluded via `.gitignore`.

The two consolidated workbooks (`data/State Annual Cement Prod.xlsx` and `data/Fuel Consumption_Cement.xlsx`) contain all the aggregated data needed to run the dashboard and are included in the repository.
