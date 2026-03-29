import pandas as pd
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent.parent
SCR_DIR = BASE_DIR / "src"
DATA_FILE = BASE_DIR / "data-file" / "data file.csv"



df = pd.read_csv(DATA_FILE)





# metris 


df["GDP_Growth"] = df["GDP"].pct_change() * 100
df["Unemployment_Change"] = df["Unemployment"].diff()

# remove nan 
df = df.dropna()

# print(df.head())


def get_condition(row):

    
    if row["GDP_Growth"] < -2:
        return "Recession Signal"
    
    elif row["Inflation"] > 8 and row["GDP_Growth"] < 2:
        return "Stagflation Risk"
    
    elif row["GDP_Growth"] > 3 and row["Unemployment_Change"] < 0:
        return "Healthy Growth"
    
    elif row["Inflation"] > 8:
        return "Inflation Risk"
    
    else:
        return "Stable"

def detect_contradiction(row):
    if row["GDP_Growth"] > 3 and row["Unemployment_Change"] > 0:
        return "Jobless Growth"
    
    elif row["GDP_Growth"] < 0 and row["Unemployment_Change"] < 0:
        return "Data Contradiction / Lag Effect"
    
    else:
        return "No Contradiction"
    

df["Condition"] = df.apply(get_condition, axis=1)
df["Contradiction"] = df.apply(detect_contradiction, axis=1)
print(df.any)
