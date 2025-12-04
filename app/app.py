import os
from datetime import datetime, date
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from models import db, Person, Category, Expense, Budget, SharedExpense

load_dotenv()

def create_app():
    app = Flask(__name__)
    database_url = os.getenv("DATABASE_URL", "sqlite:///expenses.db")
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    def parse_date(dstr):
        if not dstr:
            return date.today()
        try:
            return datetime.strptime(dstr, "%Y-%m-%d").date()
        except Exception:
            return date.today()

    @app.route("/api/expense", methods=["POST"])
    def add_expense():
        """
        Expected JSON:
        {
          "user_email": "me@example.com",
          "category": "Food",
          "amount": 120.5,
          "date": "2025-12-01",    # optional, default today
          "note": "lunch",
          "shared_with": [{"email":"a@b.c","share":40.17}, ...]  # optional
        }
        """
        data = request.get_json() or {}
        email = data.get("user_email")
        if not email:
            return jsonify({"error":"user_email required"}), 400

        person = Person.query.filter_by(email=email).first()
        if not person:
            person = Person(email=email, name=None)
            db.session.add(person)
            db.session.commit()

        cat_name = data.get("category", "Uncategorized")
        category = Category.query.filter_by(name=cat_name).first()
        if not category:
            category = Category(name=cat_name)
            db.session.add(category)
            db.session.commit()

        try:
            amount = float(data.get("amount", 0))
        except Exception:
            return jsonify({"error":"invalid amount"}), 400
        if amount <= 0:
            return jsonify({"error":"amount must be > 0"}), 400

        d = parse_date(data.get("date"))
        note = data.get("note", "")

        expense = Expense(person_id=person.id, category_id=category.id, amount=amount, date=d, note=note)
        db.session.add(expense)
        db.session.commit()

        # handle shared splits
        shared = data.get("shared_with")
        if shared and isinstance(shared, list):
            for s in shared:
                se_email = s.get("email")
                share_amt = float(s.get("share", 0))
                shared_person = Person.query.filter_by(email=se_email).first()
                if not shared_person:
                    shared_person = Person(email=se_email)
                    db.session.add(shared_person)
                    db.session.commit()
                se = SharedExpense(expense_id=expense.id, shared_with_person_id=shared_person.id, share_amount=share_amt)
                db.session.add(se)
            db.session.commit()

        # compute monthly total for this category
        total_spent = db.session.query(db.func.sum(Expense.amount)).filter(
            db.extract('year', Expense.date) == d.year,
            db.extract('month', Expense.date) == d.month,
            Expense.category_id == category.id
        ).scalar() or 0.0

        # find budget for this category+month
        budget = Budget.query.filter_by(category_id=category.id, year=d.year, month=d.month).first()

        alert = None
        if budget:
            if total_spent > budget.amount:
                alert = {
                    "type":"OVER_BUDGET",
                    "category": category.name,
                    "month": f"{budget.year}-{budget.month}",
                    "spent": total_spent,
                    "budget": budget.amount
                }
            elif budget.alert_when_remaining_pct is not None:
                remaining_pct = max(0.0, (1 - total_spent / budget.amount) * 100)
                if remaining_pct <= float(budget.alert_when_remaining_pct):
                    alert = {
                        "type":"LOW_REMAINING",
                        "remaining_pct": remaining_pct,
                        "threshold": budget.alert_when_remaining_pct,
                        "spent": total_spent,
                        "budget": budget.amount
                    }

        return jsonify({"expense_id": expense.id, "alert": alert}), 201

    @app.route("/api/budget", methods=["POST"])
    def set_budget():
        """
        Payload:
        {
          "category":"Food",
          "year":2025,
          "month":12,
          "amount":5000,
          "alert_when_remaining_pct": 10
        }
        """
        data = request.get_json() or {}
        category_name = data.get("category", "Uncategorized")
        year = int(data.get("year", datetime.today().year))
        month = int(data.get("month", datetime.today().month))
        try:
            amount = float(data.get("amount", 0))
        except Exception:
            return jsonify({"error":"invalid amount"}), 400
        if amount < 0:
            return jsonify({"error":"amount must be >= 0"}), 400

        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.commit()

        bud = Budget.query.filter_by(category_id=category.id, year=year, month=month).first()
        if not bud:
            bud = Budget(category_id=category.id, year=year, month=month, amount=amount,
                         alert_when_remaining_pct=data.get("alert_when_remaining_pct"))
            db.session.add(bud)
        else:
            bud.amount = amount
            bud.alert_when_remaining_pct = data.get("alert_when_remaining_pct")
        db.session.commit()
        return jsonify({"budget_id": bud.id}), 201

    @app.route("/api/reports/monthly_total", methods=["GET"])
    def monthly_total():
        year = int(request.args.get("year", datetime.today().year))
        month = int(request.args.get("month", datetime.today().month))
        user_email = request.args.get("user_email")

        q = db.session.query(db.func.sum(Expense.amount).label("total")).filter(
            db.extract('year', Expense.date) == year,
            db.extract('month', Expense.date) == month
        )
        if user_email:
            p = Person.query.filter_by(email=user_email).first()
            if not p:
                return jsonify({"year":year,"month":month,"total":0.0})
            q = q.filter(Expense.person_id == p.id)
        total = q.scalar() or 0.0
        return jsonify({"year": year, "month": month, "total": total})

    @app.route("/api/reports/spend_vs_budget", methods=["GET"])
    def spend_vs_budget():
        year = int(request.args.get("year", datetime.today().year))
        month = int(request.args.get("month", datetime.today().month))
        cats = Category.query.order_by(Category.name).all()
        result = []
        for c in cats:
            spent = db.session.query(db.func.sum(Expense.amount)).filter(
                Expense.category_id == c.id,
                db.extract('year', Expense.date) == year,
                db.extract('month', Expense.date) == month
            ).scalar() or 0.0
            b = Budget.query.filter_by(category_id=c.id, year=year, month=month).first()
            result.append({
                "category": c.name,
                "spent": spent,
                "budget": b.amount if b else None
            })
        return jsonify({"year": year, "month": month, "data": result})

    @app.route("/api/budget", methods=["GET"])
    def get_budget():
        category_name = request.args.get("category")
        year = int(request.args.get("year", datetime.today().year))
        month = int(request.args.get("month", datetime.today().month))
        if not category_name:
            return jsonify({"error":"category param required"}), 400
        c = Category.query.filter_by(name=category_name).first()
        if not c:
            return jsonify({"budget": None})
        b = Budget.query.filter_by(category_id=c.id, year=year, month=month).first()
        if not b:
            return jsonify({"budget": None})
        return jsonify({"year": b.year, "month": b.month, "amount": b.amount, "alert_when_remaining_pct": b.alert_when_remaining_pct})

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
