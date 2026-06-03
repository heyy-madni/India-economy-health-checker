import streamlit as st
import pandas as pd
import plotly.graph_objects as go #type:ignore
from data_pipeline import df as raw_df
from functions import  regime_periods, rank_economies

# Page config

st.set_page_config(page_title="MacroLens", layout="wide", initial_sidebar_state="expanded")

# CSS
st.markdown("""
<style>
#MainMenu, footer {visibility: hidden;}
header {visibility: hidden;}

.stApp {
    background-color: #0d1117;
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
}
section[data-testid="stSidebar"] {
    width: 240px !important;
    min-width: 240px !important;
}

.top-header {
    left: 240px;
}
[data-testid="stSidebar"] {
    min-width: 200px !important;
    max-width: 200px !important;
}
[data-testid="stSidebar"][aria-expanded="false"] {
    min-width: 200px !important;
    transform: none !important;
}

section[data-testid="stSidebar"] {
    width: 200px !important;
    min-width: 200px !important;
}
[data-testid="stSidebarCollapsedControl"] {
    display: none;
}            
.block-container {
    padding-top: 100px !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}
            
.top-header {
    position: fixed;
    top: 0;
    left: 200px;
    right: 0;
    z-index: 999;
    background-color: #161b22;
    border-bottom: 1px solid #21262d;
    padding: 16px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
[data-testid="stSidebar"] .stRadio > div {
    gap: 8px;
    padding-top: 8px;
}

[data-testid="stSidebar"] .stRadio label {
    font-size: 15px !important;
    color: #8b949e !important;
    padding: 10px 12px !important;
    border-radius: 8px !important;
    width: 100% !important;
    cursor: pointer !important;
}

[data-testid="stSidebar"] .stRadio label:hover {
    background-color: #21262d !important;
    color: #ffffff !important;
}

[data-testid="stSidebar"] .stRadio label[data-checked="true"] {
    color: #ffffff !important;
    background-color: #21262d !important;
}
            
section[data-testid="stSidebar"] {
    width: 220px !important;
    min-width: 220px !important;
}

.top-header {
    left: 220px;
}


.top-header-title {
    font-size: 24px;
    font-weight: 800;
    color: #ffffff;
}

.top-header-sub {
    font-size: 12px;
    color: #8b949e;
    margin-top: 2px;
}

.metric-card {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 24px;
    min-height: 110px;
}

.metric-label {
    font-size: 13px;
    color: #8b949e;
    margin-bottom: 10px;
}

.metric-value {
    font-size: 30px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 8px;
}

.section-header {
    font-size: 20px;
    font-weight: 600;
    color: #ffffff;
    margin: 24px 0 16px 0;
}

[data-testid="stSidebar"] {
    background-color: #0d1117;
    border-right: 1px solid #21262d;
    padding-top: 80px;
}

.block-container {
    padding-top: 80px !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}
</style>
""", unsafe_allow_html=True)

