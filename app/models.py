from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Person(db.Model):
    __tablename__ = "people"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return f"<Person {self.email}>"

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f"<Category {self.name}>"

class Expense(db.Model):
    __tablename__ = "expenses"
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey("people.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    note = db.Column(db.String(500), nullable=True)

    person = db.relationship("Person", backref="expenses")
    category = db.relationship("Category", backref="expenses")

    def __repr__(self):
        return f"<Expense {self.amount} {self.category_id}>"

class Budget(db.Model):
    __tablename__ = "budgets"
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    alert_when_remaining_pct = db.Column(db.Float, nullable=True)

    category = db.relationship("Category", backref="budgets")

    __table_args__ = (
        db.UniqueConstraint('category_id', 'year', 'month', name='uc_category_year_month'),
    )

    def __repr__(self):
        return f"<Budget {self.category.name} {self.year}-{self.month}: {self.amount}>"

class SharedExpense(db.Model):
    __tablename__ = "shared_expenses"
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey("expenses.id"), nullable=False)
    shared_with_person_id = db.Column(db.Integer, db.ForeignKey("people.id"), nullable=False)
    share_amount = db.Column(db.Float, nullable=False)

    expense = db.relationship("Expense", backref="shared_parts")
    shared_with = db.relationship("Person", backref="shared_entries")
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class Expense(Base):
__tablename__ = "expenses"
id = Column(Integer, primary_key=True, index=True)
amount = Column(Float, nullable=False)
category = Column(String, nullable=False, index=True)
note = Column(String, nullable=True)
created_at = Column(DateTime(timezone=True), server_default=func.now())
user = Column(String, default="default_user")
share_id = Column(String, nullable=True, index=True) # grouping id for shared expenses


class Budget(Base):
__tablename__ = "budgets"
id = Column(Integer, primary_key=True, index=True)
category = Column(String, nullable=False, index=True)
year = Column(Integer, nullable=False)
month = Column(Integer, nullable=False)
amount = Column(Float, nullable=False)
user = Column(String, default="default_user")
alert_threshold = Column(Float, nullable=True) # optional override per-budget
