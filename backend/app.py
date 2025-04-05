from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from nba_api.stats.endpoints import leaguedashteamstats
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import time
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

east_teams = {"BOS", "MIL", "PHI", "NYK", "MIA", "ATL", "CHI", "TOR", "IND", "CLE", "WAS", "CHA", "DET", "ORL", "BKN"}
def get_conference(team): return "East" if team in east_teams else "West"

def load_kaggle_data():
    df = pd.read_csv("data/PlayerStats.csv")
    df = df[(df["GP"] > 0) & (df["MIN"] > 0)]
    df = df[df["TEAM_ABBREVIATION"] != "TOT"]
    return df

def fetch_current_season_team_stats(season: str):
    time.sleep(1)
    try:
        df = leaguedashteamstats.LeagueDashTeamStats(
            season=season,
            season_type_all_star="Regular Season",
            per_mode_detailed="Totals"
        ).get_data_frames()[0]
        df = df[['TEAM_ABBREVIATION', 'PTS', 'AST', 'REB', 'FG_PCT', 'FT_PCT']]
        df = df[df["TEAM_ABBREVIATION"] != "TOT"]
        df["Conference"] = df["TEAM_ABBREVIATION"].apply(get_conference)
        return df
    except:
        return None

def load_team_data(season: str, df_hist: pd.DataFrame):
    file = f"data/PlayerStats_{season.replace('-', '_')}.csv"
    if os.path.exists(file):
        df = pd.read_csv(file)
    else:
        df = df_hist[df_hist["SEASON_ID"] == season]
    if df.empty: return None
    df = df[df["TEAM_ABBREVIATION"] != "TOT"]
    df = df.groupby("TEAM_ABBREVIATION").agg({
        "PTS": "sum", "AST": "sum", "REB": "sum",
        "FG_PCT": "mean", "FT_PCT": "mean"
    }).reset_index()
    df["Conference"] = df["TEAM_ABBREVIATION"].apply(get_conference)
    return df

@app.get("/predict")
def predict_top_teams(season: str = Query(...)):
    try: start_year = int(season.split("-")[0])
    except: return {"error": "Invalid season format"}

    train_years = [f"{y}-{str(y+1)[2:]}" for y in range(start_year - 7, start_year)]
    df_hist = load_kaggle_data()
    df_train = df_hist[df_hist["SEASON_ID"].isin(train_years)]
    if df_train.empty: return {"error": "No training data found"}

    team_df = df_train.groupby(["TEAM_ABBREVIATION", "SEASON_ID"]).agg({
        "PTS": "sum", "AST": "sum", "REB": "sum", "FG_PCT": "mean", "FT_PCT": "mean"
    }).reset_index()
    team_df["Conference"] = team_df["TEAM_ABBREVIATION"].apply(get_conference)
    team_df["Success"] = 0

    for season_key, group in team_df.groupby("SEASON_ID"):
        for conf in ["East", "West"]:
            top_10 = group[group["Conference"] == conf].sort_values("PTS", ascending=False).head(10).index
            team_df.loc[top_10, "Success"] = 1

    X_train = team_df[["PTS", "AST", "REB", "FG_PCT", "FT_PCT"]]
    y_train = team_df["Success"]
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    df_pred = load_team_data(season, df_hist)
    if df_pred is None: return {"error": "No prediction data available"}

    X_pred = df_pred[["PTS", "AST", "REB", "FG_PCT", "FT_PCT"]]
    df_pred["Playoff_Prob"] = model.predict_proba(X_pred)[:, 1]

    result = {"season": season, "East": [], "West": []}
    for conf in ["East", "West"]:
        top10 = df_pred[df_pred["Conference"] == conf].sort_values("Playoff_Prob", ascending=False).head(10)
        result[conf] = [
            {"team": row.TEAM_ABBREVIATION, "confidence": round(row.Playoff_Prob * 100, 2)}
            for row in top10.itertuples()
        ]
    return result

@app.get("/breakouts")
def get_breakout_players(season: str = Query(...)):
    df_hist = load_kaggle_data()
    path = f"data/PlayerStats_{season.replace('-', '_')}.csv"
    df = pd.read_csv(path) if os.path.exists(path) else df_hist[df_hist["SEASON_ID"] == season]
    if df.empty: return {"error": f"No player data for {season}"}

    players = df[df["PLAYER_AGE"] <= 26].copy()
    players = players[players["TEAM_ABBREVIATION"] != "TOT"]
    players["Score"] = (
        0.5 * players["PTS"] + 0.2 * players["REB"] + 0.2 * players["AST"] + 0.1 * players["STL"]
    )
    players["Conference"] = players["TEAM_ABBREVIATION"].apply(get_conference)

    result = {"season": season, "East": [], "West": []}
    for conf in ["East", "West"]:
        top5 = players[players["Conference"] == conf].sort_values("Score", ascending=False).head(5)
        result[conf] = [
            {
                "name": row.Name,
                "team": row.TEAM_ABBREVIATION,
                "score": round(row.Score, 2),
                "playerId": row.PLAYER_ID  # ✅ This makes player images work!
            }
            for row in top5.itertuples()
        ]
    return result

@app.get("/improvers")
def get_stat_improvers(season: str = Query(...)):
    df_hist = load_kaggle_data()
    path = f"data/PlayerStats_{season.replace('-', '_')}.csv"
    df = pd.read_csv(path) if os.path.exists(path) else df_hist[df_hist["SEASON_ID"] == season]
    if df.empty: return {"error": f"No player data for {season}"}

    players = df[df["PLAYER_AGE"] <= 25].copy()
    players = players[players["TEAM_ABBREVIATION"] != "TOT"]
    players["Conference"] = players["TEAM_ABBREVIATION"].apply(get_conference)

    result = {"season": season, "PTS": {}, "REB": {}, "AST": {}}
    for stat in ["PTS", "REB", "AST"]:
        players[f"{stat}_proj"] = players[stat] * 1.2
        for conf in ["East", "West"]:
            top5 = players[players["Conference"] == conf].sort_values(f"{stat}_proj", ascending=False).head(5)
            result[stat][conf] = [
                {
                    "name": row.Name,
                    "team": row.TEAM_ABBREVIATION,
                    "current": round(getattr(row, stat), 1),
                    "projected": round(getattr(row, f"{stat}_proj"), 1),
                    "playerId": row.PLAYER_ID  # ✅ For player headshots
                }
                for row in top5.itertuples()
            ]
    return result

