"""
app.py — ASI Cement Production Analysis Dashboard (Multi-Page, Plotly)
Run: py -m streamlit run app.py --server.headless true
"""

import streamlit as st
from src.load_data import load_production, load_fuel_combined
from src.query_production_trend import plot_production_trend
from src.query_energy_mix import plot_energy_mix
from src.query_coal_heatmap import plot_coal_heatmap
from src.query_sankey import plot_sankey
from src.query_cagr import plot_cagr
from src.query_market_concentration import plot_market_concentration

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="India Cement Sector Analysis", page_icon="🏭", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #0e1117; }
    .metric-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #252b3b 100%);
        border: 1px solid #2d3548; border-radius: 12px;
        padding: 1.2rem 1.5rem; text-align: center;
    }
    .metric-card .label { color: #8892a4; font-size: 0.8rem; font-weight: 500;
        text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-card .value { color: #e2e8f0; font-size: 1.8rem; font-weight: 700; margin-top: 0.25rem; }
    .metric-card .sub { color: #64748b; font-size: 0.75rem; margin-top: 0.2rem; }
    h1 { color: #f1f5f9 !important; font-weight: 700 !important; }
    h2, h3 { color: #cbd5e1 !important; }
    .stSidebar > div { background: #111827; }
</style>
""", unsafe_allow_html=True)


# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def get_production():
    return load_production()

@st.cache_data
def get_fuel():
    return load_fuel_combined()

df_prod = get_production()
df_fuel = get_fuel()


def fmt(val, unit="T"):
    if val >= 1e9: return f"{val / 1e9:.1f}B {unit}"
    if val >= 1e6: return f"{val / 1e6:.1f}M {unit}"
    if val >= 1e3: return f"{val / 1e3:.0f}K {unit}"
    return f"{val:.2f} {unit}"

def kpi_card(label, value, sub):
    return (f'<div class="metric-card"><div class="label">{label}</div>'
            f'<div class="value">{value}</div><div class="sub">{sub}</div></div>')


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏭 Navigation")
    pages = {
        "📈 Production Trend": "trend",
        "📊 State CAGR": "cagr",
        "🏗️ Market Concentration": "concentration",
        "🔥 Energy Mix": "energy",
        "🗺️ Coal Dependency": "heatmap",
        "🌊 Fuel → State Flow": "sankey",
    }
    selected_page = st.radio("Analysis", list(pages.keys()), label_visibility="collapsed")
    page_key = pages[selected_page]

    st.markdown("---")
    st.caption("Source: ASI microdata, MoSPI")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Production Trend
# ══════════════════════════════════════════════════════════════════════════════
if page_key == "trend":
    st.markdown("# 🇮🇳 Cement Production Trends")

    # Page-specific filters
    c1, c2 = st.columns([3, 1])
    all_years = sorted(df_prod["year"].unique())
    fy_labels = df_prod.drop_duplicates("year").set_index("year")["financial_year"]
    with c1:
        sel_years = st.multiselect("Years", all_years, default=all_years,
                                   format_func=lambda y: fy_labels.get(y, str(y)), key="trend_years")
    with c2:
        n_top = st.slider("Top N states", 3, 15, 10, key="trend_n")

    fig, s = plot_production_trend(df_prod, n_top=n_top, selected_years=sel_years)

    cols = st.columns(4)
    for col, args in zip(cols, [
        ("Total Production", fmt(s["total_production"]), f"FY {s['latest_fy']}"),
        ("Top Producer", s["top_state"], fmt(s["top_state_production"])),
        ("Producing States", str(s["n_producing_states"]), f"FY {s['latest_fy']}"),
        ("Years Covered", str(s["n_years"]), "2014-15 to 2020-21"),
    ]):
        col.markdown(kpi_card(*args), unsafe_allow_html=True)

    st.markdown("")
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Energy Mix
# ══════════════════════════════════════════════════════════════════════════════
elif page_key == "energy":
    st.markdown("# 🔥 Energy Mix — Regional Transition")
    st.markdown("Tracking the shift in fuel composition across India's cement sector (Block H consumption data)")

    all_years = sorted(df_fuel["year"].unique())
    fy_labels = df_fuel.drop_duplicates("year").set_index("year")["financial_year"]
    sel_years = st.multiselect("Years", all_years, default=all_years,
                               format_func=lambda y: fy_labels.get(y, str(y)), key="energy_years")

    fig, s = plot_energy_mix(df_fuel, selected_years=sel_years)

    cols = st.columns(4)
    for col, args in zip(cols, [
        ("Total Consumption", f"{s['total_consumption_tj']:,.0f} TJ", f"FY {s['latest_fy']}"),
        ("Dominant Fuel", s["dominant_fuel"], f"{s['dominant_share']:.0f}% of total"),
        ("Years Covered", str(s["n_years"]), "Fuel consumption data"),
        ("Insight", "Coal-heavy", "Sector still dominated by thermal fuels"),
    ]):
        col.markdown(kpi_card(*args), unsafe_allow_html=True)

    st.markdown("")
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Coal Dependency Heatmap
# ══════════════════════════════════════════════════════════════════════════════
elif page_key == "heatmap":
    st.markdown("# 🗺️ Coal Dependency by State")
    st.markdown("Share of coal in each state's total energy consumption (Block H data)")

    all_years = sorted(df_fuel["year"].unique())
    fy_labels = df_fuel.drop_duplicates("year").set_index("year")["financial_year"]
    sel_years = st.multiselect("Years", all_years, default=all_years,
                               format_func=lambda y: fy_labels.get(y, str(y)), key="heat_years")

    fig, s = plot_coal_heatmap(df_fuel, selected_years=sel_years)

    cols = st.columns(4)
    for col, args in zip(cols, [
        ("Avg Coal Share", f"{s['avg_coal_share']:.0f}%", "Across all states & years"),
        ("Most Coal-Dependent", s["highest_coal_state"], "Highest avg coal share"),
        ("Least Coal-Dependent", s["lowest_coal_state"], "Lowest avg coal share"),
        ("States Tracked", str(s["n_states"]), f"{s['n_years']} years"),
    ]):
        col.markdown(kpi_card(*args), unsafe_allow_html=True)

    st.markdown("")
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Sankey Diagram
# ══════════════════════════════════════════════════════════════════════════════
elif page_key == "sankey":
    st.markdown("# 🌊 Fuel Type → State Consumption Flows")
    st.markdown("How different fuel types are consumed across states (Block H data)")

    c1, c2 = st.columns([2, 1])
    all_years = sorted(df_fuel["year"].unique())
    fy_labels = df_fuel.drop_duplicates("year").set_index("year")["financial_year"]
    with c1:
        sel_year = st.selectbox("Year", all_years, index=len(all_years) - 1,
                                format_func=lambda y: fy_labels.get(y, str(y)), key="sankey_year")
    with c2:
        top_n = st.slider("Top N states", 5, 20, 12, key="sankey_n")

    fig, s = plot_sankey(df_fuel, year=sel_year, top_n=top_n)

    cols = st.columns(4)
    for col, args in zip(cols, [
        ("Total Consumption", f"{s['total_consumption_tj']:,.0f} TJ", f"FY {s['fy']}"),
        ("Top Consumer", s["top_consumer"], f"{s['top_consumer_val']:,.0f} TJ"),
        ("States Shown", str(s["n_states"]), "By total consumption"),
        ("Fuel Types", "5", "Coal · Gas · Electricity · Petcoke · Other"),
    ]):
        col.markdown(kpi_card(*args), unsafe_allow_html=True)

    st.markdown("")
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: State CAGR
# ══════════════════════════════════════════════════════════════════════════════
elif page_key == "cagr":
    st.markdown("# 📊 State-wise CAGR of Cement Production")
    st.markdown("Compound Annual Growth Rate — which states are growing, which are declining?")

    all_years = sorted(df_prod["year"].unique())
    fy_labels = df_prod.drop_duplicates("year").set_index("year")["financial_year"]
    sel_years = st.multiselect("Years", all_years, default=all_years,
                               format_func=lambda y: fy_labels.get(y, str(y)), key="cagr_years")

    fig, s = plot_cagr(df_prod, selected_years=sel_years)

    if fig:
        cols = st.columns(4)
        for col, args in zip(cols, [
            ("Period", s["period"], f"{s['n_states']} states"),
            ("Fastest Growing", s["fastest_state"], f"{s['fastest_cagr']:+.1f}% CAGR"),
            ("Steepest Decline", s["slowest_state"], f"{s['slowest_cagr']:+.1f}% CAGR"),
            ("Growing vs Declining", f"{s['growing']} / {s['declining']}", "Growth / Decline"),
        ]):
            col.markdown(kpi_card(*args), unsafe_allow_html=True)

        st.markdown("")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Not enough years to compute CAGR.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Market Concentration
# ══════════════════════════════════════════════════════════════════════════════
elif page_key == "concentration":
    st.markdown("# 🏗️ Market Concentration — Pareto Analysis")
    st.markdown("The 80/20 rule: how few states produce the bulk of India's cement?")

    all_years = sorted(df_prod["year"].unique())
    fy_labels = df_prod.drop_duplicates("year").set_index("year")["financial_year"]
    sel_year = st.selectbox("Year", all_years, index=len(all_years) - 1,
                            format_func=lambda y: fy_labels.get(y, str(y)), key="conc_year")

    fig, s = plot_market_concentration(df_prod, selected_years=[sel_year])

    if fig:
        cols = st.columns(4)
        for col, args in zip(cols, [
            ("80% Threshold", f"{s['pareto_states']} states", f"of {s['total_states']} producing states"),
            ("Their Share", f"{s['latest_share']:.0f}%", f"FY {s['latest_fy']}"),
            ("Top 3", ", ".join(s["top_states"][:3]), "By production volume"),
            ("National Output", fmt(s["national_total"]), f"FY {s['latest_fy']}"),
        ]):
            col.markdown(kpi_card(*args), unsafe_allow_html=True)

        st.markdown("")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Not enough data.")

