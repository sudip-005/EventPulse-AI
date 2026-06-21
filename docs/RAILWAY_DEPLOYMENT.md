# EventPulse AI — Railway Deployment

## Readiness summary

- Frontend root: `frontend` (Next.js 14, Node 20, pnpm)
- Backend root: `backend` (FastAPI, Python 3.11, Uvicorn)
- Database: Railway managed PostgreSQL; tables are created idempotently at backend startup
- ML artifacts: `backend/app/ml/models/duration_model.pkl` and `impact_model.pkl`
- API contract: canonical `/api/v1/*`, requested top-level aliases, `/health`, `/docs`
- Database assets: `database/schema.sql`, `migrate.py`, `seed.sql`, and `seed.py`

The feature pipeline performs deterministic encoding and scaling internally, so separate `encoders.pkl` and
`scaler.pkl` artifacts are not required. The loader supports a future `congestion_xgb.pkl` alias and otherwise
loads the trained impact and duration models that this application actually uses.

## Railway service structure

Create one Railway project with three services:

1. `eventpulse-db`: Railway PostgreSQL
2. `eventpulse-api`: GitHub repository, root directory `/backend`
3. `eventpulse-web`: same GitHub repository, root directory `/frontend`

Both application services read their checked-in `railway.json`. The managed PostgreSQL service is provisioned
by Railway; `database/railway.json` records the intended restart policy but is not a replacement for adding the
Railway PostgreSQL service.

## Variables

Backend:

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=<long-random-secret>
ENV=production
MODEL_PATH=app/ml/models
CORS_ORIGINS=https://<frontend-domain>
```

Frontend (set before its first build):

```env
NEXT_PUBLIC_API_URL=https://<backend-domain>/api/v1
```

If the database service is named something other than `Postgres`, change the Railway reference expression to
match its service name. Generate public domains for the frontend and backend before setting URL variables.

## Fast deployment

1. Push this repository, including the two model files, to GitHub.
2. In Railway, create a project from the repository and set the first service root to `/backend`.
3. Add a PostgreSQL database and reference its `DATABASE_URL` from the backend.
4. Add the same repository again as a second service with root `/frontend`.
5. Generate backend and frontend domains, set the variables above, and redeploy both services.
6. Optionally seed demo data from a Railway shell or a local terminal with Railway variables:

```bash
python database/seed.py
```

For a true public one-click button, publish this configured project as a Railway Template once; the template
will preserve the three-service topology and variable references for hackathon judges.

## CLI commands

```bash
railway login
railway init
railway up
railway logs
railway status
```

The Railway dashboard is the shortest path for creating the PostgreSQL service and assigning monorepo root
directories. No Docker, Kubernetes, or external cloud resources are required.

## Checklists

### Pre-deployment

- Commit `backend/app/ml/models/*.pkl`; confirm they are not ignored.
- Confirm backend tests pass and `pnpm build` succeeds.
- Rotate any previously shared database credentials.
- Generate a strong `SECRET_KEY`.
- Ensure the frontend and backend Railway services use `/frontend` and `/backend` roots.

### Deployment

- Add Railway PostgreSQL.
- Configure backend variables and deploy; wait for `/health` to pass.
- Generate the backend domain.
- Configure `NEXT_PUBLIC_API_URL`, deploy the frontend, and generate its domain.
- Set backend `CORS_ORIGINS` to the exact frontend origin and redeploy the backend.
- Optionally run the idempotent seed script.

### Post-deployment

- Check backend `/health`, `/health/deep`, and `/docs`.
- Open every frontend page: `/`, `/dashboard`, `/command-center`, `/forecast`, `/hotspots`, `/simulator`, `/analytics`.
- Create an event, generate a forecast, detect hotspots, run a simulation, and load analytics.
- Review Railway logs for database, model-loading, or CORS errors.

## Smoke tests

```bash
curl -fsS https://<backend-domain>/health
curl -fsS https://<backend-domain>/health/deep
curl -fsS https://<backend-domain>/events
curl -fsS https://<backend-domain>/analytics/overview
curl -fsS https://<backend-domain>/openapi.json > /dev/null
curl -fsS https://<frontend-domain>/ > /dev/null
```

Expected basic health response:

```json
{"status":"healthy"}
```
