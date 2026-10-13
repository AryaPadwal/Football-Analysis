# Football Player Performance Analytics Dashboard — Implementation Plan

## Top-Level Overview

Build a self-contained, portfolio-quality Streamlit dashboard for analysing and comparing synthetic
football (soccer) player data. The project is created from scratch in an empty workspace and consists
of four files: `football_players.csv`, `app.py`, `requirements.txt`, and `README.md`. All KPIs and
rankings are derived at runtime from the dataset. The UI follows a dark, football-inspired green
pitch theme using Plotly for all charts.

---

## Dataset Schema

File: `football_players.csv`

| Column | Type | Description |
|---|---|---|
| `player_id` | int | Unique player identifier (1–N) |
| `name` | str | Synthetic full name |
| `team` | str | One of 10 fictional club names |
| `position` | str | Goalkeeper / Defender / Midfielder / Forward |
| `season` | str | One of "2021-22", "2022-23", "2023-24" |
| `age` | int | 18–36 |
| `nationality` | str | One of ~20 countries |
| `appearances` | int | 1–38 |
| `minutes_played` | int | appearances × ~70–90 |
| `goals` | int | Position-realistic range |
| `assists` | int | Position-realistic range |
| `shots` | int | goals × ~3–8 |
| `passes` | int | 20–100 per game × appearances |
| `pass_accuracy` | float | 55–95 % |
| `tackles` | int | Position-realistic range |
| `yellow_cards` | int | 0–10 |
| `red_cards` | int | 0–3 |
| `rating` | float | 5.0–9.5 (1 dp) |

Seed: `numpy.random.seed(42)` — fully reproducible. A `DATA_NOTICE` banner is displayed in the
app confirming all data is synthetic.

---

## KPI Calculations

All metrics are computed with Pandas from the filtered DataFrame (never hardcoded).

| KPI Card | Calculation |
|---|---|
| Total Players | `df['player_id'].nunique()` |
| Total Goals | `df['goals'].sum()` |
| Total Assists | `df['assists'].sum()` |
| Total Minutes Played | `df['minutes_played'].sum()` |
| Avg Player Rating | `df['rating'].mean()` rounded to 2 dp |

---

## Project Structure

```
football analysis/
├── app.py                  # Main Streamlit application
├── football_players.csv    # Synthetic dataset (generated once, committed)
├── requirements.txt        # Pinned dependencies
└── README.md               # Setup and deployment instructions
```

`app.py` internal module layout (functions, not separate files — beginner-friendly):

```
app.py
 ├── load_data()            # Read CSV, validate, handle missing values
 ├── apply_filters()        # Apply sidebar selections → filtered DataFrame
 ├── render_sidebar()       # Season / Team / Position / Player filters
 ├── page_overview()        # KPI cards + top-performers table
 ├── page_player()          # Scatter plots, comparison, shots analysis
 ├── page_team()            # Bar charts for team-level aggregates
 ├── page_position()        # Position breakdown charts
 └── main()                 # Page router + layout config
```

---

## Sub-Tasks

---

### Sub-Task 1 — Generate the Synthetic Dataset

**Intent**  
Produce `football_players.csv` with realistic, position-aware statistics for ≥ 100 players across
3 seasons, 10 teams and 4 positions. This file is the single source of truth for the entire app.

**Expected Outcomes**
- `football_players.csv` exists in the workspace root.
- Contains ≥ 300 rows (100 players × 3 seasons).
- All columns listed in the schema are present with correct dtypes and no null values.
- Seed 42 makes the file reproducible.
- Goals/assists/shots distributions are position-realistic (GK lowest, FW highest).

**Todo List**
1. Write a standalone Python script (`generate_data.py`) using NumPy and Pandas.
2. Define 10 team names, 4 position labels, 3 seasons, ~20 nationalities, 100 player base names.
3. For each player, assign a fixed team, position and age; loop over 3 seasons to generate per-season rows.
4. Apply position-specific multipliers for goals, assists, shots and tackles.
5. Derive `minutes_played` from `appearances` with small random variance.
6. Clamp all counts to non-negative integers; clip `rating` to [5.0, 9.5].
7. Write the result to `football_players.csv` and delete `generate_data.py` (data is pre-generated).

**Relevant Context**  
No existing files. Use `numpy.random.seed(42)` at the top of the generation script.

**Status** `[ ] pending`

---

### Sub-Task 2 — Create `requirements.txt`

