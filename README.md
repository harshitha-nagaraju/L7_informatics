# Expense Tracker Application

A Python + Flask + SQLAlchemy based Expense Tracker that allows users to log expenses, set category-wise budgets, receive alerts, view monthly reports, and handle shared group expenses.  
Designed according to the assignment specification with clean backend architecture, ORM usage, testing, and Docker support.

---

# 1. Features

## Core Features
- Log daily expenses
- Category-wise expenses (Food, Transport, Entertainment, etc.)
- Monthly budgets per category
- Automatic alerts when:
  - Budget exceeded
  - Only 10% budget remains (configurable via `.env`)
- Monthly spending summary
- Spending vs Budget comparison for each category

## Extra Credit Features Implemented
- Different budgets for different months
- Custom threshold-based alerts
- Email notifications (configurable)
- Shared group expenses (Splitwise-style)
- CLI commands to add expenses and set budgets

---

# 2. Tech Stack

- **Python 3.11**
- **Flask 2.3**
- **SQLAlchemy ORM**
- **SQLite Database**
- **pytest** for testing
- **Docker** for containerized deployment
- **dotenv** for environment management

---

# 3. Dependencies

All dependencies are listed in `requirements.txt`.

