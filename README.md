# 🏭 India Cement Sector Analysis

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An interactive **Streamlit** dashboard for analyzing production, emissions, fuel consumption, market concentration, and energy mix trends in India's cement sector using **Annual Survey of Industries (ASI)** microdata from 2009-10 to 2023-24.

**🔗 Deployed App URL**: [india-cement-sector-analysis.streamlit.app](https://india-cement-sector-analysis-gvefvrjozntykmxxads27r.streamlit.app/)

---

## ✨ Features

| Page | Description |
|------|-------------|
| 📈 **Production Trend** | Multi-year line chart of cement output for top producing states |
| 📊 **State CAGR** | Diverging bar chart showing compound annual growth rates |
| 🏗️ **Market Concentration** | Stacked area chart of top-N states' share of national production |
| 🔥 **Energy Mix** | Stacked area chart of fuel composition (Coal, Gas, Electricity, Petcoke, Other) |
| 🗺️ **Coal Dependency** | State × Year heatmap of coal's share in total energy consumption |
| 🌊 **Fuel → State Flow** | Sankey diagram showing fuel type consumption flows to states |

Every page includes **KPI cards**, **interactive Plotly charts**, and **filter controls** for year and state selection.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/india-cement-analysis.git
cd india-cement-analysis

# Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

### Run the Dashboard

```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**.

---

## 📂 Project Structure

```
├── .gitignore
├── .streamlit/
│   └── config.toml              # Dark theme & server settings
├── LICENSE
├── README.md
├── requirements.txt
│
├── app.py                        # Streamlit dashboard entry point
│
├── src/                          # Importable Python package
│   ├── __init__.py
│   ├── load_data.py              # Data loading & cleaning utilities
│   ├── query_production_trend.py # Production trend visualisation
│   ├── query_energy_mix.py       # Energy mix stacked area chart
│   ├── query_coal_heatmap.py     # Coal dependency heatmap
│   ├── query_sankey.py           # Fuel → State Sankey diagram
│   ├── query_cagr.py             # State-wise CAGR chart
│   └── query_market_concentration.py # Market concentration chart
│
├── data/
│   ├── State Annual Cement Prod.xlsx   # Consolidated production data (Omitted/Private)
│   ├── Fuel Consumption_Cement.xlsx    # Consolidated fuel & emissions data (Omitted/Private)
│   ├── processed/                      # Processed Excel outputs (gitignored)
│   └── raw/                            # Raw ASI CSVs (gitignored)
│
├── scripts/                      # Offline data processing utilities
│   ├── process_asi_openpyxl.py   # Cross-platform (openpyxl)
│   └── process_asi_win32.py      # Windows-only (Excel COM)
│
└── docs/
    └── data_sources.md           # Details on data privacy and processing pipelines
```

---

## 📊 Data Sources & Privacy

The dashboard is designed to read from two consolidated Excel workbooks in `data/`:
* `State Annual Cement Prod.xlsx` (State-wise cement production)
* `Fuel Consumption_Cement.xlsx` (Fuel consumption & emissions data)

These files were generated from unit-level **Annual Survey of Industries (ASI)** microdata published by the [Ministry of Statistics & Programme Implementation (MoSPI)](https://www.mospi.gov.in/). 

> 🔒 **Data Omission Notice:** In compliance with the **Data Usage Agreement / NDA** signed for this internship, all raw and consolidated data files are kept private and omitted from this public repository. See [`docs/data_sources.md`](docs/data_sources.md) for more details on data privacy and compliance.

---

## ☁️ Deploy on Streamlit Community Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Click **"New app"** → Select your repo → Set main file to `app.py`
4. Click **Deploy**

The app will automatically install from `requirements.txt` and use the theme from `.streamlit/config.toml`.

---

## 🛠️ Data Processing Scripts

The `scripts/` folder contains utilities for processing raw unit-level ASI CSV data into the consolidated Excel workbooks:

| Script | Platform | Description |
|--------|----------|-------------|
| `process_asi_openpyxl.py` | Cross-platform | Uses `openpyxl` to copy template worksheets, insert raw CSV records, and update formula references |
| `process_asi_win32.py` | Windows only | Uses Excel COM automation (`win32com`) for native formula evaluation and pivot table refresh |

*(Note: These scripts are provided for code-review purposes only. They cannot be executed without the raw unit-level ASI microdata, which is omitted due to privacy agreements).*

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
