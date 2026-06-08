# JOBHUNTER

![jobhunter](/readme_pics/jobhunter.png)

A job scraping pipeline built with Airflow that automatically pulls listings from [cvbankas.lt](cvbankas.lt), cleans the data and stores it in a database. Comes with a Flask web app where you can browse the collected listings, edit your search filters and start or pause the pipeline whenever you want.

## Stack

- **Flask** - web dashboard (port 5001)
- **Airflow** - scraping pipeline scheduler (port 8080)
- **SQLite** - shared database
- **Playwright** - headless browser scraping

## Run with Docker Compose

```bash
docker compose build
docker compose up