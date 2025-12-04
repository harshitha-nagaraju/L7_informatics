from flask import Blueprint, jsonify, request, abort
from .models import Expense, Budget, User, Category, ShareGroup, ShareMember, SharedExpense
from . import db
from sqlalchemy import func, and_
from datetime import datetime, date
from .alerts import check_and_alert

bp = Blueprint('api', __name__)

def get_user_by_email_or_404(email):
    u = User.query.filter_by(email=email).first()
    if not u:
        abort(404, description=f'User not found: {email}')
    return u

def get_category_by_name_or_404(name):
    c = Category.query.filter_by(name=name).first()
    if not c:
        abort(404, description=f'Category not found: {name}')
    return c

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    name = data.get('name')
    email = data.get('email')
    if not email:
        abort(400, 'email is required')
    if User.query.filter_by(email=email).first():
        abort(400, 'user already exists')
    user = User(name=name, email=email)
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email}), 201

@bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    u = User.query.get_or_404(user_id)
    return jsonify({'id': u.id, 'name': u.name, 'email': u.email})

@bp.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'GET':
        cats = Category.query.order_by(Category.name).all()
        return jsonify([{'id': c.id, 'name': c.name} for c in cats])
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        abort(400, 'name required')
    if Category.query.filter_by(name=name).first():
        abort(400, 'category exists')
    c = Category(name=name)
    db.session.add(c)
    db.session.commit()
    return jsonify({'id': c.id, 'name': c.name}), 201

@bp.route('/expenses', methods=['POST'])
def add_expense():
    data = request.get_json() or {}
    user = get_user_by_email_or_404(data.get('user_email'))
    category = get_category_by_name_or_404(data.get('category'))
    amount = data.get('amount')
    if amount is None:
        abort(400, 'amount required')
    date_str = data.get('date')
    d = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
    exp = Expense(user_id=user.id, category_id=category.id, amount=float(amount), description=data.get('description'), date=d)
    db.session.add(exp)
    db.session.commit()
    year, month = d.year, d.month
    spent = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.user_id == user.id,
        Expense.category_id == category.id,
        func.strftime('%Y', Expense.date) == str(year),
        func.strftime('%m', Expense.date) == f"{month:02d}"
    ).scalar()
    budget = Budget.query.filter_by(user_id=user.id, category_id=category.id, year=year, month=month).first()
    if budget:
        check_and_alert(user, category, spent, budget.amount)
    return jsonify({'id': exp.id, 'user_id': user.id, 'category': category.name, 'amount': exp.amount, 'description': exp.description, 'date': exp.date.isoformat()}), 201

@bp.route('/budgets', methods=['POST'])
def set_budget():
    data = request.get_json() or {}
    user = get_user_by_email_or_404(data.get('user_email'))
    category = get_category_by_name_or_404(data.get('category'))
    year = int(data.get('year'))
    month = int(data.get('month'))
    amount = float(data.get('amount'))
    b = Budget.query.filter_by(user_id=user.id, category_id=category.id, year=year, month=month).first()
    if not b:
        b = Budget(user_id=user.id, category_id=category.id, year=year, month=month, amount=amount)
        db.session.add(b)
    else:
        b.amount = amount
    db.session.commit()
    return jsonify({'id': b.id, 'user_id': user.id, 'category': category.name, 'year': year, 'month': month, 'amount': b.amount}), 201

@bp.route('/budgets/<string:user_email>/<int:year>/<int:month>', methods=['GET'])
def get_budgets(user_email, year, month):
    user = get_user_by_email_or_404(user_email)
    rows = Budget.query.join(Category).filter(Budget.user_id == user.id, Budget.year == year, Budget.month == month).all()
    return jsonify({'user': user.email, 'year': year, 'month': month, 'budgets': [{'category': r.category.name, 'amount': r.amount} for r in rows]})

