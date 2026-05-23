# functions.py
import pandas as pd

####################### helpers ########################


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

def compute_global_benchmarks(df):
    return {
        "gdp growth": float(df["gdp growth"].mean()),
        "Inflation": float(df["Inflation"].mean()),
        "Unemployment": float(df["Unemployment"].mean()),
        "Income_Per_Capita": float(df["Income_Per_Capita"].mean())
    }

####################### pipeline functions ########################

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
    score = row["Economic_Score"]
    country = row["country"]
    year = row["Year"]
    
    # get previous year score
    prev = df[(df["country"] == country) & (df["Year"] == year - 1)]
    prev_score = prev["Economic_Score"].iloc[0] if not prev.empty else score
    
    improving = score > prev_score

    if score >= 65:
        return "Expansion"
    elif score <= 35 and not improving:
        return "Crisis"
    elif score <= 35 and improving:
        return "Recovery"
    else:
        return "Transition"

def economic_score(row, df):
    year_df = df[df["Year"] == row["Year"]]
    
    gdp_pct   = year_df["gdp growth"].rank(pct=True)[row.name] * 100
    inc_pct   = year_df["Income_Per_Capita"].rank(pct=True)[row.name] * 100
    unemp_pct = (1 - year_df["Unemployment"].rank(pct=True)[row.name]) * 100
    inf_pct   = (1 - year_df["Inflation"].rank(pct=True)[row.name]) * 100

    return round((gdp_pct * 0.25 + inc_pct * 0.35 + unemp_pct * 0.2 + inf_pct * 0.2), 2)

####################### data functions ########################

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


def rank_economies(df, year=2005):
    yearly = df[df["Year"] == year][["country", "Economic_Score", "Region"]].dropna()
    ranked = yearly.sort_values("Economic_Score", ascending=False).reset_index(drop=True)
    ranked.index += 1
    
    top10 = ranked.head(10)
    bottom10 = ranked.tail(10)
    
    return top10, bottom10


















