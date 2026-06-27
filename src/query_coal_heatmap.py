"""
query_coal_heatmap.py — State-wise Heatmap of Coal Share in Total Energy Use
X-axis: Year | Y-axis: State | Color: Share of Coal (%)
Uses Block H fuel consumption data converted to TJ.
"""

import plotly.express as px
import pandas as pd

# Same conversion factors as energy_mix
GJ_PER_TON_COAL = 29.3
GJ_PER_KG_GAS = 0.0527
GJ_PER_KWH = 0.0036
GJ_PER_TON_PETCOKE = 32.5
GJ_PER_TON_OTHER = 25.0
TJ = 1000


def plot_coal_heatmap(df_fuel, selected_years=None):
    """
    Heatmap showing each state's coal share of total energy consumption (%).

    Returns: (fig, summary_dict)
    """
    df = df_fuel.copy()
    if selected_years:
        df = df[df["year"].isin(selected_years)]

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

    # Coal share %
    df["coal_share_pct"] = df.apply(
        lambda r: (r["coal_tj"] / r["total_tj"] * 100) if r["total_tj"] > 0 else 0, axis=1
    )

    # Pivot: state × financial_year
    pivot = df.pivot_table(
        index="state", columns="financial_year",
        values="coal_share_pct", aggfunc="mean",
    )

    fy_order = df.sort_values("year")["financial_year"].unique().tolist()
    pivot = pivot.reindex(columns=fy_order)
    pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=True).index]

    fig = px.imshow(
        pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        color_continuous_scale="RdYlGn_r",
        labels=dict(x="Financial Year", y="State", color="Coal Share (%)"),
        aspect="auto",
        text_auto=".0f",
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(family="Inter", size=12),
        margin=dict(l=150, r=30, t=30, b=60),
        height=max(400, len(pivot) * 28),
        coloraxis_colorbar=dict(title="Coal %", len=0.6),
    )

    avg_share = df["coal_share_pct"].mean()
    state_avg = df.groupby("state")["coal_share_pct"].mean()
    highest_state = state_avg.idxmax()
    lowest_state = state_avg.idxmin()

    summary = {
        "avg_coal_share": avg_share,
        "highest_coal_state": highest_state,
        "lowest_coal_state": lowest_state,
        "n_states": df["state"].nunique(),
        "n_years": df["year"].nunique(),
    }

    return fig, summary


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))
    from src.load_data import load_fuel_indigenous
    df = load_fuel_indigenous()
    fig, s = plot_coal_heatmap(df)
    print("Stats:", s)
    fig.show()
