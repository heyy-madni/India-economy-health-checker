import streamlit as st
import pandas as pd
from data_pipeline import df as raw_df
from functions import  regime_periods, rank_economies


############################### web functions ########################


#for me 
# ''' #   Column               Non-Null Count  Dtype  
# ---  ------               --------------  -----  
#  0   country              5283 non-null   str    
#  1   Year                 5283 non-null   int64  
#  2   gdp growth           5283 non-null   float64
#  3   Inflation            5283 non-null   float64
#  4   Unemployment         5283 non-null   float64
#  5   Income_Per_Capita    5283 non-null   float64
#  6   Region               5283 non-null   str    
#  7   Unemployment_Change  5114 non-null   float64
#  8   Condition            5283 non-null   str    
#  9   Contradiction        5283 non-null   str    
#  10  Economic_Score       5283 non-null   float64
#  11  Insight              5283 non-null   str    
#  12  GDP_Predicted        4945 non-null   float64
#  13  Condition_checker    121 non-null    object 
#  14  Regime               5283 non-null   str  '''


# Page config
st.set_page_config(page_title="MacroLens", layout="wide", initial_sidebar_state="expanded")

# Load data
@st.cache_data
def load_data():
    return raw_df
  

df = load_data()


# st.subheader('Global Economic Intelligence — 130+ Countries, 4 Indicators, 20+ Years')
st.sidebar.markdown("---")
st.sidebar.markdown("**Data:** World Bank Open Data")
st.sidebar.markdown("**Built by:** Madni | MacroLens v2.0")

# Sidebar navigation
section = st.sidebar.radio("Navigate", ["Overview", "Country View", "Regional View", "World View", "Data Explorer"])

if section == "Overview":
    
    st.title("🌐 MacroLens")
    st.caption("Global Economic Insights at a Glance")
    
    # Latest year global averages
    latest_year = int(df["Year"].max())
    latest_df = df[df["Year"] == latest_year]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Global GDP Growth", f"{latest_df['gdp growth'].mean():.1f}%")
    with col2:
        st.metric("Global Inflation", f"{latest_df['Inflation'].mean():.1f}%")
    with col3:
        st.metric("Global Unemployment", f"{latest_df['Unemployment'].mean():.1f}%")
    with col4:
        st.metric("Avg Income Per Capita", f"${latest_df['Income_Per_Capita'].mean():,.0f}")
    
    # Global trends
    global_trend = df.groupby("Year")[["gdp growth", "Inflation"]].mean()
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Global GDP Growth (%)")
        st.line_chart(global_trend["gdp growth"], height=200)
    with col_b:
        st.subheader("Global Inflation (%)")
        st.line_chart(global_trend["Inflation"], height=200)
    
    # Country table
    st.subheader("Country Overview")
    overview_df = latest_df[["country", "Region", "gdp growth", "Inflation", 
                              "Unemployment", "Income_Per_Capita", "Economic_Score"]]\
                  .sort_values("Economic_Score", ascending=False)\
                  .reset_index(drop=True)
    st.dataframe(overview_df, use_container_width=True)


elif section == "Country View":

    if "selected_country" not in st.session_state:
        st.session_state.selected_country = None


    if st.session_state.selected_country is None:
        st.title('Country View')
        st.write("Select a country to explore its economy")

        country = st.selectbox("Enter your country", options=sorted(df["country"].unique()))
        if st.button('Explore →'):
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
            st.metric("GDP Growth", f"{latest['gdp growth']:.1f}%")
        with col2:
            st.metric("Inflation", f"{latest['Inflation']:.1f}%")
        with col3:
            st.metric('Unemployment', f"{latest['Unemployment']:.1f}%")
        with col4:
            st.metric('Income Per Capita', f"${latest['Income_Per_Capita']:,.0f}")


        col_a,col_b = st.columns(2)

        with col_a:
            st.line_chart(country_df.set_index("Year")["gdp growth"],height=150)

        with col_b:
            st.line_chart(country_df.set_index("Year")["Inflation"],height=150)

        col_c,col_d = st.columns(2)
        with col_c:
            st.line_chart(country_df.set_index("Year")["Unemployment"] ,height=150)

        with col_d:
            st.line_chart(country_df.set_index("Year")["Income_Per_Capita"],height=150)

        st.subheader("Regime Periods")
        regime_df = regime_periods(df, country)
        st.dataframe(regime_df, use_container_width=True)

elif section == "Regional View":
    
    col_title, col_region, col_year = st.columns([2, 2, 4])
    
    with col_title:
        st.title("Regional View")
    
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

    st.subheader(f"Economic Score Ranking ({year})")
    st.bar_chart(ranked.set_index("country")["Economic_Score"],height=350)


    # Country selector filtered to region
    countries_in_region = sorted(region_df["country"].dropna().unique())
    selected_country = st.selectbox("Select a country to compare", options=countries_in_region)

    # Get country row and regional averages
    country_row = region_df[region_df["country"] == selected_country]
    regional_avg = region_df.mean(numeric_only=True)

    if not country_row.empty:
        crow = country_row.iloc[0]

        st.subheader(f"{selected_country} vs {selected_region} Average ({year})")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("GDP Growth", f"{crow['gdp growth']:.1f}%", 
                      delta=f"{crow['gdp growth'] - regional_avg['gdp growth']:.1f}%")
        with col2:
            st.metric("Inflation", f"{crow['Inflation']:.1f}%",
                      delta=f"{crow['Inflation'] - regional_avg['Inflation']:.1f}%")
        with col3:
            st.metric("Unemployment", f"{crow['Unemployment']:.1f}%",
                      delta=f"{crow['Unemployment'] - regional_avg['Unemployment']:.1f}%")
        with col4:
            st.metric("Income Per Capita", f"${crow['Income_Per_Capita']:,.0f}",
                      delta=f"${crow['Income_Per_Capita'] - regional_avg['Income_Per_Capita']:,.0f}")

elif section == "World View":
    
    st.title("World View")
    
    year = st.slider("Select Year",
                     min_value=int(df["Year"].min()),
                     max_value=int(df["Year"].max()),
                     value=2020)
    
    top10, bottom10 = rank_economies(df, year)
    
    col1, col2 = st.columns(2)
    
    with col1:

        st.subheader(f"🏆 Top 10 Economies of {year}")
        st.dataframe(top10, use_container_width=True)
    
    with col2:
        st.subheader(f"⚠️ Bottom 10 Economies of {year}")
        st.dataframe(bottom10, use_container_width=True)

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

    elif choice == "Data Sources":

        st.subheader("Data Sources")

        st.markdown("""
        **Source:** World Bank

        1. **GDP Growth**  
           Annual % growth rate of GDP at constant local currency prices.

        2. **Inflation**  
           Annual % change in consumer price index.

        3. **Unemployment**  
           % of labor force unemployed but actively seeking work.

        4. **Income Per Capita**  
           Gross national income per capita in current US dollars.
        """)

    elif choice == "Data":
            st.dataframe(df)
    
    else:
        st.error("Invalid choice.")





