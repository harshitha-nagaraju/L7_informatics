# Expense Tracker (Python) — Placement Submission

Score target: complete functionality + extras (monthly budgets, custom alerts, optional email alerts, shared expenses).

## Overview
A small Flask API + SQLite backend to:
- Log daily expenses
- Categorize expenses (`Food`, `Transport`, etc.)
- Set monthly budgets per category (with per-month override)
- Alerts when budget exceeded (and configurable %-left alerts)
- Basic reports:
  - Total spending per month
  - Spending vs budget per category

Extras implemented:
- Different budgets per month
- Custom alerts (e.g., when only 10% budget left)
- Email notification hooks (using SMTP; requires SMTP config)
- Shared expenses skeleton (split amounts among users)

## Files
- `app.py` — Flask REST API + main app
- `models.py` — SQLAlchemy models (User, Category, Expense, Budget, SharedExpense)
- `db_init.py` — script to create DB & seed categories
- `requirements.txt` — Python deps
- `Dockerfile`, `docker-compose.yml` — for containerized run
- `tests/test_api.py` — pytest tests (basic)

## Quick start (local)
1. Clone the repo
2. Create virtual env and install:
   ```bash
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
