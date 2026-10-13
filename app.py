"""
Football Player Performance Analytics Dashboard
================================================
All data is SYNTHETIC — generated with a fixed random seed (42) for reproducibility.
This dashboard does not represent real players, clubs, or match results.

Run locally:
    pip install -r requirements.txt
    streamlit run app.py
"""

import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ── Constants ─────────────────────────────────────────────────────────────────

DATA_FILE = "football_players.csv"

POSITION_COLORS = {
    "Goalkeeper": "#e74c3c",
    "Defender":   "#3498db",
    "Midfielder": "#f39c12",
    "Forward":    "#2ecc71",
}

CRITICAL_COLUMNS = [
    "player_id", "name", "team", "position", "season",
    "goals", "assists", "shots", "passes", "pass_accuracy",
    "tackles", "minutes_played", "rating", "appearances",
]

RADAR_STATS   = ["goals", "assists", "passes", "tackles", "rating"]
RADAR_LABELS  = ["Goals", "Assists", "Passes", "Tackles", "Rating"]

# ── CSS Theme ─────────────────────────────────────────────────────────────────

CUSTOM_CSS = """
<style>
/* ── Global dark background ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #0a1628 !important;
    color: #e8eaf0 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #0d1f3c !important;
    border-right: 1px solid #1e3a5f;
}
[data-testid="stSidebar"] * {
    color: #c8d8f0 !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background-color: #0f2744;
    border: 1px solid #00ff87;
    border-radius: 10px;
    padding: 16px;
}
[data-testid="stMetricLabel"] { color: #a0b4cc !important; font-size: 0.78rem; }
[data-testid="stMetricValue"] { color: #00ff87 !important; font-size: 1.6rem; font-weight: 700; }

/* ── Section headers ── */
h1, h2, h3 { color: #00ff87 !important; }

/* ── Plotly chart containers ── */
.stPlotlyChart { border-radius: 8px; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border: 1px solid #1e3a5f; border-radius: 8px; }

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background-color: #00ff87 !important;
    color: #0a1628 !important;
    font-weight: 700;
    border: none;
    border-radius: 6px;
}

/* ── Info / warning banners ── */
[data-testid="stAlert"] { border-radius: 8px; }
</style>
"""

# ── Data loading ──────────────────────────────────────────────────────────────

@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and validate football_players.csv.  Returns a clean DataFrame."""
    if not os.path.exists(DATA_FILE):
        st.error(
            f"Dataset not found: **{DATA_FILE}**\n\n"
            "Run `python generate_data.py` to create it, then restart the app."
        )
        st.stop()

    df = pd.read_csv(DATA_FILE)

    # Check required columns
    missing_cols = [c for c in CRITICAL_COLUMNS if c not in df.columns]
    if missing_cols:
        st.error(f"CSV is missing required columns: {missing_cols}")
        st.stop()

    # Coerce numeric columns
    numeric_cols = [
        "goals", "assists", "shots", "passes", "tackles",
        "minutes_played", "appearances", "rating", "pass_accuracy",
        "yellow_cards", "red_cards", "age",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with nulls in critical numeric columns
    before = len(df)
    df = df.dropna(subset=CRITICAL_COLUMNS)
    dropped = before - len(df)
    if dropped > 0:
        st.warning(f"Dropped {dropped} row(s) with missing values in critical columns.")

    # Ensure non-negative counts
    for col in ["goals", "assists", "shots", "tackles", "appearances", "minutes_played"]:
        df[col] = df[col].clip(lower=0)

    df["rating"] = df["rating"].clip(lower=5.0, upper=9.5)

    return df.reset_index(drop=True)

# ── Sidebar filters ───────────────────────────────────────────────────────────

def render_sidebar(df: pd.DataFrame) -> dict:
    """Render sidebar widgets and return the current filter selections."""
    st.sidebar.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Football_pictogram.svg/"
        "200px-Football_pictogram.svg.png",
        width=60,
    )
    st.sidebar.markdown("## ⚽ Filters")

    seasons = ["All"] + sorted(df["season"].unique().tolist())
    season = st.sidebar.selectbox("Season", seasons)

    teams = sorted(df["team"].unique().tolist())
    selected_teams = st.sidebar.multiselect("Team", teams, default=teams)

    positions = sorted(df["position"].unique().tolist())
    selected_positions = st.sidebar.multiselect("Position", positions, default=positions)

    player_search = st.sidebar.text_input("Search player name", "")

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "⚠️ All data is **synthetic** and does not represent real players or clubs."
    )

    return {
        "season": season,
        "teams": selected_teams,
        "positions": selected_positions,
        "player_search": player_search,
    }


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply sidebar filter selections to the DataFrame."""
    fdf = df.copy()

    if filters["season"] != "All":
        fdf = fdf[fdf["season"] == filters["season"]]

    if filters["teams"]:
        fdf = fdf[fdf["team"].isin(filters["teams"])]
    else:
        fdf = fdf.iloc[0:0]  # empty — no team selected

    if filters["positions"]:
        fdf = fdf[fdf["position"].isin(filters["positions"])]
    else:
        fdf = fdf.iloc[0:0]

    if filters["player_search"].strip():
        q = filters["player_search"].strip().lower()
        fdf = fdf[fdf["name"].str.lower().str.contains(q, na=False)]

    return fdf.reset_index(drop=True)


