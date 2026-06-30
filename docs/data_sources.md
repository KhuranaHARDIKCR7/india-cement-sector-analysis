# Data Sources & Processing

## 📊 The Dataset

The analysis in this dashboard is based on unit-level microdata from the **Annual Survey of Industries (ASI)**, published by the **Ministry of Statistics & Programme Implementation (MoSPI)**, Government of India. 

The dataset contains industrial survey responses across multiple years. For this project, the data was filtered and aggregated specifically to analyze the Indian cement sector (under National Industrial Classification code **2394**).

---

## 🛠️ Data Processing Pipelines

Since the raw microdata is extremely large and contains inconsistent schemas across different survey years, the project includes two data processing scripts in the `scripts/` folder to clean and consolidate the data:

1. **`process_asi_openpyxl.py` (Data Cleaning & Filtering)**
   - Extracts raw unit-level records.
   - Standardizes inconsistent column names and codes across different survey years.
   - Filters the records specifically for cement manufacturing factories (NIC 2394).
   - Writes the clean, filtered data into structured Excel worksheets.

2. **`process_asi_win32.py` (Excel Automation & Calculation)**
   - Automates a local instance of Microsoft Excel via COM APIs to evaluate complex array formulas (such as `XLOOKUP`) and refresh Pivot Tables.
   - Saves the calculated cached values into the final Excel workbooks so they can be read natively by the Python dashboard.

---

## 🔒 Data Privacy & Omission

Both the raw unit-level CSV files and the consolidated Excel workbooks (`data/State Annual Cement Prod.xlsx` and `data/Fuel Consumption_Cement.xlsx`) are **omitted from this public repository**.

* **Data Usage Agreement**: The datasets are compiled from unit-level government microdata and are subject to a strict **Data Usage Agreement / Non-Disclosure Agreement (NDA)** signed for the internship. 
* **Compliance**: To comply with these legal terms and prevent unauthorized distribution of unit-level government database records, all data files are kept private.
* **Purpose of this Repository**: This public repository serves as a portfolio showcase of the dashboard's software architecture, data cleaning pipelines, and interactive visualization logic.