@bp.route('/reports/monthly_spending/<int:year>/<int:month>/<string:user_email>', methods=['GET'])
def monthly_spending(year, month, user_email):
    user = get_user_by_email_or_404(user_email)
    rows = db.session.query(Category.name, func.coalesce(func.sum(Expense.amount), 0)).join(
        Expense, Expense.category_id == Category.id
    ).filter(
        Expense.user_id == user.id,
        func.strftime('%Y', Expense.date) == str(year),
        func.strftime('%m', Expense.date) == f"{month:02d}"
    ).group_by(Category.name).all()
    res = {r[0]: float(r[1]) for r in rows}
    return jsonify({'year': year, 'month': month, 'user': user.email, 'by_category': res, 'total': sum(res.values())})

@bp.route('/reports/compare/<int:year>/<int:month>/<string:user_email>', methods=['GET'])
def compare_spending_vs_budget(year, month, user_email):
    user = get_user_by_email_or_404(user_email)
    sub_exp = db.session.query(Expense.category_id, func.sum(Expense.amount).label('spent')).filter(
        Expense.user_id == user.id,
        func.strftime('%Y', Expense.date) == str(year),
        func.strftime('%m', Expense.date) == f"{month:02d}"
    ).group_by(Expense.category_id).subquery()
    rows = db.session.query(
        Category.name,
        func.coalesce(sub_exp.c.spent, 0),
        func.coalesce(Budget.amount, 0)
    ).outerjoin(sub_exp, sub_exp.c.category_id == Category.id).outerjoin(
        Budget, and_(Budget.category_id == Category.id, Budget.user_id == user.id, Budget.year == year, Budget.month == month)
    ).all()
    return jsonify({'year': year, 'month': month, 'user': user.email, 'data': [{'category': n, 'spent': float(s), 'budget': float(b)} for n, s, b in rows]})

@bp.route('/share_groups', methods=['POST'])
def create_group():
    data = request.get_json() or {}
    owner = get_user_by_email_or_404(data.get('owner_email'))
    g = ShareGroup(name=data.get('name'), owner_id=owner.id)
    db.session.add(g)
    db.session.commit()
    return jsonify({'id': g.id, 'name': g.name, 'owner_email': owner.email}), 201

@bp.route('/share_groups/<int:group_id>/add_member', methods=['POST'])
def add_member(group_id):
    data = request.get_json() or {}
    group = ShareGroup.query.get_or_404(group_id)
    user = get_user_by_email_or_404(data.get('user_email'))
    if ShareMember.query.filter_by(group_id=group.id, user_id=user.id).first():
        abort(400, 'already member')
    m = ShareMember(group_id=group.id, user_id=user.id)
    db.session.add(m)
    db.session.commit()
    return jsonify({'group_id': group.id, 'member_id': m.id, 'user_email': user.email}), 201

@bp.route('/share_groups/<int:group_id>/shared_expenses', methods=['POST'])
def add_shared_expense(group_id):
    group = ShareGroup.query.get_or_404(group_id)
    data = request.get_json() or {}
    payer = get_user_by_email_or_404(data.get('payer_email'))
    amount = float(data.get('amount'))
    date_str = data.get('date')
    d = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
    se = SharedExpense(group_id=group.id, payer_id=payer.id, amount=amount, description=data.get('description'), date=d)
    db.session.add(se)
    db.session.commit()
    return jsonify({'id': se.id, 'group_id': group.id, 'payer_email': payer.email, 'amount': se.amount, 'date': se.date.isoformat(), 'description': se.description}), 201

@bp.route('/share_groups/<int:group_id>/shared_expenses', methods=['GET'])
def list_shared_expenses(group_id):
    group = ShareGroup.query.get_or_404(group_id)
    rows = SharedExpense.query.filter_by(group_id=group.id).order_by(SharedExpense.date.desc()).all()
    members = [m.user_id for m in group.members]
    return jsonify({
        'group_id': group.id,
        'name': group.name,
        'shared_expenses': [{
            'id': r.id,
            'payer_email': User.query.get(r.payer_id).email,
            'amount': r.amount,
            'date': r.date.isoformat(),
            'description': r.description,
            'members_count': len(members)
        } for r in rows]
    })

@bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})
