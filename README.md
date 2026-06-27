# 🏭 India Cement Sector Analysis

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An interactive **Streamlit** dashboard for analyzing production, emissions, fuel consumption, market concentration, and energy mix trends in India's cement sector using **Annual Survey of Industries (ASI)** microdata from 2009-10 to 2023-24.

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
| ⚡ **Emissions Intensity** | Horizontal bar chart of kg CO₂ per tonne of cement produced |

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
│   ├── query_emissions_intensity.py # CO₂ emissions intensity
│   ├── query_cagr.py             # State-wise CAGR chart
│   └── query_market_concentration.py # Market concentration chart
│
├── data/
│   ├── State Annual Cement Prod.xlsx   # Consolidated production data
│   ├── Fuel Consumption_Cement.xlsx    # Consolidated fuel & emissions data
│   ├── processed/                      # Processed Excel outputs (gitignored)
│   └── raw/                            # Raw ASI CSVs (gitignored — see docs/)
│
├── scripts/                      # Offline data processing utilities
│   ├── process_asi_openpyxl.py   # Cross-platform (openpyxl)
│   └── process_asi_win32.py      # Windows-only (Excel COM)
│
└── docs/
    └── data_sources.md           # How to obtain raw ASI data
```

---

## 📊 Data Sources

The dashboard reads from two consolidated Excel workbooks in `data/`:

| File | Contents |
|------|----------|
| `State Annual Cement Prod.xlsx` | State-wise cement production (plaster, quicklime, clinkers, portland cement, dolomite) |
| `Fuel Consumption_Cement.xlsx` | Block H/I fuel consumption, emissions data, and total emissions pivot |

These were generated from **Annual Survey of Industries (ASI)** microdata published by the [Ministry of Statistics & Programme Implementation (MoSPI)](https://www.mospi.gov.in/). See [`docs/data_sources.md`](docs/data_sources.md) for details on obtaining the raw data.

---

## ☁️ Deploy on Streamlit Community Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Click **"New app"** → Select your repo → Set main file to `app.py`
4. Click **Deploy**

The app will automatically install from `requirements.txt` and use the theme from `.streamlit/config.toml`.

---

## 🛠️ Data Processing Scripts

The `scripts/` folder contains utilities for processing raw ASI CSV data into the consolidated Excel workbooks. These are **not required** to run the dashboard — only to regenerate the data files from scratch.

| Script | Platform | Description |
|--------|----------|-------------|
| `process_asi_openpyxl.py` | Cross-platform | Uses `openpyxl` to copy template worksheets, insert raw CSV records, and update formula references |
| `process_asi_win32.py` | Windows only | Uses Excel COM automation (`win32com`) for native formula evaluation and pivot table refresh |

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
