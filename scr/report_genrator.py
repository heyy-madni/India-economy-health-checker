from main import df #type: ignore










   
def generate_report():
    lines = []                         
    lines.append("INDIA ECONOMIC REPORT\n")
    
    for _, row in df.iterrows():
        lines.append(f"• {row['Year']}: {row['Condition_Summary']}")   
    
    print("\n".join(lines))


if __name__ == "__main__":
    report = generate_report()
    print(report)