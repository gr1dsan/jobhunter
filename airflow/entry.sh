#!/bin/bash
set -e

echo "Running Airflow migrations..."
airflow db migrate

echo "Creating admin user..."

airflow users create \
  --username "$AIRFLOW_USER" \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email "$AIRFLOW_EMAIL" \
  --password "$AIRFLOW_PASSWORD" || true

echo "Starting Airflow..."
exec airflow standalone