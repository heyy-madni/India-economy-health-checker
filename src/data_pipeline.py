 #data_pipeline.py

#imports
import pandas as pd
from pathlib import Path
import functions as f
import country_converter as cc 
import os

#dir
BASE_DIR = Path(__file__).resolve().parent.parent
SCR_DIR = BASE_DIR / "src"
SAVE_REPORT_DIR = BASE_DIR / "reports"


def raw_files():
    
    return {
        "GDP_GROWTH": BASE_DIR / "data-file" / "gdp growth.csv",
        "INFLATION": BASE_DIR / "data-file" / "inflation.csv",
        "UNEMPLOYMENT": BASE_DIR / "data-file" / "Unemployment.csv",
        "INCOME_PER_CAPITA": BASE_DIR / "data-file" / "income per capita.csv"
    }

def data_loader(file_path):
    

    with open(file_path) as f:
        df=pd.read_csv(f,on_bad_lines='skip')

    df = df.rename(columns={
        'ï»¿"Country Name"': 'country'})
    
    df.drop(['Indicator Code',\
             'Country Code',\
            'Indicator Name',\
            '2025','1960',\
            'Unnamed: 70'],axis=1,inplace=True)


        
    df = df.melt(id_vars=['country'],var_name='Years',value_name='value')


    return df

def merge_data(gdp_growth_df,inflation_df,unemployment,income_per_capita_df=None):
    df=pd.merge(gdp_growth_df,inflation_df,on=['country', 'Years'],how='outer')
    df=pd.merge(df,unemployment,on=['country', 'Years'],how='outer')
    df=pd.merge(df,income_per_capita_df,on=['country', 'Years'],how='outer') if income_per_capita_df is not None else df
    df.rename(columns={'value_x':'gdp growth',
                   'value_y':'inflation',
                   'value':'unemployment'
                   },inplace=True)
    


    return df

def country_data(country_name,df):  

    
    country_df = df[df['country'] == country_name]
    return country_df


non_countries = [
    "World", "South Asia", "North America", "Sub-Saharan Africa",
    "Middle income", "Upper middle income", "Lower middle income",
    "High income", "Low income", "OECD members",
    "Small states", "Other small states", "Pacific island small states",
    "Post-demographic dividend", "Pre-demographic dividend",
    "Middle East & North Africa", "East Asia & Pacific",
    "Europe & Central Asia", "Latin America & Caribbean","Fragile and conflict affected situations",
    "Euro area","Heavily indebted poor countries","Least developed countries: UN classification","Heavily indebted poor countries (HIPC)"
]
non_country_keywords = [
    "World", "income", "Asia", "Africa", "Europe", "America",
    "Caribbean", "Pacific", "OECD", "IDA", "IBRD", "Arab",
    "demographic", "states", "dividend", "fragile", "blend",
    "Central", "Eastern", "Western", "Southern", "Northern",
    "region", "Region"
]


CACHE_PATH = BASE_DIR / "data-file" / "processed_cache.csv"

if os.path.exists(CACHE_PATH):
    df = pd.read_csv(CACHE_PATH)
    print("Loaded from cache.")
else:

    gdp_growth_df = data_loader(raw_files()["GDP_GROWTH"])
    inflation_df =data_loader(raw_files()["INFLATION"])
    unemployment = data_loader(raw_files()["UNEMPLOYMENT"])
    income_per_capita_df = data_loader(raw_files()["INCOME_PER_CAPITA"])


    df = merge_data(gdp_growth_df,inflation_df,unemployment)
    df = pd.merge(df, income_per_capita_df, on=['country', 'Years'], how='outer')
    df['Years'] = df['Years'].astype(int)
    df['value'] = pd.to_numeric(df['value'], errors='coerce')


    df=df.rename(columns={
    "Years": "Year",
    "gdp growth": "gdp growth",
    "inflation": "Inflation",
    "unemployment": "Unemployment",
    "value": "Income_Per_Capita"
})

    df = df.dropna(subset=["gdp growth", "Inflation", "Unemployment", "Income_Per_Capita"])
    df = df.reset_index(drop=True)


    pattern = "|".join(non_country_keywords)

    df = df[~df["country"].str.contains(pattern, na=False)]
    df = df[~df["country"].isin(non_countries)]



    
    # all the heavy computation goes here
    df["Region"]                = cc.convert(df["country"], to="UNregion")
    df["Unemployment_Change"]   = df.groupby("country")["Unemployment"].diff().round(2)
    df["Condition"]             = df.apply(lambda row: f.get_condition(row, df), axis=1)
    df["Contradiction"]         = df.apply(lambda row: f.detect_contradiction(row, df), axis=1)
    df["Economic_Score"]        = df.apply(lambda row: f.economic_score(row, df), axis=1).round(2)
    df["Insight"]               = df.apply(f.generate_insight, axis=1)
    df["GDP_Predicted"]         = df.groupby("country")["gdp growth"].transform(lambda x: x.rolling(3).mean())
    df["Condition_checker"]     = df.apply(lambda row: f.check_get_condition(row, df), axis=1)
    df["Regime"]                = df.apply(lambda row: f.get_regime(row, df), axis=1)
    
    


    df.to_csv(CACHE_PATH, index=False)
    print("Computed and saved to cache.")




