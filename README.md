# ⚽ Football Player Performance Analytics Dashboard

A portfolio-quality, interactive football (soccer) analytics dashboard built with **Python**, **Streamlit**, **Pandas**, and **Plotly**.

> ⚠️ **Data Notice:** All player and club data in this project is **entirely synthetic**, generated with a fixed random seed (42) for reproducibility. No statistics represent real players, clubs, or match results.

---

## Features

| Page | What you get |
|---|---|
| **Overview** | 5 KPI cards (players, goals, assists, minutes, avg rating), top-10 goals & rating charts, searchable stats table, CSV download |
| **Player Analysis** | Goals vs Assists scatter, Shots vs Goals scatter with trendline, side-by-side radar comparison for any two players |
| **Team Analysis** | Grouped goals/assists bar, avg rating bar, squad size bar — all per team |
| **Position Analysis** | Box plots for goals & rating, bar charts for avg tackles & pass accuracy — all per position |
| **Sidebar Filters** | Season, Team (multi), Position (multi), Player name search — all reactive |

---

## Prerequisites

- Python **3.10** or later
- `pip`

---

## Local Setup

```bash
# 1. Clone or download the project
git clone https://github.com/your-username/football-analytics-dashboard.git
cd football-analytics-dashboard

# 2. (Recommended) Create a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The dashboard opens automatically at `http://localhost:8501`.

> The dataset (`football_players.csv`) is included in the repository and loaded directly by `app.py`.  
> If you ever need to regenerate it, run `python generate_data.py` first.

---

## Project Structure

```
football analysis/
├── app.py                    # Main Streamlit application (all pages & logic)
├── football_players.csv      # Synthetic dataset — 300 rows, 18 columns
├── generate_data.py          # One-off data generation script (keep for reference)
├── requirements.txt          # Pinned Python dependencies
└── README.md                 # This file
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web app framework |
| `pandas` | Data loading, filtering, aggregation |
| `numpy` | Numeric operations, data generation |
| `plotly` | Interactive charts (Express + Graph Objects) |

---

## Deploying to Streamlit Cloud

1. Push the project to a **public GitHub repository**.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** → select your repo and branch.
4. Set **Main file path** to `app.py`.
5. Click **Deploy** — done. No secrets or environment variables required.

---

## Dataset Schema

| Column | Type | Description |
|---|---|---|
| `player_id` | int | Unique player identifier |
| `name` | str | Synthetic full name |
| `team` | str | One of 10 fictional clubs |
| `position` | str | Goalkeeper / Defender / Midfielder / Forward |
| `season` | str | 2021-22, 2022-23, or 2023-24 |
| `age` | int | 18–36 |
| `nationality` | str | One of 20 countries |
| `appearances` | int | Games played in the season |
| `minutes_played` | int | Total minutes on the pitch |
| `goals` | int | Goals scored |
| `assists` | int | Goal assists |
| `shots` | int | Total shots |
| `passes` | int | Total passes |
| `pass_accuracy` | float | Pass completion % |
| `tackles` | int | Tackles made |
| `yellow_cards` | int | Yellow cards received |
| `red_cards` | int | Red cards received |
| `rating` | float | Overall match rating (5.0–9.5) |

---

## License

MIT — free to use, modify, and distribute for personal and commercial projects.
