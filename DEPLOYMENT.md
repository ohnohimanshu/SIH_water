## Deploying to Railway (Docker)

This app is production-ready for Railway using Docker. It uses:
- Gunicorn WSGI server
- WhiteNoise for static files
- DATABASE_URL from Railway PostgreSQL
- HTTPS security behind Railway proxy

### 1) Prerequisites
- Railway account
- Railway CLI installed (`npm i -g @railway/cli`)
- A PostgreSQL plugin on Railway (or provision one during setup)

### 2) Configure Environment Variables
Required in Railway project settings:
- `SECRET_KEY` (strong random value)
- `DEBUG=false`
- `DATABASE_URL` (from Railway Postgres plugin)
- Optional HTTPS/security:
  - `SECURE_SSL_REDIRECT=true`
  - `SECURE_HSTS_SECONDS=31536000`
  - `CSRF_TRUSTED_ORIGINS` (comma-separated list, e.g., `https://your-app.up.railway.app`)

### 3) Files to Note
- `railway.toml` – defines Docker build and start command
- `Dockerfile` – builds the Django app image
- `health_surveillance/settings.py` – reads `DATABASE_URL`, enables WhiteNoise and security options

### 4) Static Files
Collect static in Docker build or on first run. For Railway builds, you can add this to your Dockerfile after dependencies are installed and before final CMD:

```bash
python manage.py collectstatic --noinput
```

WhiteNoise serves files from `STATIC_ROOT`.

### 5) Deploy Steps
```bash
# Login and initialize
railway login
railway init

# Link to project (if needed)
railway link

# Provision Postgres (if not already)
railway addon create postgresql

# Set env vars (or set from UI)
railway variables set SECRET_KEY=your-secret DEBUG=false SECURE_SSL_REDIRECT=true

# Deploy
railway up
```

### 6) Post-Deploy
Run migrations:
```bash
railway run python manage.py migrate
```

Optional: create superuser
```bash
railway run python manage.py createsuperuser
```

### 7) Verifying
- Open the public URL (e.g., `https://<app>.up.railway.app`)
- Confirm static assets load (DevTools Network panel)
- Confirm admin and API endpoints are reachable
- Check logs:
```bash
railway logs -f
```

### Troubleshooting
- If you see 400 Bad Request, ensure `ALLOWED_HOSTS` includes your Railway domain
- If static files 404, confirm `collectstatic` ran and that `STATIC_ROOT` exists
- If HTTPS redirects loop locally, set `SECURE_SSL_REDIRECT=false` for dev


