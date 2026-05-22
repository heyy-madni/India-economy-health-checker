#imports
from matplotlib import pyplot as plt


def over_view_of_economy_chart(df, choice="India"):
    clean = df[df['gdp growth'].between(-20, 25)]
    fig, ax = plt.subplots(figsize=(14, 6))

    # background
    
    fig.patch.set_facecolor('#0f0f0f')
    ax.set_facecolor('#1a1a1a')
    ax.axhline(0, color='#555555', linewidth=0.9, linestyle='--')
   
    plt.grid(color='#2a2a2a', linewidth=0.6)
    # todo
   
    country = clean[clean["country"] == choice]

    # labkels and title
    ax.set_title('country Economic Indicators', fontsize=16,
                 fontweight='bold', color='white', pad=16)
    ax.set_xlabel(f'Year                              country:{choice}', color='#aaaaaa', fontsize=12)
    ax.set_ylabel('Percentage (%)', color='#aaaaaa', fontsize=12)


    # background
    x_ticks = country['Year'][country['Year'] % 5 == 0].tolist()
    ax.tick_params(axis='x', rotation=45)

    x_ticks.append(country['Year'].iloc[-1])  # Ensure the last year is included
    
    ax.set_xticks(x_ticks)


    ax.tick_params(colors='#aaaaaa')
    ax.spines['bottom'].set_color('#333333')
    ax.spines['left'].set_color('#333333')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


      # plot lines
    ax.plot(country['Year'], country['gdp growth'], color="#1cd40b", linewidth=2,
            marker='o', markersize=3, label='GDP Growth (%)', zorder=3)

    ax.plot(country['Year'], country['Inflation'], color="#bd2b06", linewidth=2,
            marker='o', markersize=3, label='Inflation (%)', zorder=3)
   
    ax.plot(country['Year'], country['Unemployment'], color="#06bdbd", linewidth=2,
                marker='o', markersize=3, label='Unemployment', zorder=3   )


    plt.legend(facecolor='#2a2a2a', edgecolor='#444444',labelcolor='white', fontsize=10)
    
    plt.show()

def generate_report(df, country="India"):


    filtered = df[df['country'] == country]
    
    from functions import get_condition, detect_contradiction
    filtered["Condition"]     = filtered.apply(lambda row: get_condition(row, df), axis=1)
    filtered["Contradiction"] = filtered.apply(lambda row: detect_contradiction(row, df), axis=1)
    if filtered.empty:
        print(f"No data found for: {country}")
        return
    
    lines = [f"ECONOMIC REPORT — {country}\n"]
    
    for _, row in filtered.iterrows():
        lines.append(f"• {int(row['Year'])} [{row['country']}]: {row['Condition']} — {row['Contradiction']}")
    
    print("\n".join(lines))

