"""
query_market_concentration.py — Pareto Analysis of Cement Production
Bar chart (descending production) + cumulative % line with 80% threshold.
Shows how few states account for the majority of national output.
"""

import plotly.graph_objects as go
import pandas as pd


def plot_market_concentration(df_prod, top_n=None, selected_years=None):
    """
    Pareto chart: bars = state production (desc), line = cumulative %.
    80% line highlights the Pareto threshold.

    Returns: (fig, summary_dict)
    """
    df = df_prod.copy()
    if selected_years:
        df = df[df["year"].isin(selected_years)]

    # Use latest year for the Pareto snapshot
    latest_year = df["year"].max()
    latest = df[df["year"] == latest_year].copy()
    fy_label = latest["financial_year"].iloc[0] if len(latest) > 0 else str(latest_year)

    # Aggregate by state, sort descending
    state_totals = latest.groupby("state")["total"].sum().sort_values(ascending=False)
    state_totals = state_totals[state_totals > 0]  # drop zero-production states

    national_total = state_totals.sum()
    cumulative_pct = state_totals.cumsum() / national_total * 100

    # Find 80% threshold
    states_for_80 = (cumulative_pct <= 80).sum() + 1  # +1 because the state that crosses 80% counts
    states_for_80 = min(states_for_80, len(state_totals))

    fig = go.Figure()

    # Bars — color states inside 80% differently
    bar_colors = ["#3b82f6" if i < states_for_80 else "#1e293b" for i in range(len(state_totals))]

    fig.add_trace(go.Bar(
        x=state_totals.index.tolist(),
        y=state_totals.values,
        name="Production (Tonnes)",
        marker_color=bar_colors,
        hovertemplate="%{x}: %{y:,.0f} T<extra></extra>",
        yaxis="y",
    ))

    # Cumulative % line
    fig.add_trace(go.Scatter(
        x=cumulative_pct.index.tolist(),
        y=cumulative_pct.values,
        name="Cumulative %",
        mode="lines+markers",
        line=dict(color="#f59e0b", width=2.5),
        marker=dict(size=5),
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
        yaxis="y2",
    ))

    # 80% threshold line
    fig.add_hline(
        y=80, line_dash="dash", line_color="#ef4444", line_width=1.5,
        annotation_text="80%", annotation_position="right",
        annotation_font=dict(color="#ef4444", size=12),
        yref="y2",
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(family="Inter", size=12),
        xaxis=dict(title="State", showgrid=False, type="category",
                   tickangle=-45, tickfont=dict(size=10)),
        yaxis=dict(title="Production (Tonnes)", gridcolor="#1e293b",
                   side="left"),
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right",
                    range=[0, 105], showgrid=False,
                    ticksuffix="%"),
        legend=dict(orientation="h", yanchor="top", y=-0.35, xanchor="center", x=0.5),
        margin=dict(l=70, r=70, t=30, b=120),
        height=520, hovermode="x unified",
        bargap=0.15,
    )

    # Top states list (those within 80%)
    top_states = state_totals.index[:states_for_80].tolist()

    summary = {
        "top_n": states_for_80,
        "top_states": top_states,
        "latest_share": cumulative_pct.iloc[states_for_80 - 1] if states_for_80 > 0 else 0,
        "earliest_share": cumulative_pct.iloc[states_for_80 - 1] if states_for_80 > 0 else 0,
        "trend": f"{states_for_80} of {len(state_totals)} states",
        "latest_fy": fy_label,
        "n_years": df["year"].nunique(),
        "national_total": national_total,
        "pareto_states": states_for_80,
        "total_states": len(state_totals),
    }

    return fig, summary


if __name__ == "__main__":
    from load_data import load_production
    fig, s = plot_market_concentration(load_production())
    print(f"Pareto: {s['pareto_states']} of {s['total_states']} states produce {s['latest_share']:.0f}%")
    print("Top states:", s["top_states"])
    fig.show()