def _empty_guard(df: pd.DataFrame) -> bool:
    """Return True (and show a warning) if the DataFrame is empty."""
    if df.empty:
        st.warning("No players match the current filters. Adjust the sidebar selections.")
        return True
    return False


def _chart_layout(fig, title: str = "", height: int = 400):
    """Apply consistent dark theme layout to a Plotly figure."""
    fig.update_layout(
        title=title,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,39,68,0.6)",
        font=dict(color="#c8d8f0"),
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig

# ── Overview page ─────────────────────────────────────────────────────────────

def page_overview(df: pd.DataFrame):
    st.title("📊 Overview")
    st.info("ℹ️ All statistics are **synthetic** — generated for demonstration purposes only.", icon=None)

    if _empty_guard(df):
        return

    # ── KPI cards ──
    total_players  = df["player_id"].nunique()
    total_goals    = int(df["goals"].sum())
    total_assists  = int(df["assists"].sum())
    total_minutes  = int(df["minutes_played"].sum())
    avg_rating     = round(float(df["rating"].mean()), 2)

    c1, c2, c3, c4, c5 = st.columns(5, gap="medium")
    c1.metric("👥 Total Players",    f"{total_players:,}")
    c2.metric("⚽ Total Goals",      f"{total_goals:,}")
    c3.metric("🎯 Total Assists",    f"{total_assists:,}")
    c4.metric("⏱️ Minutes Played",  f"{total_minutes:,}")
    c5.metric("⭐ Avg Rating",       f"{avg_rating}")

    st.markdown("---")

    # ── Top performers charts ──
    col_left, col_right = st.columns(2, gap="medium")

    with col_left:
        st.subheader("Top 10 — Goals")
        top_goals = (
            df.groupby(["name", "team"], as_index=False)["goals"]
            .sum()
            .nlargest(10, "goals")
            .sort_values("goals")
        )
        fig_goals = px.bar(
            top_goals, x="goals", y="name",
            orientation="h",
            color_discrete_sequence=["#00ff87"],
            hover_data={"team": True, "goals": True, "name": False},
            labels={"goals": "Goals", "name": "Player"},
        )
        _chart_layout(fig_goals, height=380)
        st.plotly_chart(fig_goals, use_container_width=True)

    with col_right:
        st.subheader("Top 10 — Rating")
        top_rating = (
            df.groupby(["name", "team"], as_index=False)["rating"]
            .mean()
            .round(2)
            .nlargest(10, "rating")
            .sort_values("rating")
        )
        fig_rating = px.bar(
            top_rating, x="rating", y="name",
            orientation="h",
            color_discrete_sequence=["#00b4d8"],
            hover_data={"team": True, "rating": True, "name": False},
            labels={"rating": "Avg Rating", "name": "Player"},
        )
        _chart_layout(fig_rating, height=380)
        st.plotly_chart(fig_rating, use_container_width=True)

    st.markdown("---")
    st.subheader("Player Statistics Table")

    display_cols = [
        "name", "team", "position", "season", "age", "nationality",
        "appearances", "goals", "assists", "shots", "passes",
        "pass_accuracy", "tackles", "yellow_cards", "red_cards", "rating",
    ]
    st.dataframe(
        df[[c for c in display_cols if c in df.columns]],
        use_container_width=True,
        height=400,
        column_config={
            "pass_accuracy": st.column_config.NumberColumn("Pass Acc (%)", format="%.1f"),
            "rating":        st.column_config.NumberColumn("Rating", format="%.1f"),
        },
    )

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download filtered data as CSV",
        data=csv_bytes,
        file_name="football_players_filtered.csv",
        mime="text/csv",
    )

