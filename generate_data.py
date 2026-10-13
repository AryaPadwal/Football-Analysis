"""
generate_data.py — Run once to produce football_players.csv.
Delete this script after the CSV is generated.
All data is SYNTHETIC and does not represent real players or clubs.
"""

import numpy as np
import pandas as pd

np.random.seed(42)

# ── Reference data ────────────────────────────────────────────────────────────

TEAMS = [
    "FC Northgate",
    "Riverside United",
    "Capital City FC",
    "Eastern Athletic",
    "Westbrook City",
    "Port Vale Rangers",
    "Hillside Rovers",
    "Lakeside FC",
    "Northern Star",
    "Sundown Athletic",
]

POSITIONS = ["Goalkeeper", "Defender", "Midfielder", "Forward"]
# rough squad distribution per team (GK=2, DEF=4, MID=4, FWD=3 → 13 per team × 10 = 130 players, pick 100)
POS_WEIGHTS = [0.10, 0.30, 0.35, 0.25]

SEASONS = ["2021-22", "2022-23", "2023-24"]

NATIONALITIES = [
    "England", "Spain", "France", "Germany", "Brazil", "Argentina",
    "Portugal", "Italy", "Netherlands", "Belgium", "Uruguay", "Croatia",
    "Senegal", "Nigeria", "Morocco", "Japan", "South Korea", "Colombia",
    "Mexico", "United States",
]

FIRST_NAMES = [
    "Liam", "Noah", "Oliver", "James", "Elijah", "Lucas", "Mason", "Ethan",
    "Aiden", "Logan", "Carlos", "Mateo", "Diego", "Rafael", "Gabriel",
    "Marco", "Luca", "Enzo", "Kai", "Finn", "Hugo", "Felix", "Leon",
    "Oscar", "Emil", "Axel", "Victor", "Simon", "Max", "Tom",
    "Ryo", "Seo", "Yuki", "Hiroshi", "Kwame", "Kofi", "Emeka",
    "Tariq", "Zaid", "Iker",
]

LAST_NAMES = [
    "Silva", "Müller", "Dupont", "García", "Rossi", "Santos", "Kowalski",
    "Ahmed", "Okafor", "Nakamura", "Park", "Chen", "Williams", "Brown",
    "Jones", "Smith", "Taylor", "Davies", "Evans", "Wilson", "Thompson",
    "Martin", "Bernard", "Leroy", "Diallo", "Traoré", "Mbeki", "Osei",
    "Fernández", "Herrera",
]

# ── Position-specific stat multipliers ───────────────────────────────────────

POS_PARAMS = {
    #             goals  assists shots  tackles  passes_per_game
    "Goalkeeper": (0.5,   0.5,   1.0,   1.0,     35),
    "Defender":   (2.0,   3.0,   4.0,   6.0,     55),
    "Midfielder": (5.0,   7.0,   8.0,   5.0,     70),
    "Forward":    (12.0,  6.0,  20.0,   2.0,     50),
}

# ── Build player roster (fixed attributes) ───────────────────────────────────

N_PLAYERS = 100

names_pool = [
    f"{np.random.choice(FIRST_NAMES)} {np.random.choice(LAST_NAMES)}"
    for _ in range(N_PLAYERS)
]

positions = np.random.choice(POSITIONS, size=N_PLAYERS, p=POS_WEIGHTS)
teams = np.random.choice(TEAMS, size=N_PLAYERS)
ages_base = np.random.randint(18, 33, size=N_PLAYERS)
nationalities = np.random.choice(NATIONALITIES, size=N_PLAYERS)

# ── Generate per-season rows ──────────────────────────────────────────────────

rows = []
for pid in range(N_PLAYERS):
    name = names_pool[pid]
    pos = positions[pid]
    team = teams[pid]
    nat = nationalities[pid]
    g_mu, a_mu, sh_mu, tk_mu, ppg = POS_PARAMS[pos]

    for s_idx, season in enumerate(SEASONS):
        age = int(ages_base[pid]) + s_idx

        appearances = int(np.random.randint(8, 38))
        minutes_played = int(appearances * np.random.randint(70, 95))

        goals = max(0, int(np.random.poisson(g_mu * appearances / 38)))
        assists = max(0, int(np.random.poisson(a_mu * appearances / 38)))
        shots = max(goals, int(np.random.poisson(sh_mu * appearances / 38)))
        tackles = max(0, int(np.random.poisson(tk_mu * appearances / 38)))
        passes = int(appearances * ppg + np.random.randint(-10, 10))
        pass_accuracy = round(float(np.clip(np.random.normal(75, 8), 55, 95)), 1)
        yellow_cards = int(np.random.randint(0, 8))
        red_cards = int(np.random.randint(0, 3))
        rating = round(float(np.clip(np.random.normal(6.8, 0.8), 5.0, 9.5)), 1)

        rows.append({
            "player_id": pid + 1,
            "name": name,
            "team": team,
            "position": pos,
            "season": season,
            "age": age,
            "nationality": nat,
            "appearances": appearances,
            "minutes_played": minutes_played,
            "goals": goals,
            "assists": assists,
            "shots": shots,
            "passes": passes,
            "pass_accuracy": pass_accuracy,
            "tackles": tackles,
            "yellow_cards": yellow_cards,
            "red_cards": red_cards,
            "rating": rating,
        })

df = pd.DataFrame(rows)
df.to_csv("football_players.csv", index=False)
print(f"Generated {len(df)} rows -> football_players.csv")
