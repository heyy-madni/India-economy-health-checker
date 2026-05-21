# functions.py
import streamlit as st
import os
from report_genrator import over_view_of_economy_chart, generate_report
import pandas as pd

####################### helpers ########################

def normalize_country(name: str) -> str:
    if not name or not name.strip():
        return "India"
    
    name = name.strip()
    aliases = {
        "india": "India",
        "usa": "United States", "us": "United States",
        "united states": "United States", "america": "United States",
        "uk": "United Kingdom", "britain": "United Kingdom", "england": "United Kingdom",
        "china": "China", "prc": "China",
        "uae": "United Arab Emirates",
        "russia": "Russian Federation",
        "south korea": "Korea, Rep.", "korea": "Korea, Rep.",
        "iran": "Iran, Islamic Rep.",
        "egypt": "Egypt, Arab Rep.",
        "venezuela": "Venezuela, RB",
        "vietnam": "Viet Nam",
        "turkey": "Turkiye",
    }
    return aliases.get(name.lower(), name.title())

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')



_baseline_cache = {}

def get_regional_baseline(df, country, year, agg):
    cache_key = (country, int(year), agg)
    if cache_key in _baseline_cache:
        return _baseline_cache[cache_key]

    country_rows = df[df["country"] == country]
    if country_rows.empty or "Region" not in country_rows.columns:
        result = pd.Series(dtype=float)
    else:
        region = country_rows["Region"].iloc[0]
        regional_df = df[(df["Region"] == region) & (df["Year"] == int(year))]
        result = pd.Series(dtype=float) if regional_df.empty else getattr(regional_df, agg)(numeric_only=True)

    _baseline_cache[cache_key] = result
    return result


####################### data functions ########################

def get_condition(row, df):
    country = row["country"]
    year    = row["Year"]

    mean   = get_regional_baseline(df, country, year, 'mean')
    std    = get_regional_baseline(df, country, year, 'std')

    if mean.empty or std.empty:
        return "Stable"

    gdp_mean         = mean.get('gdp growth', 0)
    gdp_std          = std.get('gdp growth', 2)
    inflation_mean   = mean.get('Inflation', 5)
    inflation_std    = std.get('Inflation', 3)
    unemp_mean       = mean.get('Unemployment', 6)
    unemp_std        = std.get('Unemployment', 2)
    income_mean      = mean.get('Income_Per_Capita', 10000)
    income_std       = std.get('Income_Per_Capita', 5000)

    # Derived thresholds
    gdp_low          = gdp_mean - gdp_std        # recession threshold
    gdp_high         = gdp_mean + gdp_std        # strong growth threshold
    inflation_high   = inflation_mean + inflation_std   # high inflation threshold
    unemp_high       = unemp_mean + unemp_std    # high unemployment threshold
    unemp_low        = unemp_mean - unemp_std    # low unemployment threshold
    income_low       = income_mean - income_std  # low income threshold

    if row["gdp growth"] < gdp_low:
        return "Recession Signal"

    elif row["gdp growth"] < 0 and row["Inflation"] > inflation_high and row["Unemployment"] > unemp_high:
        return "Recession Signal"

    elif row["Inflation"] > inflation_high and row["gdp growth"] < gdp_mean and row["Unemployment"] > unemp_mean:
        return "Stagflation Risk"

    elif row["Income_Per_Capita"] < income_low:
        return "Low Income Alert"

    elif row["Income_Per_Capita"] > income_mean:
        return "High Income Alert"

    elif row["gdp growth"] > gdp_high and row["Unemployment"] < unemp_low and row["Inflation"] < inflation_mean:
        return "Healthy Growth"

    elif row["Inflation"] > inflation_high:
        return "Inflation Risk"

    else:
        return "Stable"

def generate_insight(row):
    condition    = row["Condition"]
    contradiction = row["Contradiction"]
    score        = row["Economic_Score"]
    gdp          = row["gdp growth"]
    inflation    = row["Inflation"]
    unemp        = row["Unemployment"]

    base = f"{int(row['Year'])}: {condition}"

    if contradiction != "No Contradiction":
        base += f" — {contradiction}"

    if score >= 70:
        base += f" (Strong economy, score {score})"
    elif score <= 30:
        base += f" (Weak economy, score {score})"

    if gdp < 0:
        base += f" | GDP contracting at {gdp:.1f}%"
    if inflation > 10:
        base += f" | High inflation {inflation:.1f}%"
    if unemp > 15:
        base += f" | High unemployment {unemp:.1f}%"

    return base

