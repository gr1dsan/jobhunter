# JOBHUNTER

![JobHunter](redme_pics/jobhunter.png)

Automated job scraping pipeline with a Flask dashboard to manage search filters, view results, and control the scraper.

## Stack

- **Flask** — web dashboard (port 5001)
- **Airflow** — scraping pipeline scheduler (port 8080)
- **SQLite** — shared database
- **Playwright** — headless browser scraping

## Instructions

### 1. Run with Docker Compose

```bash
docker compose build
docker compose up