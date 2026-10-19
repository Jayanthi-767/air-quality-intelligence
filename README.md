# 🌍 Air Quality Intelligence

A Python-based data analytics project that collects air-quality readings from the World Air Quality Index (WAQI) API, stores them in SQLite, analyzes pollutant measurements, and displays results through an interactive dashboard.

## ✨ Features

- Fetch air-quality data from the WAQI API
- Store observations in a local SQLite database
- Build a FastAPI backend for accessing saved measurements
- Analyze readings using pandas
- Visualize PM2.5 trends and pollutant measurements
- Export observations to CSV
- Display saved readings in a Streamlit dashboard
- Check dataset quality before analysis

## 🛠️ Tech Stack

- Python
- FastAPI
- SQLite
- SQLAlchemy
- pandas
- Matplotlib
- Streamlit
- Requests
- python-dotenv

## 📁 Project Structure

```text
air-quality-intelligence/
├── backend/
│   └── app/
│       ├── database.py
│       ├── models.py
│       ├── schemas.py
│       └── main.py
├── .env
├── .gitignore
├── create_tables.py
├── fetch_waqi.py
├── test_waqi.py
├── plot_trends.py
├── plot_pollutants.py
├── analyze_air_quality.py
├── check_data_quality.py
├── dashboard.py
├── air_quality.db
└── README.md
```

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd air-quality-intelligence
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install fastapi uvicorn sqlalchemy requests python-dotenv pandas matplotlib streamlit
```

### 4. Configure the API token

Create a `.env` file in the project root:

```text
WAQI_API_TOKEN=your_token_here
```

Replace the placeholder with your own WAQI token. Never commit your real token to GitHub.

### 5. Collect real readings

```bash
python fetch_waqi.py
```

### 6. Start the dashboard

```bash
python -m streamlit run dashboard.py
```

### 7. Start the API

In a separate terminal:

```bash
python -m uvicorn backend.app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to explore the API.

## 📊 Analysis

The project provides:

- Latest saved air-quality readings
- PM2.5 trend visualization
- Pollutant comparisons
- Summary statistics
- CSV export
- Data-quality checks

## 🔐 Data and Privacy

API credentials are stored locally in `.env`. The local SQLite database and generated datasets may contain collected observations and should be reviewed before sharing.

## 📌 Future Improvements

- Collect observations on a scheduled basis
- Compare multiple monitoring stations
- Add more historical data visualizations
- Build a predictive model after collecting sufficient quality data
- Deploy the dashboard and API

## ⚠️ Disclaimer

This is an educational analytics project. Readings depend on the source station and its update frequency. The project does not provide medical advice or guarantee current local air conditions.

## 👤 Author

Add your name and portfolio links here.