def check_get_condition(row, df):
    condition = get_condition(row, df)
    contradictions = []

    country = row["country"]
    year    = row["Year"]

    mean = get_regional_baseline(df, country, year, 'mean')
    std  = get_regional_baseline(df, country, year, 'std')

    if mean.empty or std.empty:
        return None

    gdp_mean       = mean.get('gdp growth', 0)
    gdp_std        = std.get('gdp growth', 2)
    inflation_mean = mean.get('Inflation', 5)
    inflation_std  = std.get('Inflation', 3)

    gdp_high       = gdp_mean + gdp_std
    gdp_low        = gdp_mean - gdp_std
    inflation_high = inflation_mean + inflation_std
    inflation_low  = inflation_mean - inflation_std

    if condition == "Healthy Growth" and row["Inflation"] > inflation_high:
        contradictions.append("High Inflation despite Healthy Growth label")
    if condition == "Stable" and row["gdp growth"] < gdp_low:
        contradictions.append("Near-recession GDP despite Stable label")
    if condition == "Recession Signal" and row["Unemployment"] < 0:
        contradictions.append("Unemployment falling despite Recession label")
    if condition == "Stagflation Risk" and row["gdp growth"] > gdp_high:
        contradictions.append("Strong growth despite Stagflation label")
    if condition == "Inflation Risk" and row["gdp growth"] > gdp_high:
        contradictions.append("Strong growth despite Inflation Risk label")
    if condition == "Inflation Risk" and row["Unemployment"] < 0:
        contradictions.append("Falling Unemployment despite Inflation Risk label")
    if condition == "Recession Signal" and row["Inflation"] < inflation_low:
        contradictions.append("Low Inflation despite Recession label")
    if condition == "Stable" and row["Inflation"] > inflation_high:
        contradictions.append("High Inflation despite Stable label")

    return contradictions if contradictions else None

def detect_contradiction(row, df):
    country = row["country"]
    year    = row["Year"]

    mean = get_regional_baseline(df, country, year, 'mean')
    std  = get_regional_baseline(df, country, year, 'std')

    if mean.empty or std.empty:
        return "No Contradiction"

    gdp_mean       = mean.get('gdp growth', 0)
    gdp_std        = std.get('gdp growth', 2)
    inflation_mean = mean.get('Inflation', 5)
    inflation_std  = std.get('Inflation', 3)

    gdp_high       = gdp_mean + gdp_std
    inflation_high = inflation_mean + inflation_std

    if row["gdp growth"] > gdp_high and row["Unemployment"] > 0:
        return "Jobless Growth"

    elif row["gdp growth"] < 0 and row["Unemployment"] < 0:
        return "Data Contradiction"

    elif row["Inflation"] > inflation_high and row["gdp growth"] > gdp_high:
        return "Growth with High Inflation"

    else:
        return "No Contradiction"

def get_regime(row, df):
    country = row["country"]
    year    = row["Year"]

    mean = get_regional_baseline(df, country, year, 'mean')
    std  = get_regional_baseline(df, country, year, 'std')

    if mean.empty or std.empty:
        return "Transition"

    score_mean = mean.get('Economic_Score', 50)
    score_std  = std.get('Economic_Score', 10)

    score_high = score_mean + score_std
    score_low  = score_mean - score_std

    if row["Economic_Score"] > score_high:
        return "Expansion"
    elif row["Economic_Score"] < score_low:
        return "Crisis"
    else:
        return "Transition"



def economic_score(row, df=None):
    gdp       = row.get("gdp growth", 0)
    unemp     = row.get("Unemployment", 6)
    inflation = row.get("Inflation", 2)
    income    = row.get("Income_Per_Capita", 0)

    # Use regional income benchmark if df available, else fallback
    if df is not None:
        mean = get_regional_baseline(df, row["country"], row["Year"], 'mean')
        income_benchmark = mean.get('Income_Per_Capita', 12416.13) if not mean.empty else 12416.13
    else:
        income_benchmark = 12416.13

    score  = gdp * 4
    score -= unemp * 3
    score -= max(0, inflation - 2) * 2
    score += (income / income_benchmark) * 3

    MIN_SCORE, MAX_SCORE = -40, 60
    normalized = (score - MIN_SCORE) / (MAX_SCORE - MIN_SCORE) * 100
    return round(max(0, min(100, normalized)), 2)