def generate_report_HTML(df, country="India", output_path="economic_report.html"):
    from functions import get_condition, detect_contradiction, economic_score, get_regime

    filtered = df[df["country"] == country].copy()

    if filtered.empty:
        print(f"No data found for: {country}")
        return

    filtered["Condition"] = filtered.apply(get_condition, axis=1)
    filtered["Contradiction"] = filtered.apply(detect_contradiction, axis=1)
    filtered["Economic_Score"] = filtered.apply(economic_score, axis=1)
    filtered["Regime"] = filtered.apply(get_regime, axis=1)
    filtered = filtered.sort_values("Year")

    CONDITION_COLOR = {
        "Healthy Growth":   ("#0d2b1a", "#22c55e"),
        "Stable":           ("#0f1f2e", "#38bdf8"),
        "Stagflation Risk": ("#2b1a00", "#f59e0b"),
        "Inflation Risk":   ("#2b1500", "#f97316"),
        "Recession Signal": ("#2b0d0d", "#ef4444"),
    }

    rows_html = ""
    for _, row in filtered.iterrows():
        bg, accent = CONDITION_COLOR.get(row["Condition"], ("#1a1a1a", "#aaaaaa"))
        score = f"{row['Economic_Score']:.2f}"
        gdp = f"{row['gdp growth']:.2f}%"
        inf = f"{row['Inflation']:.2f}%"
        une = f"{row['Unemployment']:.2f}%"

        rows_html += f"""
        <tr style="background:{bg}; border-left: 3px solid {accent};">
            <td>{int(row['Year'])}</td>
            <td><span class="badge" style="background:{accent}22; color:{accent}; border:1px solid {accent}44">{row['Condition']}</span></td>
            <td>{gdp}</td>
            <td>{inf}</td>
            <td>{une}</td>
            <td style="color:{accent}; font-weight:600">{score}</td>
            <td style="color:#666; font-size:0.8rem">{row['Contradiction']}</td>
            <td><span class="regime-tag">{row['Regime']}</span></td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Economic Report — {country}</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Syne:wght@700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    background: #080b0f;
    color: #c9d1d9;
    font-family: 'IBM Plex Mono', monospace;
    min-height: 100vh;
    padding: 2rem;
  }}

  .header {{
    border-bottom: 1px solid #1e2a38;
    padding-bottom: 1.5rem;
    margin-bottom: 2rem;
  }}

  .header h1 {{
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    color: #f0f6fc;
    letter-spacing: -1px;
  }}

  .header h1 span {{ color: #38bdf8; }}

  .subtitle {{
    margin-top: 0.4rem;
    font-size: 0.78rem;
    color: #4a5568;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }}

  .legend {{
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
  }}

  .legend-item {{
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.72rem;
    color: #8b949e;
  }}

  .legend-dot {{
    width: 8px; height: 8px;
    border-radius: 50%;
  }}

  .table-wrap {{
    overflow-x: auto;
    border-radius: 8px;
    border: 1px solid #1e2a38;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
  }}

  thead tr {{
    background: #0d1117;
    border-bottom: 1px solid #1e2a38;
  }}

  th {{
    padding: 0.75rem 1rem;
    text-align: left;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #4a5568;
    font-weight: 600;
  }}

  td {{
    padding: 0.6rem 1rem;
    border-bottom: 1px solid #0d1117;
    vertical-align: middle;
  }}

  tr:last-child td {{ border-bottom: none; }}

  .badge {{
    display: inline-block;
    padding: 0.2rem 0.55rem;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    white-space: nowrap;
  }}

  .regime-tag {{
    font-size: 0.68rem;
    color: #4a5568;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }}

  .footer {{
    margin-top: 2rem;
    font-size: 0.68rem;
    color: #2d3748;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }}
</style>
</head>
<body>

<div class="header">
  <h1>Economic Report — <span>{country}</span></h1>
  <p class="subtitle">World Bank Indicators · GDP · Inflation · Unemployment · Regime Analysis</p>
</div>

<div class="legend">
  <div class="legend-item"><div class="legend-dot" style="background:#22c55e"></div> Healthy Growth</div>
  <div class="legend-item"><div class="legend-dot" style="background:#38bdf8"></div> Stable</div>
  <div class="legend-item"><div class="legend-dot" style="background:#f59e0b"></div> Stagflation Risk</div>
  <div class="legend-item"><div class="legend-dot" style="background:#f97316"></div> Inflation Risk</div>
  <div class="legend-item"><div class="legend-dot" style="background:#ef4444"></div> Recession Signal</div>
</div>

<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Year</th>
        <th>Condition</th>
        <th>GDP Growth</th>
        <th>Inflation</th>
        <th>Unemployment</th>
        <th>Score</th>
        <th>Contradiction</th>
        <th>Regime</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</div>

<div class="footer">Generated by Simple-Sales-Analytics · {country} Economic Intelligence Layer</div>

</body>
</html>"""
    from data_pipeline import SAVE_REPORT_DIR
    SAVE_REPORT_DIR.mkdir(exist_ok=True)

    with open(SAVE_REPORT_DIR / output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report saved → {output_path}")


