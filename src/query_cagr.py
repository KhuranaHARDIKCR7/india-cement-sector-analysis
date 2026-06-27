"""
query_cagr.py — State-wise CAGR of Cement Production
Diverging horizontal bar chart: green = growth, red = decline.
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np


def compute_cagr(df):
    """Compute CAGR for each state across available years."""
    years = sorted(df["year"].unique())
    if len(years) < 2:
        return pd.DataFrame()

    first_year, last_year = years[0], years[-1]
    n = last_year - first_year  # number of years gap

    first = df[df["year"] == first_year][["state", "total"]].rename(columns={"total": "start"})
    last = df[df["year"] == last_year][["state", "total"]].rename(columns={"total": "end"})

    merged = first.merge(last, on="state")
    # Only compute CAGR where start > 0
    merged = merged[merged["start"] > 0].copy()
    merged["cagr"] = ((merged["end"] / merged["start"]) ** (1 / n) - 1) * 100
    return merged.sort_values("cagr", ascending=True)


def plot_cagr(df_prod, selected_years=None):
    """
    Diverging bar chart of CAGR by state.

    Returns: (fig, summary_dict)
    """
    df = df_prod.copy()
    if selected_years:
        df = df[df["year"].isin(selected_years)]

    cagr_df = compute_cagr(df)
    if cagr_df.empty:
        return None, {"error": "Not enough years to compute CAGR"}

    colors = ["#ef4444" if v < 0 else "#22c55e" for v in cagr_df["cagr"]]

    fig = go.Figure(go.Bar(
        x=cagr_df["cagr"], y=cagr_df["state"],
        orientation="h", marker_color=colors,
        text=[f"{v:+.1f}%" for v in cagr_df["cagr"]],
        textposition="outside", textfont=dict(size=11),
        hovertemplate="%{y}: %{x:.1f}% CAGR<extra></extra>",
    ))

    fig.add_vline(x=0, line_color="#64748b", line_width=1)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(family="Inter", size=12),
        xaxis=dict(title="CAGR (%)", gridcolor="#1e293b", zeroline=False),
        yaxis=dict(title=""),
        margin=dict(l=150, r=80, t=30, b=60),
        height=max(400, len(cagr_df) * 28),
        hovermode="y unified",
    )

    years = sorted(df["year"].unique())
    fy_start = df[df["year"] == years[0]]["financial_year"].iloc[0]
    fy_end = df[df["year"] == years[-1]]["financial_year"].iloc[0]
    growing = (cagr_df["cagr"] > 0).sum()
    declining = (cagr_df["cagr"] < 0).sum()
    fastest = cagr_df.iloc[-1]
    slowest = cagr_df.iloc[0]

    summary = {
        "period": f"{fy_start} to {fy_end}",
        "n_states": len(cagr_df),
        "growing": growing,
        "declining": declining,
        "fastest_state": fastest["state"],
        "fastest_cagr": fastest["cagr"],
        "slowest_state": slowest["state"],
        "slowest_cagr": slowest["cagr"],
    }

    return fig, summary


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))
    from src.load_data import load_production
    fig, s = plot_cagr(load_production())
    print("Stats:", s)
    fig.show()
