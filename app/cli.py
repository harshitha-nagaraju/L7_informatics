import click
def register_cli(app):
@app.cli.command('add-expense')
@click.option('--user', required=True)
@click.option('--category', required=True)
@click.option('--amount', required=True, type=float)
@click.option('--date', required=False)
@click.option('--desc', required=False)
def add_expense(user, category, amount, date, desc):
"""Add an expense from CLI: flask add-expense --user demo@example.com --category Food --amount 10.5"""
u = User.query.filter_by(email=user).first()
if not u:
click.echo('User not found')
return
c = Category.query.filter_by(name=category).first()
if not c:
click.echo('Category not found')
return
d = datetime.today().date() if not date else datetime.strptime(date, '%Y-%m-%d').date()
e = Expense(user_id=u.id, category_id=c.id, amount=amount, description=desc, date=d)
db.session.add(e)
db.session.commit()


# compute spent for this month for this category
from sqlalchemy import func
year = d.year
month = d.month
spent = db.session.query(func.sum(Expense.amount)).filter(Expense.user_id==u.id, Expense.category_id==c.id, func.strftime('%Y', Expense.date)==str(year), func.strftime('%m', Expense.date)==f"{month:02d}").scalar() or 0
budget = Budget.query.filter_by(user_id=u.id, category_id=c.id, year=year, month=month).first()
if budget:
check_and_alert(u, c, spent, budget.amount)
click.echo('Expense added')


@app.cli.command('set-budget')
@click.option('--user', required=True)
@click.option('--category', required=True)
@click.option('--year', required=True, type=int)
@click.option('--month', required=True, type=int)
@click.option('--amount', required=True, type=float)
def set_budget(user, category, year, month, amount):
u = User.query.filter_by(email=user).first()
if not u:
click.echo('User not found')
return
c = Category.query.filter_by(name=category).first()
if not c:
click.echo('Category not found')
return
b = Budget.query.filter_by(user_id=u.id, category_id=c.id, year=year, month=month).first()
if not b:
b = Budget(user_id=u.id, category_id=c.id, year=year, month=month, amount=amount)
db.session.add(b)
else:
b.amount = amount
db.session.commit()
click.echo('Budget set')
