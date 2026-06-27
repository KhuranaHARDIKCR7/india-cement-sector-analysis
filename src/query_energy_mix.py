"""
query_energy_mix.py — Multi-year Energy Mix Stacked Area Chart
X-axis: Year | Y-axis: Total Energy Consumption (TJ) | Stack: Coal, Gas, Electricity, Petcoke, Other Fuels
Uses Block H indigenous fuel consumption data, converted to TJ for a common unit.
"""

import plotly.graph_objects as go
import pandas as pd


# ── Conversion factors to TJ (terajoules) ───────────────────────────────────
# Standard calorific values for cement industry fuels
GJ_PER_TON_COAL = 29.3       # bituminous coal
GJ_PER_KG_GAS = 0.0527       # natural gas
GJ_PER_KWH = 0.0036          # electricity
GJ_PER_TON_PETCOKE = 32.5    # petroleum coke
GJ_PER_TON_OTHER = 25.0      # approximate for misc solid fuels

TJ = 1000  # 1 TJ = 1000 GJ


def prepare_energy_mix(df_fuel):
    """
    Aggregate Block H fuel consumption into 5 categories, convert to TJ.
    """
    df = df_fuel.copy()

    # Coal: summary column (coal_ton) already includes coke
    df["coal_tj"] = df["coal_ton"] * GJ_PER_TON_COAL / TJ

    # Gas
    df["gas_tj"] = df["gas_kg"] * GJ_PER_KG_GAS / TJ

    # Electricity: purchased + own generated
    df["elec_tj"] = (df["elec_purchased_kwh"] + df["elec_own_kwh"]) * GJ_PER_KWH / TJ

    # Petcoke: calcined + regular
    df["petcoke_tj"] = (df["petcoke_calcined_ton"] + df["petcoke_ton"]) * GJ_PER_TON_PETCOKE / TJ

    # Other: remaining tonnage fuels (bitumen, furnace oil approx, coke variants, lignite, etc.)
    other_cols = ["bitumen_ton", "coke_nec_ton", "coke_soft_ton", "coke_peat_ton",
                  "coke_mixed_ton", "coke_hard_ton", "coke_dust_ton", "coke_breeze_ton",
                  "briquettes_coke_ton", "asphalt_rock_ton", "crude_petro_ton",
                  "lignite_agg_ton", "briquettes_coal_ton", "coal_nec_ton",
                  "coal_slack_ton", "coal_compressed_ton", "coal_undersized_ton",
                  "coal_ton_direct", "anthracite_ton"]
    existing = [c for c in other_cols if c in df.columns]
    df["other_tj"] = df[existing].sum(axis=1) * GJ_PER_TON_OTHER / TJ

    return df


def plot_energy_mix(df_fuel, selected_years=None):
    """
    Stacked area chart of energy consumption by fuel type (in TJ).

    Returns: (fig, summary_dict)
    """
    df = prepare_energy_mix(df_fuel)
    if selected_years:
        df = df[df["year"].isin(selected_years)]

    fuel_cols = {
        "coal_tj": "Coal",
        "gas_tj": "Gas",
        "elec_tj": "Electricity",
        "petcoke_tj": "Petcoke",
        "other_tj": "Other Fuels",
    }

    yearly = df.groupby(["year", "financial_year"])[list(fuel_cols.keys())].sum().reset_index()
    yearly = yearly.sort_values("year")
    yearly["total_tj"] = yearly[list(fuel_cols.keys())].sum(axis=1)

    colors = {
        "Coal": "#ef4444",
        "Gas": "#22c55e",
        "Electricity": "#3b82f6",
        "Petcoke": "#f59e0b",
        "Other Fuels": "#8b5cf6",
    }

    fig = go.Figure()
    for col, label in fuel_cols.items():
        fig.add_trace(go.Scatter(
            x=yearly["financial_year"], y=yearly[col],
            name=label, mode="lines", stackgroup="one",
            line=dict(width=0.5, color=colors[label]),
            fillcolor=colors[label],
            hovertemplate=f"{label}: %{{y:,.0f}} TJ<extra></extra>",
        ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(family="Inter", size=13),
        xaxis=dict(title="Financial Year", showgrid=False, type="category"),
        yaxis=dict(title="Energy Consumption (TJ)", gridcolor="#1e293b"),
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
        margin=dict(l=60, r=30, t=30, b=80),
        height=520, hovermode="x unified",
    )

    # Summary
    latest = yearly.iloc[-1] if len(yearly) > 0 else {}
    total_latest = latest.get("total_tj", 0)
    dominant = max(fuel_cols.items(), key=lambda kv: latest.get(kv[0], 0))

    summary = {
        "total_consumption_tj": total_latest,
        "dominant_fuel": dominant[1],
        "dominant_share": (latest.get(dominant[0], 0) / total_latest * 100) if total_latest > 0 else 0,
        "latest_fy": latest.get("financial_year", "N/A"),
        "n_years": len(yearly),
    }

    return fig, summary


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))
    from src.load_data import load_fuel_indigenous
    df = load_fuel_indigenous()
    fig, s = plot_energy_mix(df)
    print("Stats:", s)
    fig.show()
