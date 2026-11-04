# 📈 Executive Business Analytics Platform

An enterprise-grade Fullstack Analytics Platform featuring an interactive **Streamlit** data science application, backed by a **Neon PostgreSQL** serverless cloud database, and integrated with **Vercel Serverless Functions** for high-performance edge REST APIs.

---

## 🏗️ Architecture Overview

This project implements a modern dual-tier cloud architecture designed for high availability, zero server maintenance, and multi-platform deployment:

```
                          ┌─────────────────────────────┐
                          │    Neon PostgreSQL (AWS)    │
                          │   (Cloud Serverless DB)     │
                          └──────────────┬──────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 │                                               │
                 ▼                                               ▼
   ┌───────────────────────────┐                   ┌───────────────────────────┐
   │     Vercel Platform       │                   │ Streamlit Community Cloud │
   ├───────────────────────────┤                   ├───────────────────────────┤
   │ • Serverless Python API   │                   │ • Stateful WebSocket App  │
   │   (/api/kpis, /api/data)  │                   │ • Multi-tab Dashboard     │
   │ • Executive Web UI        │                   │ • Seaborn & Plotly Charts │
   │ • Instant Edge Deployment │                   │ • Dynamic Data Filtering  │
   └───────────────────────────┘                   └───────────────────────────┘
```

1. **Vercel Serverless Engine (`/api`, `/public`, `vercel.json`)**:
   - High-throughput, stateless Python serverless functions running on Vercel.
   - Provides RESTful JSON endpoints (`/api/health`, `/api/kpis`, `/api/charts`, `/api/data`).
   - Serves an executive Glassmorphism dashboard frontend (`public/index.html`) rendered at the edge.

2. **Streamlit Analytics Engine (`app.py`, `charts.py`, `utils.py`)**:
   - Long-lived WebSocket architecture for data science exploration.
   - 5 visualization types (Line Chart, Bar Chart, Heatmap, Pie Chart, Histogram) switchable between **Seaborn/Matplotlib** and **Plotly Interactive**.
   - Dynamic sidebar controls for date ranges, multi-category selection, region slicing, and rating ranges.

3. **Neon Serverless PostgreSQL (`db.py`, `seed_db.py`)**:
   - Auto-scaling cloud PostgreSQL database with automated CSV fallback (`business_data.csv`) if the database is temporarily offline or unreachable.

---

## 🚀 How to Deploy on Vercel Serverless

This repository is pre-configured with `vercel.json` and a serverless API handler in `api/index.py`.

### Step 1: Connect Repository to Vercel
1. Log in to [vercel.com](https://vercel.com).
2. Click **"Add New..."** &rarr; **"Project"**.
3. Import your GitHub repository (`interactive-dashboard`).

### Step 2: Configure Environment Variables
In the Vercel project configuration screen, open the **Environment Variables** section and add:
- **Key**: `DATABASE_URL`
- **Value**: `postgresql://neondb_owner:***@ep-spring-waterfall-az6eppdd-pooler.c-3.ap-southeast-1.aws.neon.tech/neondb?sslmode=require`

### Step 3: Deploy
1. Click **"Deploy"**.
2. Vercel automatically detects the Python runtime and builds the serverless endpoints and web portal.
3. Your app is live at `https://<your-project-name>.vercel.app`!

#### Available Vercel Serverless Endpoints:
- `GET /` &mdash; Executive Web Portal
- `GET /api/health` &mdash; Database and service health check
- `GET /api/kpis` &mdash; Filterable KPI summary metrics
- `GET /api/charts` &mdash; Aggregated timeseries and categorical chart data
- `GET /api/data?limit=50&search=keyword` &mdash; Paginated/searched transactions

---

## 📊 How to Deploy Native Streamlit (Streamlit Cloud)

Because Streamlit relies on persistent WebSockets for live slider/rerun interactions, Streamlit Community Cloud is the official, free hosting platform:

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **"New app"**.
3. Select:
   - **Repository**: `malapareddysandhyarani/interactive-dashboard`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Expand **Advanced Settings** &rarr; **Secrets** and paste:
   ```toml
   DATABASE_URL = "postgresql://neondb_owner:***@ep-spring-waterfall-az6eppdd-pooler.c-3.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
   ```
5. Click **"Deploy!"**. Your interactive dashboard will launch within seconds.

---

## 💻 Local Development Setup

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/malapareddysandhyarani/interactive-dashboard.git
cd interactive-dashboard
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Database Credentials
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://neondb_owner:your_password@your-host.aws.neon.tech/neondb?sslmode=require
```

### 3. Initialize & Seed Database
```bash
python seed_db.py
```

### 4. Run Locally
- **Run the Streamlit Dashboard**:
  ```bash
  streamlit run app.py
  ```
- **Test the Serverless API**:
  ```bash
  python -m http.server 8000 --directory public
  ```

---

## 📁 Repository Structure

```text
├── .streamlit/
│   ├── config.toml            # Streamlit theme & server options
│   └── secrets.toml           # Local database credentials (gitignored)
├── api/
│   └── index.py               # Vercel Serverless Python HTTP handler
├── public/
│   └── index.html             # Executive Fullstack Dashboard UI
├── .env                       # Local environment variables (gitignored)
├── .gitignore                 # Protected secret files & cache patterns
├── .python-version            # Pinned Python version (3.11)
├── Procfile                   # Process configuration for PaaS platforms
├── README.md                  # System documentation & deployment guide
├── app.py                     # Streamlit analytics application
├── business_data.csv          # 2,000 transaction dataset (Neon DB seed / fallback)
├── charts.py                  # Seaborn, Matplotlib & Plotly visualizers
├── db.py                      # SQLAlchemy ORM & Neon PostgreSQL connection
├── generate_data.py           # Synthetic dataset generator
├── render.yaml                # Render 1-click cloud blueprint
├── requirements.txt           # Python package dependencies
├── seed_db.py                 # Neon PostgreSQL seeding script
├── utils.py                   # Filtering, KPI metrics & data transformation
└── vercel.json                # Vercel serverless routing & build configuration
```

---

## 🔒 Security & Best Practices
- **Zero Exposed Secrets**: `.env` and `.streamlit/secrets.toml` are strictly ignored by Git. Credentials are injected via platform environment variable managers (Vercel Project Settings & Streamlit Cloud Secrets).
- **Graceful Fallback**: If PostgreSQL connectivity experiences latency or timeout, the system automatically falls back to `business_data.csv` to ensure 100% uptime.

