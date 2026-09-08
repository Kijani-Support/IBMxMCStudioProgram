# Vizier

Vizier is an Ethiopian personal-finance intelligence prototype. It combines monthly budgeting, statement analysis, savings and debt tracking, explainable health scoring, an educational AI coach, and a demo asset portfolio in one black-and-gold NiceGUI interface.

This is not a bank, lender, payment processor, trading platform or regulatory-reporting system. It does not execute transactions or provide personalized buy/sell recommendations.

## Demo capabilities

- Local accounts with salted PBKDF2 password hashes and a five-attempt login throttle
- Multiple financial accounts, monthly history and CSV export
- Category budgets, savings goals, emergency-fund coverage and debt tracking
- Statement CSV import with column detection, validation, categorization and duplicate protection
- Explainable 0–100 financial-health score and deterministic coaching
- Optional IBM watsonx.ai Granite coaching, optional OpenAI fallback and offline operation
- Ethiopian asset reference portfolio with clearly labelled demo values
- Persistent dark mode and supplied Vizier branding

All amounts default to Ethiopian birr (`ETB`). Override `VIZIER_COUNTRY` and `VIZIER_CURRENCY` only when deliberately running another market profile.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Open <http://localhost:8080>. The health endpoint is <http://localhost:8080/health>.

The included `sample-data/ethiopia-statement.csv` contains synthetic demo transactions. No API key is needed for the offline coach.

## IBM watsonx.ai and Granite

Set these values in `.env` or a secret manager:

```dotenv
WATSONX_API_KEY=...
WATSONX_PROJECT_ID=...
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
```

Vizier exchanges the API key for a short-lived IBM Cloud IAM token and calls the watsonx.ai text-generation endpoint. Only the deterministic financial context assembled for the user's question is sent. Raw statement files are not sent. When watsonx.ai fails or is not configured, Vizier tries OpenAI if configured and otherwise uses the offline coach.

## Market data

The Ethiopia profile ships with illustrative asset values because no approved exchange-grade feed is bundled. Set `VIZIER_MARKET_URL` only to a compatible, authorized quote endpoint. The application labels configured feed data separately from demo fallback data and never executes trades.

## Test

```bash
python -m unittest -v
```

## Container

Production mode fails closed when the storage secret is missing or weak:

```bash
docker build -t vizier .
docker run --rm -p 8080:8080 \
  -e VIZIER_STORAGE_SECRET='replace-with-at-least-32-random-characters' \
  -e VIZIER_ENV=production \
  vizier
```

Mount a protected volume and set `VIZIER_DB_PATH` if container data must persist.

## Prototype security boundary

Read `SECURITY.md` before deployment. SQLite, process-local rate limiting and application-managed passwords are adequate for a controlled demo, not a multi-instance financial service. Real deployment requires PostgreSQL migrations, a managed identity provider with MFA, shared rate limiting, encrypted storage, audit logging, backups and operational monitoring.

## Disclaimer

Vizier provides educational estimates. Demo values are not live market prices, and coaching is not financial, investment, legal or tax advice.
