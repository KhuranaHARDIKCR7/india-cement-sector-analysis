"""
query_sankey.py — Sankey Diagram: Fuel Types → States
Source: Fuel Types | Destination: States | Width: Consumption Volume (TJ)
Uses Block H indigenous fuel consumption data.
"""

import plotly.graph_objects as go
import pandas as pd

# Same conversion factors
GJ_PER_TON_COAL = 29.3
GJ_PER_KG_GAS = 0.0527
GJ_PER_KWH = 0.0036
GJ_PER_TON_PETCOKE = 32.5
GJ_PER_TON_OTHER = 25.0
TJ = 1000


def plot_sankey(df_fuel, year=None, top_n=12):
    """
    Sankey diagram showing flow of fuel consumption to states (in TJ).

    Returns: (fig, summary_dict)
    """
    df = df_fuel.copy()

    if year is None:
        year = df["year"].max()
    df = df[df["year"] == year]

    fy_label = df["financial_year"].iloc[0] if len(df) > 0 else str(year)

    # Convert to TJ
    df["coal_tj"] = df["coal_ton"] * GJ_PER_TON_COAL / TJ
    df["gas_tj"] = df["gas_kg"] * GJ_PER_KG_GAS / TJ
    df["elec_tj"] = (df["elec_purchased_kwh"] + df["elec_own_kwh"]) * GJ_PER_KWH / TJ
    df["petcoke_tj"] = (df["petcoke_calcined_ton"] + df["petcoke_ton"]) * GJ_PER_TON_PETCOKE / TJ

    other_cols = ["bitumen_ton", "coke_nec_ton", "coke_soft_ton", "coke_peat_ton",
                  "coke_mixed_ton", "coke_hard_ton", "coke_dust_ton", "coke_breeze_ton",
                  "briquettes_coke_ton", "asphalt_rock_ton", "crude_petro_ton",
                  "lignite_agg_ton", "briquettes_coal_ton", "coal_nec_ton",
                  "coal_slack_ton", "coal_compressed_ton", "coal_undersized_ton",
                  "coal_ton_direct", "anthracite_ton"]
    existing = [c for c in other_cols if c in df.columns]
    df["other_tj"] = df[existing].sum(axis=1) * GJ_PER_TON_OTHER / TJ

    df["total_tj"] = df["coal_tj"] + df["gas_tj"] + df["elec_tj"] + df["petcoke_tj"] + df["other_tj"]

    # Top N states by total consumption
    top_states = df.nlargest(top_n, "total_tj")["state"].tolist()
    df = df[df["state"].isin(top_states)]

    fuel_types = ["Coal", "Gas", "Electricity", "Petcoke", "Other Fuels"]
    fuel_cols = ["coal_tj", "gas_tj", "elec_tj", "petcoke_tj", "other_tj"]
    fuel_colors = ["rgba(239,68,68,1)", "rgba(34,197,94,1)",
                   "rgba(59,130,246,1)", "rgba(245,158,11,1)", "rgba(139,92,246,1)"]
    link_alphas = ["rgba(239,68,68,0.35)", "rgba(34,197,94,0.35)",
                   "rgba(59,130,246,0.35)", "rgba(245,158,11,0.35)", "rgba(139,92,246,0.35)"]

    node_labels = fuel_types + top_states
    node_colors = fuel_colors + ["rgba(100,116,139,1)"] * len(top_states)

    sources, targets, values, link_colors = [], [], [], []

    for fi, (fuel, col) in enumerate(zip(fuel_types, fuel_cols)):
        for si, state in enumerate(top_states):
            row = df[df["state"] == state]
            val = row[col].values[0] if len(row) > 0 else 0
            if val > 0.01:
                sources.append(fi)
                targets.append(len(fuel_types) + si)
                values.append(val)
                link_colors.append(link_alphas[fi])

    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=20, thickness=25,
            label=node_labels,
            color=node_colors,
            line=dict(color="#1e293b", width=1),
        ),
        link=dict(
            source=sources, target=targets, value=values,
            color=link_colors,
        ),
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(family="Inter", size=12, color="#cbd5e1"),
        margin=dict(l=30, r=30, t=30, b=30),
        height=550,
    )

    total = df["total_tj"].sum()
    top_consumer = df.nlargest(1, "total_tj")
    summary = {
        "year": year,
        "fy": fy_label,
        "total_consumption_tj": total,
        "top_consumer": top_consumer["state"].values[0] if len(top_consumer) > 0 else "N/A",
        "top_consumer_val": top_consumer["total_tj"].values[0] if len(top_consumer) > 0 else 0,
        "n_states": len(top_states),
    }

    return fig, summary


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))
    from src.load_data import load_fuel_indigenous
    fig, s = plot_sankey(load_fuel_indigenous())
    print("Stats:", s)
    fig.show()
