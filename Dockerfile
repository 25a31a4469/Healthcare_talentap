FROM python:3.12-slim

WORKDIR /app

# Install system dependencies if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and database
COPY backend backend
COPY data data
COPY healthcare.db .

ENV PORT=8000
ENV ENVIRONMENT=production
ENV DATABASE_URL=sqlite:///./healthcare.db

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