def compare_countries(df, country1=None, country2=None, country3=None, year: int = 2020):
    countries = df["country"].unique()
    if country1 is None: country1 = countries[0]
    if country2 is None: country2 = countries[1]
    if country3 is None: country3 = countries[2]

    c1_df = df[(df["country"] == country1) & (df["Year"] == year)]
    c2_df = df[(df["country"] == country2) & (df["Year"] == year)]
    c3_df = df[(df["country"] == country3) & (df["Year"] == year)]

    if c1_df.empty or c2_df.empty or c3_df.empty:
        return [f"Data not found for one or more countries in {year}."]

    c1, c2, c3 = c1_df.iloc[0], c2_df.iloc[0], c3_df.iloc[0]

    insights = []
    for label, c in [(country1, c1), (country2, c2), (country3, c3)]:
        mean = get_regional_baseline(df, label, year, 'mean')

        if not mean.empty:
            gdp_mean       = mean.get('gdp growth', 0)
            inflation_mean = mean.get('Inflation', 0)
            unemp_mean     = mean.get('Unemployment', 0)
            score_mean     = mean.get('Economic_Score', 0)

            insights.append(
                f"{label} in {year}: {c.Condition} | Score: {c.Economic_Score} "
                f"(regional avg: {score_mean:.2f}) | "
                f"GDP: {c['gdp growth']:.2f}% (regional avg: {gdp_mean:.2f}%) | "
                f"Inflation: {c.Inflation:.2f}% (regional avg: {inflation_mean:.2f}%) | "
                f"Unemployment: {c.Unemployment:.2f}% (regional avg: {unemp_mean:.2f}%)\n"
            )
        else:
            insights.append(f"{label} in {year}: {c.Condition} with {c.Contradiction} and Economic Score of {c.Economic_Score}\n")

    pairs = [(country1, c1, country2, c2), (country1, c1, country3, c3)]
    for n1, d1, n2, d2 in pairs:
        insights.append(f"Comparison: {n1} has {'higher' if d1.Economic_Score > d2.Economic_Score else 'lower'} economic score than {n2}\n")
        insights.append(f"Comparison: {n1} has {'higher' if d1.Inflation > d2.Inflation else 'lower'} Inflation than {n2}\n")
        insights.append(f"Comparison: {n1} has {'higher' if d1.Unemployment > d2.Unemployment else 'lower'} Unemployment than {n2}\n")

    return insights

def regime_periods(df, country="India"):
    df = df[df["country"] == country].copy()
    df["Regime_change"] = df["Regime"] != df["Regime"].shift()
    df["Regime_ID"] = df["Regime_change"].cumsum()

    return df.groupby("Regime_ID").agg(
        Country=("country", "first"),
        Regime=("Regime", "first"),
        Start=("Year", "min"),
        End=("Year", "max"),
        Avg_Score=("Economic_Score", "mean")
    ).reset_index(drop=True)

def back_testing(df, year: int, country="India"):
    filtered_df = df[(df["Year"] == year) & (df["country"] == country)]
    if filtered_df.empty:
        print(f"No data for {country} in {year}.")
        return

    mean = get_regional_baseline(df, country, year, 'mean')

    for row in filtered_df.itertuples(index=False):
        print(f"{row.Year} {row.country}: {row.Condition} | Score: {row.Economic_Score}", end="")
        if not mean.empty:
            print(f" (regional avg: {mean.get('Economic_Score', 0):.2f})", end="")
        print(f" | {row.Contradiction}")

def rank_economies(df, year=2005):
    yearly = df[df["Year"] == year][["country", "Economic_Score", "Region"]].dropna()
    ranked = yearly.sort_values("Economic_Score", ascending=False).reset_index(drop=True)
    ranked.index += 1
    
    top10 = ranked.head(10)
    bottom10 = ranked.tail(10)
    
    return top10, bottom10


####################### menu functions ########################
    # fw3cf