# ── Player Analysis page ──────────────────────────────────────────────────────

def page_player(df: pd.DataFrame, full_df: pd.DataFrame):
    st.title("🔍 Player Analysis")
    st.info("ℹ️ All statistics are **synthetic** — generated for demonstration purposes only.", icon=None)

    if _empty_guard(df):
        return

    # ── Goals vs Assists scatter ──
    st.subheader("Goals vs Assists")
    fig_ga = px.scatter(
        df, x="assists", y="goals",
        color="position",
        size="rating",
        size_max=18,
        hover_data={"name": True, "team": True, "minutes_played": True, "position": True},
        color_discrete_map=POSITION_COLORS,
        labels={"assists": "Assists", "goals": "Goals", "position": "Position"},
    )
    _chart_layout(fig_ga, height=450)
    st.plotly_chart(fig_ga, use_container_width=True)

    # ── Shots vs Goals scatter ──
    st.subheader("Shots vs Goals")
    try:
        fig_sg = px.scatter(
            df, x="shots", y="goals",
            color="team",
            trendline="ols",
            hover_data={"name": True, "position": True},
            labels={"shots": "Shots", "goals": "Goals", "team": "Team"},
        )
    except Exception:
        # trendline requires statsmodels; fall back gracefully
        fig_sg = px.scatter(
            df, x="shots", y="goals",
            color="team",
            hover_data={"name": True, "position": True},
            labels={"shots": "Shots", "goals": "Goals", "team": "Team"},
        )
    _chart_layout(fig_sg, height=450)
    st.plotly_chart(fig_sg, use_container_width=True)

    st.markdown("---")

    # ── Player Comparison radar ──
    st.subheader("Player Comparison")
    player_names = sorted(df["name"].unique().tolist())
    if len(player_names) < 2:
        st.info("Select at least two players using the sidebar filters to enable comparison.")
        return

    col_a, col_b = st.columns(2)
    with col_a:
        player_a = st.selectbox("Player A", player_names, index=0, key="pa")
    with col_b:
        player_b = st.selectbox("Player B", player_names, index=min(1, len(player_names) - 1), key="pb")

    if player_a == player_b:
        st.info("Both selections are the same player — the radar traces will overlap.")

    # Aggregate across seasons for the two players (sum goals/assists/shots/tackles/passes; mean rating)
    def get_player_stats(name: str, source_df: pd.DataFrame) -> pd.Series:
        p = source_df[source_df["name"] == name]
        if p.empty:
            return pd.Series({s: 0.0 for s in RADAR_STATS})
        return pd.Series({
            "goals":   p["goals"].sum(),
            "assists": p["assists"].sum(),
            "passes":  p["passes"].sum(),
            "tackles": p["tackles"].sum(),
            "rating":  p["rating"].mean(),
        })

    # Normalise against full dataset range for stability
    def normalise(val: float, col: str) -> float:
        lo = float(full_df[col].min()) if col != "rating" else 5.0
        hi = float(full_df[col].max()) if col != "rating" else 9.5
        if hi == lo:
            return 0.5
        return float(np.clip((val - lo) / (hi - lo), 0.0, 1.0))

    stats_a = get_player_stats(player_a, df)
    stats_b = get_player_stats(player_b, df)

    norm_a = [normalise(stats_a[s], s) for s in RADAR_STATS]
    norm_b = [normalise(stats_b[s], s) for s in RADAR_STATS]

    fig_radar = go.Figure()
    for label, norm_vals, raw_vals, color in [
        (player_a, norm_a, stats_a, "#00ff87"),
        (player_b, norm_b, stats_b, "#f39c12"),
    ]:
        hover_text = "<br>".join(
            f"{RADAR_LABELS[i]}: {raw_vals[RADAR_STATS[i]]:.1f}"
            for i in range(len(RADAR_STATS))
        )
        fig_radar.add_trace(go.Scatterpolar(
            r=norm_vals + [norm_vals[0]],
            theta=RADAR_LABELS + [RADAR_LABELS[0]],
            fill="toself",
            fillcolor=color.replace(")", ",0.15)").replace("rgb(", "rgba(").replace("#", ""),
            line=dict(color=color, width=2),
            name=label,
            hovertext=hover_text,
            hoverinfo="text+name",
        ))

    fig_radar.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        polar=dict(
            bgcolor="rgba(15,39,68,0.6)",
            radialaxis=dict(visible=True, range=[0, 1], showticklabels=False),
            angularaxis=dict(color="#c8d8f0"),
        ),
        font=dict(color="#c8d8f0"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15),
        height=450,
        margin=dict(l=40, r=40, t=40, b=60),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # Raw stats table for selected players
    raw_compare = pd.DataFrame([stats_a, stats_b], index=[player_a, player_b]).round(2)
    raw_compare.columns = RADAR_LABELS
    st.table(raw_compare)

