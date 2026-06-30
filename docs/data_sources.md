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

### Data Privacy & Omission of Datasets

Both the raw unit-level ASI CSV files and the consolidated Excel workbooks (`data/State Annual Cement Prod.xlsx` and `data/Fuel Consumption_Cement.xlsx`) are **not included** in this public repository.

#### Why the Data is Kept Private:
* **Data Usage Agreement**: The datasets are compiled from unit-level government microdata (Ministry of Statistics & Programme Implementation, India) and are subject to a strict **Data Usage Agreement** signed for the internship. 
* **Compliance**: To comply with these legal terms and prevent unauthorized distribution of unit-level government database records, all data files are kept private.
* **Purpose of this Repository**: This public repository serves as a portfolio showcase of the dashboard's software architecture, data cleaning pipelines, and interactive visualization logic.