# top header
st.markdown("""
<div class="top-header">
    <div style="display:flex; align-items:center; gap:12px;">
        <span style="font-size:28px">🌐</span>
        <div>
            <div class="top-header-title">MacroLens</div>
            <div class="top-header-sub">Global Economic Insights at a Glance</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    return raw_df

df = load_data()

# Sidebar
st.sidebar.markdown("""
<div style='padding: 16px 0 8px 0; color: #8b949e; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;'>Navigation</div>
""", unsafe_allow_html=True)

section = st.sidebar.radio("", ["Overview", "Country View", "Regional View", "World View", "Data Explorer"], label_visibility="collapsed")

st.sidebar.markdown("""
<div style='position: fixed; bottom: 24px; font-size: 12px; color: #8b949e;'>
    🌐 Data: World Bank<br>
    Built by: Madni | MacroLens v2.0
</div>
""", unsafe_allow_html=True)

# Delta helper
def delta_html(now, prev, invert=False):
    diff = now - prev
    positive = diff > 0
    if invert: positive = not positive
    color = "#3fb950" if positive else "#f85149"
    arrow = "▲" if diff > 0 else "▼"
    return f'<span style="color:{color}; font-size:13px">{arrow} {abs(diff):.2f} vs last year</span>'

# Plotly layout defaults
def dark_layout(title, height=250):
    return dict(
        title=title,
        paper_bgcolor='#161b22',
        plot_bgcolor='#161b22',
        font=dict(color='#8b949e'),
        margin=dict(l=20, r=20, t=40, b=20),
        height=height,
        xaxis=dict(gridcolor='#21262d'),
        yaxis=dict(gridcolor='#21262d')
    )

############################### OVERVIEW ################################

if section == "Overview":

    latest_year = int(df["Year"].max())
    latest_df = df[df["Year"] == latest_year]
    prev_df = df[df["Year"] == latest_year - 1]

    gdp_now    = latest_df['gdp growth'].mean()
    gdp_prev   = prev_df['gdp growth'].mean()
    inf_now    = latest_df['Inflation'].mean()
    inf_prev   = prev_df['Inflation'].mean()
    unemp_now  = latest_df['Unemployment'].mean()
    unemp_prev = prev_df['Unemployment'].mean()
    inc_now    = latest_df['Income_Per_Capita'].mean()
    inc_prev   = prev_df['Income_Per_Capita'].mean()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Global GDP Growth</div>
            <div class="metric-value">{gdp_now:.1f}%</div>
            {delta_html(gdp_now, gdp_prev)}
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Global Inflation</div>
            <div class="metric-value">{inf_now:.1f}%</div>
            {delta_html(inf_now, inf_prev, invert=True)}
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Global Unemployment</div>
            <div class="metric-value">{unemp_now:.1f}%</div>
            {delta_html(unemp_now, unemp_prev, invert=True)}
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Income Per Capita</div>
            <div class="metric-value">${inc_now:,.0f}</div>
            {delta_html(inc_now, inc_prev)}
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

    global_trend = df[df["Year"] >= 2000].groupby("Year")[["gdp growth", "Inflation"]].mean().reset_index()

    col_a, col_b = st.columns(2)
    with col_a:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=global_trend["Year"], y=global_trend["gdp growth"],
            mode='lines+markers', line=dict(color='#2dd4bf', width=2),
            marker=dict(size=5)
        ))
        fig.update_layout(**dark_layout("Global GDP Growth (%)"))#type:ignore
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=global_trend["Year"], y=global_trend["Inflation"],
            mode='lines+markers', line=dict(color='#f59e0b', width=2),
            marker=dict(size=5)
        ))
        fig2.update_layout(**dark_layout("Global Inflation (%)"))#type:ignore
        fig2.update_yaxes(rangemode='tozero', gridcolor='#21262d')
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Country Overview</div>', unsafe_allow_html=True)
    overview_df = latest_df[["country", "Region", "gdp growth", "Inflation",
                              "Unemployment", "Income_Per_Capita", "Economic_Score"]]\
                  .sort_values("Economic_Score", ascending=False)\
                  .reset_index(drop=True)
    st.dataframe(overview_df, use_container_width=True)


elif section == "Country View":

    if "selected_country" not in st.session_state:
        st.session_state.selected_country = None

    if st.session_state.selected_country is None:
        st.markdown("""
        <div style='padding: 40px 0 24px 0;'>
            <div style='font-size:32px; font-weight:800; color:#ffffff;'>Country View</div>
            <div style='font-size:15px; color:#8b949e; margin-top:8px;'>Select a country to explore its full economic profile</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
        with col1:
            countries = sorted(df["country"].unique())
            default_index = countries.index("India")
            country = st.selectbox("", options=countries, index=default_index, label_visibility="collapsed")
        with col2:
            if st.button('Explore →', use_container_width=True):
                st.session_state.selected_country = country
                st.rerun()
    else:
        country = st.session_state.selected_country
        if st.sidebar.button('← Back to Country Selection'):
            st.session_state.selected_country = None
            st.rerun()

        country_df = df[df["country"] == country].sort_values("Year")
        latest = country_df.iloc[-1]
        region = country_df["Region"].iloc[0]

        st.title(country)
        st.caption(region)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">GDP Growth</div>
                <div class="metric-value">{latest['gdp growth']:.1f}%</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Inflation</div>
                <div class="metric-value">{latest['Inflation']:.1f}%</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Unemployment</div>
                <div class="metric-value">{latest['Unemployment']:.1f}%</div>
            </div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Income Per Capita</div>
                <div class="metric-value">${latest['Income_Per_Capita']:,.0f}</div>
            </div>""", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=country_df["Year"], y=country_df["gdp growth"],
                mode='lines+markers', line=dict(color='#2dd4bf', width=2), marker=dict(size=4)))
            fig1.update_layout(**dark_layout("GDP Growth (%)", height=200))#type:ignore
            fig1.update_xaxes(tickformat='d')
            st.plotly_chart(fig1, use_container_width=True)

        with col_b:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=country_df["Year"], y=country_df["Inflation"],
                mode='lines+markers', line=dict(color='#f59e0b', width=2), marker=dict(size=4)))
            fig2.update_layout(**dark_layout("Inflation (%)", height=200))#type:ignore
            fig2.update_xaxes(tickformat='d')
            st.plotly_chart(fig2, use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=country_df["Year"], y=country_df["Unemployment"],
                mode='lines+markers', line=dict(color='#818cf8', width=2), marker=dict(size=4)))
            fig3.update_layout(**dark_layout("Unemployment (%)", height=200))#type:ignore
            fig3.update_xaxes(tickformat='d')
            st.plotly_chart(fig3, use_container_width=True)

        with col_d:
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(
                x=country_df["Year"], y=country_df["Income_Per_Capita"],
                mode='lines+markers', line=dict(color='#a78bfa', width=2), marker=dict(size=4)))
            fig4.update_layout(**dark_layout("Income Per Capita ($)", height=200))#type:ignore
            fig4.update_xaxes(tickformat='d')
            st.plotly_chart(fig4, use_container_width=True)

        st.subheader("Regime Periods")
        regime_df = regime_periods(df, country)
        st.dataframe(regime_df, use_container_width=True)

elif section == "Regional View":

    col_title, col_region, col_year = st.columns([2, 2, 4])

    with col_title:
        st.markdown("<div style='padding-top:8px'><span style='font-size:28px; font-weight:800; color:#ffffff;'>Regional View</span></div>", unsafe_allow_html=True)

    with col_region:
        regions = sorted(df["Region"].dropna().unique())
        default_index = regions.index("Southern Asia")
        selected_region = st.selectbox("Region", options=regions, index=default_index)

    with col_year:
        year = st.slider("Year",
                         min_value=int(df["Year"].min()),
                         max_value=int(df["Year"].max()),
                         value=2024)

    region_df = df[(df["Region"] == selected_region) & (df["Year"] == year)]
    ranked = region_df[["country", "Economic_Score"]]\
             .dropna()\
             .sort_values("Economic_Score", ascending=True)

    regional_avg = region_df["Economic_Score"].mean()

    # Horizontal Plotly bar chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=ranked["Economic_Score"],
        y=ranked["country"],
        orientation='h',
        marker_color='#2dd4bf',
        text=ranked["Economic_Score"].round(1),
        textposition='outside',
        textfont=dict(color='#ffffff', size=12)
    ))

    # Regional average dashed line
    fig.add_vline(
        x=regional_avg,
        line_dash="dash",
        line_color="#ffffff",
        line_width=1.5,
        annotation_text=f"Regional Avg: {regional_avg:.1f}",
        annotation_position="top",
        annotation_font_color="#ffffff"
    )

    fig.update_layout(
        title=f"Economic Score Ranking ({year})",
        paper_bgcolor='#161b22',
        plot_bgcolor='#161b22',
        font=dict(color='#8b949e'),
        height=max(300, len(ranked) * 35),
        margin=dict(l=20, r=60, t=60, b=20)
    )
    fig.update_xaxes(range=[0, 100], gridcolor='#21262d')
    fig.update_yaxes(gridcolor='#21262d')

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div style='font-size:12px; color:#8b949e;'>Source: World Bank • Economic Score is a composite measure based on growth, inflation, unemployment, and income per capita.</div>", unsafe_allow_html=True)

    # Country comparison section
    st.markdown(f"<div class='section-header'>Selected Country vs Regional Average ({year})</div>", unsafe_allow_html=True)

    countries_in_region = sorted(region_df["country"].dropna().unique())
    selected_country = st.selectbox("Select a country to compare", options=countries_in_region, label_visibility="collapsed")

    country_row = region_df[region_df["country"] == selected_country]
    regional_means = region_df.mean(numeric_only=True)

    if not country_row.empty:
        crow = country_row.iloc[0]

        st.markdown(f"""
        <div style='background:#161b22; border:1px solid #21262d; border-radius:12px; padding:24px; margin-top:12px;'>
            <div style='display:flex; gap:48px; align-items:flex-start;'>
                <div style='min-width:180px;'>
                    <div style='font-size:18px; font-weight:700; color:#2dd4bf;'>{selected_country}</div>
                    <div style='font-size:13px; color:#8b949e; margin-top:4px;'>Economic Score: <b style='color:#ffffff'>{crow['Economic_Score']:.1f}</b></div>
                    <div style='border-top:1px dashed #21262d; margin-top:16px; padding-top:16px;'>
                        <div style='font-size:13px; color:#2dd4bf;'>{selected_region}</div>
                        <div style='font-size:13px; color:#8b949e;'>Regional Average: <b style='color:#ffffff'>{regional_means['Economic_Score']:.1f}</b></div>
                    </div>
                </div>
                <div style='display:grid; grid-template-columns: repeat(4, 1fr); gap:32px; flex:1;'>
                    <div>
                        <div style='font-size:12px; color:#8b949e;'>GDP Growth (%)</div>
                        <div style='font-size:20px; font-weight:700; color:#ffffff; margin:4px 0;'>{crow['gdp growth']:.1f}%</div>
                        <div style='font-size:12px; color:{"#3fb950" if crow["gdp growth"] >= regional_means["gdp growth"] else "#f85149"};'>
                            {"▲" if crow["gdp growth"] >= regional_means["gdp growth"] else "▼"} {abs(crow["gdp growth"] - regional_means["gdp growth"]):.1f} pp
                        </div>
                        <div style='font-size:14px; color:#8b949e; margin-top:12px;'>{regional_means["gdp growth"]:.1f}%</div>
                    </div>
                    <div>
                        <div style='font-size:12px; color:#8b949e;'>Inflation (%)</div>
                        <div style='font-size:20px; font-weight:700; color:#ffffff; margin:4px 0;'>{crow['Inflation']:.1f}%</div>
                        <div style='font-size:12px; color:{"#f85149" if crow["Inflation"] >= regional_means["Inflation"] else "#3fb950"};'>
                            {"▲" if crow["Inflation"] >= regional_means["Inflation"] else "▼"} {abs(crow["Inflation"] - regional_means["Inflation"]):.1f} pp
                        </div>
                        <div style='font-size:14px; color:#8b949e; margin-top:12px;'>{regional_means["Inflation"]:.1f}%</div>
                    </div>
                    <div>
                        <div style='font-size:12px; color:#8b949e;'>Unemployment (%)</div>
                        <div style='font-size:20px; font-weight:700; color:#ffffff; margin:4px 0;'>{crow['Unemployment']:.1f}%</div>
                        <div style='font-size:12px; color:{"#f85149" if crow["Unemployment"] >= regional_means["Unemployment"] else "#3fb950"};'>
                            {"▲" if crow["Unemployment"] >= regional_means["Unemployment"] else "▼"} {abs(crow["Unemployment"] - regional_means["Unemployment"]):.1f} pp
                        </div>
                        <div style='font-size:14px; color:#8b949e; margin-top:12px;'>{regional_means["Unemployment"]:.1f}%</div>
                    </div>
                    <div>
                        <div style='font-size:12px; color:#8b949e;'>Income Per Capita (USD)</div>
                        <div style='font-size:20px; font-weight:700; color:#ffffff; margin:4px 0;'>${crow['Income_Per_Capita']:,.0f}</div>
                        <div style='font-size:12px; color:{"#3fb950" if crow["Income_Per_Capita"] >= regional_means["Income_Per_Capita"] else "#f85149"};'>
                            {"▲" if crow["Income_Per_Capita"] >= regional_means["Income_Per_Capita"] else "▼"} ${abs(crow["Income_Per_Capita"] - regional_means["Income_Per_Capita"]):,.0f}
                        </div>
                        <div style='font-size:14px; color:#8b949e; margin-top:12px;'>${regional_means["Income_Per_Capita"]:,.0f}</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

elif section == "World View":

    col_title, col_year = st.columns([2, 4])
    with col_title:
        st.markdown("<div style='font-size:28px; font-weight:800; color:#ffffff; padding-top:8px;'>World View</div>", unsafe_allow_html=True)
    with col_year:
        year = st.slider("Year",
                         min_value=int(df["Year"].min()),
                         max_value=int(df["Year"].max()),
                         value=2020)

    top10, bottom10 = rank_economies(df, year)
    top10 = top10.copy()
    top10["Economic_Score"] = top10["Economic_Score"].round(2)
    bottom10 = bottom10.copy()
    bottom10["Economic_Score"] = bottom10["Economic_Score"].round(2)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='section-header'>🏆 Top 10 Economies of {year}</div>", unsafe_allow_html=True)
        st.dataframe(
            top10.style.background_gradient(subset=["Economic_Score"], cmap="Greens"),
            use_container_width=True
        )
    with col2:
        st.markdown(f"<div class='section-header'>⚠️ Bottom 10 Economies of {year}</div>", unsafe_allow_html=True)
        st.dataframe(
            bottom10.style.background_gradient(subset=["Economic_Score"], cmap="Reds_r"),
            use_container_width=True
        )

    st.markdown(f"<div class='section-header'>GDP Growth vs Inflation ({year})</div>", unsafe_allow_html=True)

    scatter_df = df[df["Year"] == year].dropna(subset=["gdp growth", "Inflation", "Region"])

    top10_countries = top10["country"].tolist()


    selected_countries = st.multiselect(
        "Select countries to label",
        options=sorted(scatter_df["country"].unique()),
        default=top10_countries
    )

    fig = go.Figure()




    for region in scatter_df["Region"].unique():
        r_df = scatter_df[scatter_df["Region"] == region]
        labeled = r_df[r_df["country"].isin(selected_countries)]

        if not labeled.empty:
            fig.add_trace(go.Scatter(
                x=labeled["gdp growth"],
                y=labeled["Inflation"],
                mode='markers+text',
                name=region,
                text=labeled["country"],
                textposition="top center",
                textfont=dict(size=10, color="#ffffff"),
                marker=dict(size=9, opacity=1),
                hovertext=labeled["country"],
                hoverinfo="text+x+y"
            ))

    fig.update_layout(
        paper_bgcolor='#161b22',
        plot_bgcolor='#161b22',
        font=dict(color='#8b949e'),
        height=500,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(bgcolor='#161b22', bordercolor='#21262d')
    )

    max_inflation = scatter_df[scatter_df["country"].isin(selected_countries)]["Inflation"].max()
    max_gdp = scatter_df[scatter_df["country"].isin(selected_countries)]["gdp growth"].max()
    min_gdp = scatter_df[scatter_df["country"].isin(selected_countries)]["gdp growth"].min()

    y_max = max_inflation * 1.2  # 20% padding above highest point
    x_max = max_gdp * 1.2
    x_min = min(min_gdp * 1.2, -5)


    fig.update_xaxes(gridcolor='#21262d', title="GDP Growth (%)", range=[x_min, x_max])
    fig.update_yaxes(gridcolor='#21262d', title="Inflation (%)", range=[-5, y_max])

    scatter_df = df[df["Year"] == year].dropna(subset=["gdp growth", "Inflation", "Region"])
    scatter_df = scatter_df[scatter_df["Inflation"] <= 40]  # remove hyperinflation outliers
    scatter_df = scatter_df[scatter_df["gdp growth"] >= -20]  # remove extreme GDP crashes


    st.plotly_chart(fig, use_container_width=True)

elif section == "Data Explorer":

    choice = st.selectbox(
        "Info",
        [
            "Countries",
            "Years",
            "Functions",
            "Data Sources",
            "Data"
        ]
    )

    if choice == "Countries":
        num=(df['country'].unique().shape[0])
        st.subheader(f"Countries Supported ({num})")
        st.write(df["country"].unique())

    elif choice == "Years":

        st.subheader("Years Supported")
        st.write(df["Year"].unique())

    elif choice == "Functions":

        st.subheader("Functions Used in the Project")

        st.markdown("""
        - **get_condition** → Determines economic condition based on indicators  
        - **generate_insight** → Creates insights from conditions and contradictions  
        - **check_get_condition** → Checks for contradictions in assigned conditions  
        - **detect_contradiction** → Identifies contradictions in economic data  
        - **get_regime** → Classifies economic regime based on score  
        - **economic_score** → Calculates overall economic score   
        - **regime_periods** → Identifies periods of different economic regimes  
        """)

    elif section == "Data Explorer":

        st.markdown("<div style='font-size:28px; font-weight:800; color:#ffffff; padding:8px 0 4px 0;'>Data Explorer</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:14px; color:#8b949e; margin-bottom:24px;'>Raw dataset — 130+ countries, 4 indicators, sourced from World Bank Open Data</div>", unsafe_allow_html=True)
    
        st.markdown("""
        <div style='background:#161b22; border:1px solid #21262d; border-radius:12px; padding:20px 24px; margin-bottom:24px;'>
            <div style='font-size:15px; font-weight:600; color:#ffffff; margin-bottom:12px;'>Data Sources</div>
            <div style='font-size:13px; color:#8b949e; line-height:2;'>
                <b style='color:#ffffff'>GDP Growth</b> — Annual % growth rate of GDP at constant local currency prices<br>
                <b style='color:#ffffff'>Inflation</b> — Annual % change in consumer price index<br>
                <b style='color:#ffffff'>Unemployment</b> — % of labor force unemployed but actively seeking work<br>
                <b style='color:#ffffff'>Income Per Capita</b> — Gross national income per capita in current US dollars
            </div>
        </div>
        """, unsafe_allow_html=True)
    
        st.dataframe(df, use_container_width=True)