def choice_1(df):
    clear_console()
    raw = input("Enter the country for overview (default: India): ").strip()
    country = normalize_country(raw) if raw else "India"
    if country not in df["country"].values:
        print(f"Country '{country}' not found in data. Defaulting to India.")
        country = "India"
    clear_console()
    over_view_of_economy_chart(df=df, choice=country)
    input("Press Enter to return to the menu...")
    clear_console()

def choice_2(df, country):
    clear_console()
    generate_report(df, country=country)
    input("Press Enter to return to the menu...")
    clear_console()

def choice_3(df):
    clear_console()
    print("Back Testing Options:")
    print("1. Custom Year Back Testing")
    print("2. Regime Periods")
    print("3. Condition Checker")
    choice = input("Enter your choice: ")

    if choice == "1":
        year = int(input("Enter the Year for back testing ex (2005): "))
        country = normalize_country(input("Enter the country for back testing ex (india): ")).strip()

        back_testing(df,year,country)
        input("Press Enter to return to the menu...")
    elif choice == "2":
        country = normalize_country(input("Enter the country (default: India): ") or "India")
        print(regime_periods(df, country))
        input("Press Enter to return to the menu...")
    elif choice == "3":
        country = normalize_country(input("Enter the country (default: India): ") or "India")
        choice_3_3(df, country)
        input("Press Enter to return to the menu...")

def choice_3_3(df, country):
    clear_console()
    filtered_df = df[df["country"] == country].copy()
    
    if filtered_df.empty:
        print(f"No data found for '{country}'.")
        input("Press Enter to return to the menu...")
        return

    filtered_df["Condition_checker"] = filtered_df["Condition_checker"].apply(
        lambda x: " | ".join(x) if isinstance(x, list) else "None"
    )

    result = filtered_df[["Year", "country", "Condition", "Condition_checker"]]
    print("Condition Checker Results:")

    col_widths = {col: max(result[col].astype(str).map(len).max(), len(col)) for col in result.columns}
    header    = "  ".join(col.ljust(col_widths[col]) for col in result.columns)
    separator = "  ".join("-" * col_widths[col] for col in result.columns)
    print(header)
    print(separator)
    for _, row in result.iterrows():
        print("  ".join(str(row[col]).ljust(col_widths[col]) for col in result.columns))

    input("Press Enter to return to the menu...")
    clear_console()

def choice_4(df):
    clear_console()
    country1 = normalize_country(input("Enter the first country (default: India): ") or "India")
    country2 = normalize_country(input("Enter the second country (default: USA): ") or "United States")
    country3 = normalize_country(input("Enter the third country (default: China): ") or "China")
    year_input = input("Enter the year for comparison (default: 2020): ")
    year = int(year_input) if year_input else 2020

    clear_console()
    for line in compare_countries(df, country1, country2, country3, year):
        print(line)
    input("Press Enter to return to the menu...")
    clear_console()

def choice_5(df):
    choice = input("""
 1. List of countries supported
 2. List of years supported
 3. Functions used in the project and their purpose
 4. Data sources and their description
 5. Back to menu
""")

    if choice == "5":
        return
    elif choice == "1":
        print("Countries supported:")
        print(df["country"].unique())
    elif choice == "2":
        print("Years supported:")
        print(df["Year"].unique())
    elif choice == "3":
        print("Functions used in the project and their purpose:")
        print("- get_condition: Determines economic condition based on indicators")
        print("- generate_insight: Creates insights from conditions and contradictions")
        print("- check_get_condition: Checks for contradictions in assigned conditions")
        print("- detect_contradiction: Identifies contradictions in economic data")
        print("- get_regime: Classifies economic regime based on score")
        print("- economic_score: Calculates an overall economic score")
        print("- compare_countries: Compares economic indicators between countries")
        print("- regime_periods: Identifies periods of different economic regimes")
        print("- back_testing: Tests conditions against historical data")
    elif choice == "4":
        print("Data sources and their description:")
        print("Source: World Bank")
        print("1. GDP Growth: Annual % growth rate of GDP at constant local currency prices.")
        print("2. Inflation: Annual % change in consumer price index.")
        print("3. Unemployment: % of labor force unemployed but actively seeking work.")
        print("4. Income_Per_Capita: Gross national Income_Per_Capita in current US dollars.")
    else:
        print("Invalid choice. Returning to menu.")



