# ── Team Analysis page ────────────────────────────────────────────────────────

def page_team(df: pd.DataFrame):
    st.title("🏟️ Team Analysis")
    st.info("ℹ️ All statistics are **synthetic** — generated for demonstration purposes only.", icon=None)

    if _empty_guard(df):
        return

    team_agg = (
        df.groupby("team", as_index=False)
        .agg(
            total_goals=("goals",    "sum"),
            total_assists=("assists", "sum"),
            avg_rating=("rating",    "mean"),
            players=("player_id",   "nunique"),
        )
        .round({"avg_rating": 2})
    )

    # ── Goals & Assists grouped bar ──
    st.subheader("Goals & Assists by Team")
    fig_ga = px.bar(
        team_agg.melt(id_vars="team", value_vars=["total_goals", "total_assists"],
                      var_name="Metric", value_name="Count"),
        x="team", y="Count", color="Metric",
        barmode="group",
        color_discrete_map={"total_goals": "#00ff87", "total_assists": "#00b4d8"},
        labels={"team": "Team", "Count": "Count", "Metric": ""},
    )
    fig_ga.for_each_trace(lambda t: t.update(
        name="Goals" if t.name == "total_goals" else "Assists"
    ))
    _chart_layout(fig_ga, height=400)
    st.plotly_chart(fig_ga, use_container_width=True)

    col_left, col_right = st.columns(2, gap="medium")

    with col_left:
        st.subheader("Avg Rating by Team")
        fig_rating = px.bar(
            team_agg.sort_values("avg_rating", ascending=False),
            x="avg_rating", y="team",
            orientation="h",
            color="avg_rating",
            color_continuous_scale=["#1a3a5c", "#00ff87"],
            labels={"avg_rating": "Avg Rating", "team": "Team"},
        )
        _chart_layout(fig_rating, height=380)
        fig_rating.update_coloraxes(showscale=False)
        st.plotly_chart(fig_rating, use_container_width=True)

    with col_right:
        st.subheader("Squad Size by Team")
        fig_squad = px.bar(
            team_agg.sort_values("players", ascending=False),
            x="players", y="team",
            orientation="h",
            color_discrete_sequence=["#f39c12"],
            labels={"players": "Players", "team": "Team"},
        )
        _chart_layout(fig_squad, height=380)
        st.plotly_chart(fig_squad, use_container_width=True)

