"""
query_emissions_intensity.py — CO₂ Emissions per Tonne of Cement Produced
Bar chart by state for overlapping years between production and emissions data.
"""

import plotly.express as px
import pandas as pd


def plot_emissions_intensity(df_prod, df_emis, year=None):
    """
    Bar chart: tonnes CO₂ per tonne cement for each state.

    Returns: (fig, summary_dict)
    """
    # Find overlapping years
    common_years = sorted(set(df_prod["year"]) & set(df_emis["year"]))
    if not common_years:
        return None, {"error": "No overlapping years between production and emissions data"}

    if year is None:
        year = max(common_years)

    prod = df_prod[df_prod["year"] == year][["state", "total"]].copy()
    emis = df_emis[df_emis["year"] == year][["state", "total_emissions_mt"]].copy()

    merged = prod.merge(emis, on="state", how="inner")
    # Convert: emissions in MT (million tonnes), production in tonnes
    # Intensity = (emissions_mt * 1e6) / production_tonnes = tonnes CO₂ per tonne cement
    merged = merged[merged["total"] > 0].copy()
    merged["intensity"] = (merged["total_emissions_mt"] * 1e6) / merged["total"]
    merged = merged.sort_values("intensity", ascending=True)

    fy = df_prod[df_prod["year"] == year]["financial_year"].iloc[0]

    fig = px.bar(
        merged, x="intensity", y="state", orientation="h",
        labels={"intensity": "kg CO₂ / Tonne Cement", "state": ""},
        color="intensity",
        color_continuous_scale="RdYlGn_r",
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(family="Inter", size=12),
        margin=dict(l=150, r=30, t=30, b=60),
        height=max(400, len(merged) * 30),
        coloraxis_colorbar=dict(title="kg CO₂/T"),
        yaxis=dict(autorange="reversed"),
        hovermode="y unified",
    )

    avg_intensity = merged["intensity"].mean()
    worst = merged.iloc[-1]
    best = merged.iloc[0]

    summary = {
        "fy": fy,
        "year": year,
        "avg_intensity": avg_intensity,
        "worst_state": worst["state"],
        "worst_val": worst["intensity"],
        "best_state": best["state"],
        "best_val": best["intensity"],
        "n_states": len(merged),
        "common_years": common_years,
    }

    return fig, summary


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))
    from src.load_data import load_production, load_emissions
    fig, s = plot_emissions_intensity(load_production(), load_emissions())
    print("Stats:", s)
    fig.show()
