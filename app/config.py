class Config:
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///data/expenses.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
FROM_EMAIL = os.getenv('FROM_EMAIL')
LOW_BUDGET_THRESHOLD = float(os.getenv('LOW_BUDGET_THRESHOLD', 0.1))