# ── Position Analysis page ────────────────────────────────────────────────────

def page_position(df: pd.DataFrame):
    st.title("📐 Position Analysis")
    st.info("ℹ️ All statistics are **synthetic** — generated for demonstration purposes only.", icon=None)

    if _empty_guard(df):
        return

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.subheader("Goals Distribution by Position")
        fig_gbox = px.box(
            df, x="position", y="goals",
            color="position",
            color_discrete_map=POSITION_COLORS,
            labels={"position": "Position", "goals": "Goals"},
            points="outliers",
        )
        _chart_layout(fig_gbox, height=380)
        fig_gbox.update_layout(showlegend=False)
        st.plotly_chart(fig_gbox, use_container_width=True)

    with col2:
        st.subheader("Rating Distribution by Position")
        fig_rbox = px.box(
            df, x="position", y="rating",
            color="position",
            color_discrete_map=POSITION_COLORS,
            labels={"position": "Position", "rating": "Rating"},
            points="outliers",
        )
        _chart_layout(fig_rbox, height=380)
        fig_rbox.update_layout(showlegend=False)
        st.plotly_chart(fig_rbox, use_container_width=True)

    col3, col4 = st.columns(2, gap="medium")

    pos_agg = (
        df.groupby("position", as_index=False)
        .agg(avg_tackles=("tackles", "mean"), avg_pass_accuracy=("pass_accuracy", "mean"))
        .round(2)
    )

    with col3:
        st.subheader("Avg Tackles by Position")
        fig_tackles = px.bar(
            pos_agg.sort_values("avg_tackles", ascending=False),
            x="position", y="avg_tackles",
            color="position",
            color_discrete_map=POSITION_COLORS,
            labels={"position": "Position", "avg_tackles": "Avg Tackles"},
        )
        _chart_layout(fig_tackles, height=360)
        fig_tackles.update_layout(showlegend=False)
        st.plotly_chart(fig_tackles, use_container_width=True)

    with col4:
        st.subheader("Avg Pass Accuracy by Position")
        fig_pacc = px.bar(
            pos_agg.sort_values("avg_pass_accuracy", ascending=False),
            x="position", y="avg_pass_accuracy",
            color="position",
            color_discrete_map=POSITION_COLORS,
            labels={"position": "Position", "avg_pass_accuracy": "Avg Pass Acc (%)"},
        )
        _chart_layout(fig_pacc, height=360)
        fig_pacc.update_layout(showlegend=False)
        st.plotly_chart(fig_pacc, use_container_width=True)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Football Analytics Dashboard",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    full_df = load_data()

    filters = render_sidebar(full_df)
    filtered_df = apply_filters(full_df, filters)

    page = st.sidebar.radio(
        "Navigate",
        ["Overview", "Player Analysis", "Team Analysis", "Position Analysis"],
        index=0,
    )

    if page == "Overview":
        page_overview(filtered_df)
    elif page == "Player Analysis":
        page_player(filtered_df, full_df)
    elif page == "Team Analysis":
        page_team(filtered_df)
    elif page == "Position Analysis":
        page_position(filtered_df)


if __name__ == "__main__":
    main()
