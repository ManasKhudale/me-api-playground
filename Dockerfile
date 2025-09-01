# Simple production Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend /app/backend
COPY frontend /app/frontend
ENV PYTHONPATH=/app

# Defaults; can be overridden
ENV ADMIN_USER=admin
ENV ADMIN_PASS=change-me
ENV DATABASE_URL=sqlite:///./meapi.db
ENV RATE_LIMIT_PER_MINUTE=60
ENV ALLOWED_ORIGINS=*

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
