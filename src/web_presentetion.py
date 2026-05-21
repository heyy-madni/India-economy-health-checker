import streamlit as st
import pandas as pd
from data_pipeline import df as raw_df
from functions import compare_countries, regime_periods, rank_economies


############################### web functions ########################
def country_view_setup():
    pass

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
st.set_page_config(page_title="MacroLens", layout="wide")

# Load data
@st.cache_data
def load_data():
    return raw_df
  

df = load_data()


st.title('MacroLens')
# st.subheader('Global Economic Intelligence — 130+ Countries, 4 Indicators, 20+ Years')
st.sidebar.markdown("---")
st.sidebar.markdown("**Data:** World Bank Open Data")
st.sidebar.markdown("**Built by:** Madni | MacroLens v2.0")

# Sidebar navigation
section = st.sidebar.radio("Navigate", ["Country View", "Regional View", "World View","Data Explorer",])

    
if section == "Country View":

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
            st.line_chart(country_df.set_index("Year")["gdp growth"])

        with col_b:
            st.line_chart(country_df.set_index("Year")["Inflation"])

        col_c,col_d = st.columns(2)
        with col_c:
            st.line_chart(country_df.set_index("Year")["Unemployment"])

        with col_d:
            st.line_chart(country_df.set_index("Year")["Income_Per_Capita"])

    # show = st.toggle("Rank Economies")

    # if show:
    #     st.write(rank_economies(df))
    

    # if st.button("Rank economies"):
    #     top10, bottom10 = rank_economies(df)
    #     st.dataframe(top10)
    #     st.dataframe(bottom10)












elif section == "Regional View":
    pass

elif section == "World View":
    pass



# st.dataframe(df)

