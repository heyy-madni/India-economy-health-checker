#main.py


from data_pipeline import df
from data_pipeline import SCR_DIR
import subprocess
import sys
#todo add multi country in Regime Periods & Condition Checker
#todo use income per capita 
#todo refactor menu and add library






if __name__ == "__main__":
    try:
        file =SCR_DIR / "web_presentetion.py"
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(file)])
    except Exception as e :
        print(f"An error occurred: {e}")