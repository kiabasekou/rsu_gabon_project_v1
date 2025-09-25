# 🇬🇦 RSU Gabon - Docker Image Production
FROM python:3.11-slim

WORKDIR /app

# Dependencies système
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create logs directory
RUN mkdir -p /var/log/rsu

# Non-root user for security
RUN useradd --create-home --shell /bin/bash rsu
RUN chown -R rsu:rsu /app /var/log/rsu
USER rsu

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "rsu_identity.wsgi:application"]
