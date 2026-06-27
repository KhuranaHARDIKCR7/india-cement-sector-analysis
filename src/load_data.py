"""
load_data.py — Load and clean ASI cement production and fuel consumption data.
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROD_FILE = BASE_DIR / "data" / "State Annual Cement Prod.xlsx"
FUEL_FILE = BASE_DIR / "data" / "Fuel Consumption_Cement.xlsx"


# ── Financial year labels ────────────────────────────────────────────────────
FY_MAP = {
    2011: "2010-11", 2012: "2011-12", 2013: "2012-13", 2014: "2013-14",
    2015: "2014-15", 2016: "2015-16", 2017: "2016-17",
    2018: "2017-18", 2019: "2018-19", 2020: "2019-20",
    2021: "2020-21", 2022: "2021-22", 2023: "2022-23", 2024: "2023-24",
}


def _add_fy(df):
    """Add financial_year column from year."""
    df["financial_year"] = df["year"].map(FY_MAP).fillna(df["year"].astype(str))
    return df


# ── Cement Production (Summary sheet) ────────────────────────────────────────
def load_production() -> pd.DataFrame:
    """Load and clean cement production data from the DetailedData (NPCMS 374) sheet."""
    cols_to_use = [0, 1, 6, 11, 12, 27, 28]
    df = pd.read_excel(PROD_FILE, sheet_name="DetailedData (NPCMS 374)", header=3, usecols=cols_to_use)
    df.columns = ["year", "state", "plaster", "quicklime_lime",
                  "cement_clinkers", "portland_cement", "dolomite"]
    df = df.dropna(subset=["year", "state"])
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)

    prod_cols = ["plaster", "quicklime_lime", "cement_clinkers",
                 "portland_cement", "dolomite"]
    for col in prod_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Compute total production across these categories
    df["total"] = df[prod_cols].sum(axis=1)

    return _add_fy(df).reset_index(drop=True)



# ── Fuel Consumption (Block H — Indigenous) ──────────────────────────────────
def load_fuel_indigenous() -> pd.DataFrame:
    """Load Block H indigenous fuel consumption for cement factories."""
    df = pd.read_excel(FUEL_FILE, sheet_name="Fuel Cons (2394_1&2) BlkH",
                       header=5, usecols="A:AD")

    # Row 6 has NPCMS codes as headers — rename to readable names
    rename = {
        "Year": "year", "State": "state",
        9990900: "gas_kg", 9990700: "coal_ton",
        9990600: "petrol_diesel_rs", 9990500: "elec_purchased_kwh",
        9990400: "elec_own_kwh", 9920400: "other_fuel_rs",
        3350004: "petcoke_calcined_ton", 3350003: "petcoke_ton",
        3350001: "bitumen_ton", 3338001: "furnace_oil_litre",
        3310099: "coke_nec_ton", 3310011: "coke_soft_ton",
        3310009: "coke_peat_ton", 3310008: "coke_mixed_ton",
        3310007: "coke_hard_ton", 3310006: "coke_dust_ton",
        3310004: "coke_breeze_ton", 3310001: "briquettes_coke_ton",
        1533002: "asphalt_rock_ton", 1201000: "crude_petro_ton",
        1104000: "lignite_agg_ton", 1102001: "briquettes_coal_ton",
        1101099: "coal_nec_ton", 1101007: "coal_slack_ton",
        1101005: "coal_compressed_ton", 1101003: "coal_undersized_ton",
        1101002: "coal_ton_direct", 1101001: "anthracite_ton",
    }
    df = df.rename(columns=rename)

    # Keep only rows with valid year + state
    df = df.dropna(subset=["year", "state"])
    df["year"] = pd.to_numeric(df["year"], errors="coerce").dropna().astype(int)
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    df = df.fillna(0)

    return _add_fy(df).reset_index(drop=True)


# ── Fuel Consumption (Block I — Imported) ────────────────────────────────────
def load_fuel_imported() -> pd.DataFrame:
    """Load Block I imported fuel consumption for cement factories."""
    df = pd.read_excel(FUEL_FILE, sheet_name="Fuel Cons Imp(2394_1&2) BlkI",
                       header=5, usecols="A:O")

    rename = {
        "Year": "year", "State": "state",
        3350004: "imp_petcoke_calcined_ton", 3350003: "imp_petcoke_ton",
        3338001: "imp_furnace_oil_litre", 3337000: "imp_fuel_oil_kl",
        3310099: "imp_coke_nec_ton", 3310011: "imp_coke_soft_ton",
        3310009: "imp_coke_peat_ton", 3310007: "imp_coke_hard_ton",
        1104000: "imp_lignite_agg_ton", 1103000: "imp_lignite_ton",
        1102001: "imp_briquettes_ton", 1101002: "imp_coal_ton",
        1101001: "imp_anthracite_ton",
    }
    df = df.rename(columns=rename)
    df = df.dropna(subset=["year", "state"])
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    df = df.fillna(0)

    return _add_fy(df).reset_index(drop=True)


# ── Combined Fuel (Indigenous + Imported) ────────────────────────────────────
def load_fuel_combined() -> pd.DataFrame:
    """Merge Block H (indigenous) and Block I (imported) into a single DataFrame.
    Imported values are added to matching indigenous columns by state+year."""
    indig = load_fuel_indigenous()
    imp = load_fuel_imported()

    # Map imported columns → indigenous column names
    imp_to_indig = {
        "imp_petcoke_calcined_ton": "petcoke_calcined_ton",
        "imp_petcoke_ton": "petcoke_ton",
        "imp_furnace_oil_litre": "furnace_oil_litre",
        "imp_coke_nec_ton": "coke_nec_ton",
        "imp_coke_soft_ton": "coke_soft_ton",
        "imp_coke_peat_ton": "coke_peat_ton",
        "imp_coke_hard_ton": "coke_hard_ton",
        "imp_lignite_agg_ton": "lignite_agg_ton",
        "imp_lignite_ton": "lignite_agg_ton",       # merge into same bucket
        "imp_briquettes_ton": "briquettes_coal_ton",
        "imp_coal_ton": "coal_ton_direct",
        "imp_anthracite_ton": "anthracite_ton",
        "imp_fuel_oil_kl": "furnace_oil_litre",     # 1 KL = 1000 L, handled below
    }

    # Merge on year + state
    merged = indig.copy()
    imp_grouped = imp.groupby(["year", "state"]).sum(numeric_only=True).reset_index()

    for imp_col, indig_col in imp_to_indig.items():
        if imp_col not in imp_grouped.columns or indig_col not in merged.columns:
            continue
        # Special: imp_fuel_oil_kl is in K Litres, furnace_oil_litre is in Litres
        factor = 1000 if imp_col == "imp_fuel_oil_kl" else 1

        lookup = imp_grouped.set_index(["year", "state"])[imp_col] * factor
        merged = merged.set_index(["year", "state"])
        merged[indig_col] = merged[indig_col].add(lookup, fill_value=0)
        merged = merged.reset_index()

    return merged


# ── Emissions (Sheet1) ──────────────────────────────────────────────────────
def load_emissions() -> pd.DataFrame:
    """Load state-wise emissions data from Sheet1."""
    df = pd.read_excel(FUEL_FILE, sheet_name="Sheet1", header=1, usecols="A:H")
    df.columns = ["year", "state", "accounting_pct", "coal_emissions_mt",
                   "elec_emissions_mt", "petcoke_emissions_mt",
                   "furnace_oil_emissions_mt", "total_emissions_mt"]
    df = df.dropna(subset=["year", "state"])
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    df = df.fillna(0)

    return _add_fy(df).reset_index(drop=True)


# ── Total Emissions (pivot by state × year) ─────────────────────────────────
def load_total_emissions() -> pd.DataFrame:
    """Load total emissions pivot table."""
    df = pd.read_excel(FUEL_FILE, sheet_name="Total Emissions", header=0)
    # First col is State, rest are years, then Total, Cumulative
    return df


if __name__ == "__main__":
    for name, fn in [("Production", load_production),
                     ("Fuel (Indigenous)", load_fuel_indigenous),
                     ("Fuel (Imported)", load_fuel_imported),
                     ("Fuel (Combined)", load_fuel_combined),
                     ("Emissions", load_emissions)]:
        d = fn()
        print(f"{name}: {len(d)} rows, years={sorted(d['year'].unique())}")