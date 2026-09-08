FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 VIZIER_ENV=production
WORKDIR /app

RUN useradd --create-home --uid 10001 vizier
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=vizier:vizier . .
USER vizier

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=3)"
CMD ["python", "app.py"]