**Intent**  
Pin the exact dependency versions needed so any reviewer can reproduce the environment with one
command.

**Expected Outcomes**
- `requirements.txt` exists and lists only the packages the app actually imports.
- No extraneous dependencies.

**Todo List**
1. Identify all imports used across `app.py` and the data-generation script.
2. Resolve compatible versions: `streamlit`, `pandas`, `numpy`, `plotly`.
3. Write `requirements.txt` with one package per line, pinned to minor version (e.g. `streamlit>=1.32,<2`).

**Relevant Context**  
Target Python 3.10+. Streamlit 1.32+ supports `st.columns` with gap parameter and `st.metric`.

**Status** `[ ] pending`

---

### Sub-Task 3 — Build `app.py` — Layout, Theme & Data Loading

**Intent**  
Establish the Streamlit page config, dark green pitch theme (via custom CSS injected with
`st.markdown`), the `load_data()` function with validation, and the sidebar filter controls.

**Expected Outcomes**
- Running `streamlit run app.py` opens a dark-themed dashboard without errors.
- Sidebar shows Season / Team / Position / Player multi-select or selectbox widgets.
- Any missing or malformed CSV rows are dropped with a visible warning, not a crash.
- A synthetic-data disclaimer banner is visible on every page.

**Todo List**
1. Set `st.set_page_config` (title, wide layout, football icon favicon).
2. Inject CSS for dark background (`#0a1628`), green accent (`#00ff87`), card styling and font.
3. Implement `load_data()`: read CSV, coerce dtypes, drop rows with nulls in critical columns,
   show `st.warning` if any rows were dropped.
4. Implement `render_sidebar()`: Season selectbox (includes "All"), Team / Position multi-selects,
   Player search text input.
5. Implement `apply_filters()`: chain filter conditions; return full DataFrame when "All" is selected.
6. Add synthetic-data notice with `st.info` at top of every page render.

**Relevant Context**  
CSS is injected via `st.markdown(..., unsafe_allow_html=True)`. Keep CSS minimal — only override
background, text colour, metric card border and sidebar colour.

**Status** `[ ] pending`

---

### Sub-Task 4 — Build the Overview Page

**Intent**  
Deliver the first page: five KPI metric cards and a searchable, sortable top-performers table.

**Expected Outcomes**
- Five `st.metric` cards show Total Players, Total Goals, Total Assists, Total Minutes and Avg Rating.
- A Plotly horizontal bar chart shows top-10 players by goals.
- A Plotly horizontal bar chart shows top-10 players by rating.
- A `st.dataframe` table below the charts is searchable and scrollable.
- A `st.download_button` exports the filtered data as CSV.

**Todo List**
1. Implement `page_overview(df)` function.
2. Calculate all five KPIs from `df` using Pandas aggregations.
3. Render KPI cards in a single `st.columns(5)` row using `st.metric`.
4. Build top-10 goals bar chart with Plotly Express `px.bar`, horizontal, green bars.
5. Build top-10 rating bar chart with `px.bar`, horizontal, teal bars.
6. Render `st.dataframe(df, use_container_width=True)` with column config for numeric formatting.
7. Add `st.download_button` that calls `df.to_csv(index=False).encode('utf-8')`.

**Relevant Context**  
Use `st.columns` with `gap="medium"` for card layout. Plotly figures should use
`template="plotly_dark"` and a transparent background to blend with the CSS theme.

**Status** `[ ] pending`

---

### Sub-Task 5 — Build the Player Analysis Page

**Intent**  
Deliver interactive player-level analysis: a Goals vs Assists scatter plot, a Shots vs Goals
scatter plot, and a side-by-side player comparison radar chart.

**Expected Outcomes**
- Goals vs Assists scatter: each point is a player, coloured by position, sized by rating, with
  hover showing name, team and minutes played.
- Shots vs Goals scatter: each point is a player, colour-coded by team.
- Player comparison section: user picks two players from selectboxes; a Plotly radar chart
  overlays their normalised stats (goals, assists, passes, tackles, rating).
- All charts use dark theme and green accent colours.

**Todo List**
1. Implement `page_player(df)` function.
2. Build Goals vs Assists `px.scatter` with `color="position"`, `size="rating"`,
   `hover_data=["name","team","minutes_played"]`.
