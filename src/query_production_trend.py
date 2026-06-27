"""
query_production_trend.py — Trend of cement production for top producing states.
Modular query: returns a Plotly figure + summary stats.
"""

import plotly.express as px


def get_top_states(df, n=10):
    """Return top N states by average total production."""
    return df.groupby("state")["total"].mean().nlargest(n).index.tolist()


def plot_production_trend(df, n_top=10, selected_years=None):
    """
    Plot cement production trends for top producing states.

    Returns: (fig, summary_dict)
    """
    if selected_years:
        df = df[df["year"].isin(selected_years)].copy()

    top_states = get_top_states(df, n_top)
    trend_df = df[df["state"].isin(top_states)].sort_values(["year", "total"], ascending=[True, False])

    # Pivot for year ordering
    year_order = sorted(df["year"].unique())
    fy_order = [df[df["year"] == y]["financial_year"].iloc[0] for y in year_order if y in df["year"].values]

    palette = px.colors.qualitative.Set2 + px.colors.qualitative.Pastel1

    fig = px.line(
        trend_df, x="financial_year", y="total", color="state",
        markers=True,
        labels={"financial_year": "Financial Year", "total": "Total Production (Tonnes)", "state": "State"},
        color_discrete_sequence=palette,
        category_orders={"financial_year": fy_order},
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(family="Inter", size=13),
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5, font=dict(size=11)),
        xaxis=dict(showgrid=False, title_font=dict(size=13), type="category"),
        yaxis=dict(gridcolor="#1e293b", title_font=dict(size=13)),
        margin=dict(l=60, r=30, t=30, b=100),
        height=520, hovermode="x unified",
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=7))

    # Summary stats
    latest_year = max(df["year"])
    latest = df[df["year"] == latest_year]
    summary = {
        "total_production": latest["total"].sum(),
        "top_state": latest.nlargest(1, "total")["state"].values[0] if len(latest) > 0 else "N/A",
        "top_state_production": latest.nlargest(1, "total")["total"].values[0] if len(latest) > 0 else 0,
        "n_producing_states": latest[latest["total"] > 0]["state"].nunique(),
        "n_years": df["year"].nunique(),
        "latest_fy": latest["financial_year"].iloc[0] if len(latest) > 0 else "N/A",
    }

    return fig, summary


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))
    from src.load_data import load_production
    df = load_production()
    fig, s = plot_production_trend(df, n_top=10)
    print("Stats:", s)
    fig.show()
