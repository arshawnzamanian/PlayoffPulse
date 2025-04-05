# 🏀 NBA Prediction Center

A full-stack web app that uses machine learning to:

- 🔮 Predict the top 10 NBA teams per conference for any season
- 🚀 Highlight breakout players (age ≤ 26)
- 📈 Show projected stat improvers (PTS, AST, REB for age ≤ 25)

Built with:
- ⚛️ React + Next.js frontend
- 🐍 FastAPI backend
- 🧠 Scikit-learn ML
- 🐳 Docker and/or simple `launch.sh` script

---

## 🚀 Features

| Feature       | Description                                             |
|---------------|---------------------------------------------------------|
| ✅ Predictions | Top 10 teams (East & West) with playoff confidence     |
| ✅ Breakouts   | Ranks breakout players based on scoring potential      |
| ✅ Improvers   | Projects stat growth for promising young players       |
| 🖼 Logos       | Team logos + player headshots dynamically rendered     |
| 🌐 API         | `/predict`, `/breakouts`, `/improvers`                |

---

## 📁 Project Structure

```
nba-predictor/
├── backend/             # FastAPI backend (app.py)
│   ├── app.py
│   ├── requirements.txt
│   └── data/            # PlayerStats.csv + PlayerStats_YYYY_YY.csv
├── frontend/            # Next.js frontend
│   ├── src/app/page.tsx
│   └── public/          # Backgrounds, logos, default-player.png
├── docker-compose.yml
├── launch.sh            # Launch script for local dev
└── README.md
```

---

## 🧪 Local Dev Setup (No Docker)

### 1. Create Python venv and install backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Install frontend dependencies

```bash
cd ../frontend
npm install
```

### 3. Run both with one command

```bash
./launch.sh
```

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend: [http://localhost:9000](http://localhost:9000)

---

## 🐳 Docker (Optional)

```bash
docker-compose up --build
```

---

## 🔌 API Endpoints

| Endpoint                         | Description                                 |
|----------------------------------|---------------------------------------------|
| `/predict?season=2024-25`        | Returns top 10 teams by conference          |
| `/breakouts?season=2024-25`      | Breakout players with headshots             |
| `/improvers?season=2024-25`      | Stat improvers with projections             |

---

## 🧠 How It Works

1. Model trains on the 7 seasons **before** selected season
2. Labels top 10 teams per conference as “success”
3. Makes predictions based on team stats using RandomForestClassifier

---

## 🖼 Image Sources

- ✅ Team logos: `https://cdn.nba.com/logos/...`
- ✅ Player photos: `https://ak-static.cms.nba.com/...`
- ✅ Fallback image: `public/default-player.png`

---

## 🙌 Credits

- `nba_api` for live data
- [shadcn/ui](https://ui.shadcn.dev) for UI components
- Tailwind CSS
- You — for making this awesome

---

## 📄 License

MIT — free to use, build on, and deploy 🏀
---
Built for fun using chatGPT, Kaggle, NBA, and ESPN. ❤️
