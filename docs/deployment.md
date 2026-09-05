# Mule Matrix Deployment Guide

This repository has been optimized and prepared for a decoupled cloud deployment:
- **Frontend**: Vercel
- **Backend**: Render (or any Docker/Uvicorn compatible PaaS)
- **Database**: Neo4j AuraDB

## Environment Variables

### Backend (Render)
Ensure the following environment variables are set in your Render Web Service dashboard:
- `NEO4J_URI`: Your Neo4j AuraDB connection string (e.g., `neo4j+s://<instance>.databases.neo4j.io`)
- `NEO4J_USER`: Your AuraDB username (typically `neo4j`)
- `NEO4J_PASSWORD`: Your AuraDB password
- `FRONTEND_URL`: The production URL of your Vercel deployment (e.g., `https://mule-matrix.vercel.app`). This is required for CORS to allow the frontend to communicate with the backend.
- `PORT`: (Optional) Render will automatically assign a `PORT` environment variable which the `main.py` entrypoint listens to dynamically.

### Frontend (Vercel)
Ensure the following environment variable is set in your Vercel project settings:
- `VITE_API_URL`: The production URL of your Render backend API (e.g., `https://mule-matrix-api.onrender.com/api`)

## Deployment Process

### 1. Database (Neo4j AuraDB)
1. Provision a free or paid instance on Neo4j Aura.
2. Obtain the connection URI, username, and password.
3. If necessary, populate the AuraDB instance with initial graph data using the local data generator scripts or by running Cypher commands from your local `graph/schema` directory against the cloud instance.

### 2. Backend (Render)
1. Connect your GitHub repository to Render and create a new **Web Service**.
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Add the backend environment variables listed above.
5. The ML models (in `ml/models/*.joblib`) are tracked in the repository and will be loaded dynamically by `predict.py` without retraining.
6. Deploy the backend.

### 3. Frontend (Vercel)
1. Connect your GitHub repository to Vercel and create a new Project.
2. Ensure the Framework Preset is set to **Vite**.
3. **Root Directory**: `frontend`
4. Add the frontend environment variables listed above.
5. Deploy the frontend.

## Local Development Compatibility
The platform is still fully compatible with local execution.
- If `FRONTEND_URL` is omitted, the backend will default to allowing CORS for `http://localhost:5173`.
- If `VITE_API_URL` is omitted, the frontend will default to requesting `http://127.0.0.1:8000/api`.
- Local Docker Neo4j continues to work by defaulting to `bolt://localhost:7687` and `password` if `.env` variables are missing.
