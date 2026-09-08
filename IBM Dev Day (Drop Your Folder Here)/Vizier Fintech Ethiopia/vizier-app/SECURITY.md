# Security policy

Vizier is an educational prototype. Do not load real customer records, banking credentials, national IDs, PINs or OTPs into it.

## Reporting

Report suspected vulnerabilities privately to the project team. Do not include personal financial data or active credentials in a report.

## Deployment baseline

- Run behind TLS and a trusted reverse proxy.
- Set `VIZIER_ENV=production` and a unique `VIZIER_STORAGE_SECRET` of at least 32 characters.
- Store IBM and OpenAI credentials in the hosting platform's secret manager.
- Restrict access to the SQLite database and back it up. PostgreSQL remains the appropriate next step for multiple production instances.
- Keep dependency scanning and the test workflow enabled.
- Treat the process-local login throttle as demo protection. Production requires a shared rate limiter or managed identity provider.
