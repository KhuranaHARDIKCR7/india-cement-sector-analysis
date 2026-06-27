"""
query_market_concentration.py — Market Concentration of Top States
Line chart: share of top-5 states in national production over time.
"""

import plotly.graph_objects as go
import pandas as pd


def plot_market_concentration(df_prod, top_n=5, selected_years=None):
    """
    Line chart showing top-N states' share of total national production by year.

    Returns: (fig, summary_dict)
    """
    df = df_prod.copy()
    if selected_years:
        df = df[df["year"].isin(selected_years)]

    # National total by year
    national = df.groupby(["year", "financial_year"])["total"].sum().reset_index()
    national.columns = ["year", "financial_year", "national_total"]

    # Top N states (by average production across all years)
    top_states = df.groupby("state")["total"].mean().nlargest(top_n).index.tolist()

    # Top N total by year
    top_df = df[df["state"].isin(top_states)].groupby(["year", "financial_year"])["total"].sum().reset_index()
    top_df.columns = ["year", "financial_year", "top_total"]

    merged = national.merge(top_df, on=["year", "financial_year"])
    merged["top_share_pct"] = merged["top_total"] / merged["national_total"] * 100
    merged["rest_share_pct"] = 100 - merged["top_share_pct"]
    merged = merged.sort_values("year")

    fig = go.Figure()

    # Stacked area: top N vs rest
    fig.add_trace(go.Scatter(
        x=merged["financial_year"], y=merged["top_share_pct"],
        name=f"Top {top_n} States", fill="tozeroy",
        line=dict(color="#3b82f6", width=2),
        hovertemplate=f"Top {top_n}: %{{y:.1f}}%<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=merged["financial_year"], y=[100] * len(merged),
        name=f"Remaining States", fill="tonexty",
        line=dict(color="#64748b", width=0),
        hovertemplate="Rest: %{customdata:.1f}%<extra></extra>",
        customdata=merged["rest_share_pct"],
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(family="Inter", size=13),
        xaxis=dict(title="Financial Year", showgrid=False, type="category"),
        yaxis=dict(title="Share of National Production (%)", gridcolor="#1e293b",
                   range=[0, 105]),
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
        margin=dict(l=60, r=30, t=30, b=80),
        height=450, hovermode="x unified",
    )

    latest = merged.iloc[-1]
    earliest = merged.iloc[0]

    summary = {
        "top_n": top_n,
        "top_states": top_states,
        "latest_share": latest["top_share_pct"],
        "earliest_share": earliest["top_share_pct"],
        "trend": "increasing" if latest["top_share_pct"] > earliest["top_share_pct"] else "decreasing",
        "latest_fy": latest["financial_year"],
        "n_years": len(merged),
    }

    return fig, summary


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))
    from src.load_data import load_production
    fig, s = plot_market_concentration(load_production())
    print("Stats:", s)
    print("Top states:", s["top_states"])
    fig.show()