3. Build Shots vs Goals `px.scatter` with `color="team"`, trendline via Plotly (OLS).
4. Add two `st.selectbox` widgets for player A and player B from the filtered player list.
5. Extract per-player row for each; normalise stats to 0–1 range using column min/max from full df.
6. Build Plotly radar (polar) chart with two traces, one per player; fill semi-transparent.
7. Show a `st.table` of raw stats for the two selected players below the radar.

**Relevant Context**  
Radar chart uses `go.Scatterpolar`. Normalise against the full unfiltered dataset so the scale
is stable regardless of sidebar filters.

**Status** `[ ] pending`

---

### Sub-Task 6 — Build the Team Analysis Page

**Intent**  
Aggregate player-level data to team level and visualise team performance comparisons.

**Expected Outcomes**
- Grouped bar chart: total goals and assists per team.
- Bar chart: average player rating per team, sorted descending.
- Bar chart: squad size (player count) per team.
- All charts labelled clearly with team names on the axis.

**Todo List**
1. Implement `page_team(df)` function.
2. Group `df` by `team`: sum goals, sum assists, mean rating, count unique players.
3. Build `px.bar` for goals + assists using `barmode="group"`.
4. Build `px.bar` for avg rating sorted descending, coloured by rating value.
5. Build `px.bar` for squad size.
6. Arrange in a 2-column layout: goals/assists chart full-width top; rating and squad side by side.

**Relevant Context**  
When sidebar filters by team, the team page automatically scopes to selected teams only — this
is handled by `apply_filters()` upstream.

**Status** `[ ] pending`

---

### Sub-Task 7 — Build the Position Analysis Page

**Intent**  
Show how stats differ across the four position groups (GK, DEF, MID, FWD) to contextualise
individual player comparisons.

**Expected Outcomes**
- Box plot: goals distribution per position.
- Box plot: rating distribution per position.
- Bar chart: average tackles per position.
- Bar chart: average pass accuracy per position.
- Colour coding matches the position colours used in the Player Analysis scatter plots.

**Todo List**
1. Implement `page_position(df)` function.
2. Build `px.box` for goals by position using consistent position colour map.
3. Build `px.box` for rating by position.
4. Build `px.bar` for mean tackles per position.
5. Build `px.bar` for mean pass accuracy per position.
6. Arrange in a 2×2 grid using `st.columns(2)`.

**Relevant Context**  
Use a fixed `color_discrete_map` dict for positions so colours are identical across all pages:
`{"Goalkeeper": "#e74c3c", "Defender": "#3498db", "Midfielder": "#f39c12", "Forward": "#2ecc71"}`.

**Status** `[ ] pending`

---

### Sub-Task 8 — Write `README.md`

**Intent**  
Provide clear, copy-paste-ready instructions for local setup and cloud deployment so the project
is portfolio-ready.

**Expected Outcomes**
- `README.md` covers: project description, screenshot placeholder, prerequisites, local setup
  (clone → venv → pip install → streamlit run), Streamlit Cloud deployment steps, project
  structure table, and the synthetic-data disclaimer.

**Todo List**
1. Write project overview section with feature bullet list.
2. Write prerequisites section (Python 3.10+, pip).
3. Write local setup section with shell commands.
4. Write Streamlit Cloud deployment section (push to GitHub → connect repo → set main file).
5. Write project structure table.
6. Add data disclaimer section.

**Relevant Context**  
No external APIs or secrets are needed — deployment is straightforward one-click on Streamlit Cloud.

**Status** `[ ] pending`

---

## Page Navigation

The app uses a `st.sidebar.radio` for page selection:

```
● Overview
● Player Analysis
● Team Analysis
● Position Analysis
```

The `main()` function reads the selection and calls the corresponding `page_*()` function, passing
the filtered DataFrame.

---

## Dependency Graph

```
football_players.csv
       │
       ▼
  load_data()
       │
       ▼
render_sidebar() ──► apply_filters() ──► filtered df
                                              │
                    ┌─────────────────────────┼──────────────────────┐
                    ▼                         ▼                       ▼
            page_overview()          page_player()          page_team()
                                                                      │
                                                            page_position()
```

---

## Input Validation & Error Handling Strategy

| Scenario | Handling |
|---|---|
| CSV file missing | `st.error` with path hint, `st.stop()` |
| CSV has unexpected columns | Log warning, continue with available columns |
| Filter produces empty DataFrame | `st.warning("No players match the current filters.")`, skip chart rendering |
| Player comparison — same player selected twice | `st.info` notice, still renders (identical traces) |
| Numeric columns contain nulls | Drop affected rows in `load_data()`, show count in `st.warning` |
