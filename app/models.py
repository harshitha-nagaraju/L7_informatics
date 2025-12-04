from datetime import date
from . import db


class User(db.Model):
id = db.Column(db.Integer, primary_key=True)
name = db.Column(db.String(120))
email = db.Column(db.String(255), unique=True, nullable=False)


expenses = db.relationship('Expense', backref='user', lazy=True)


class Category(db.Model):
id = db.Column(db.Integer, primary_key=True)
name = db.Column(db.String(80), nullable=False, unique=True)


class Budget(db.Model):
id = db.Column(db.Integer, primary_key=True)
user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
year = db.Column(db.Integer, nullable=False)
month = db.Column(db.Integer, nullable=False)
amount = db.Column(db.Float, nullable=False)


user = db.relationship('User')
category = db.relationship('Category')


class Expense(db.Model):
id = db.Column(db.Integer, primary_key=True)
user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
amount = db.Column(db.Float, nullable=False)
description = db.Column(db.String(300))
date = db.Column(db.Date, nullable=False)


category = db.relationship('Category')


class ShareGroup(db.Model):
id = db.Column(db.Integer, primary_key=True)
name = db.Column(db.String(120), nullable=False)
owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
members = db.relationship('ShareMember', backref='group')


class ShareMember(db.Model):
id = db.Column(db.Integer, primary_key=True)
group_id = db.Column(db.Integer, db.ForeignKey('share_group.id'))
user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class SharedExpense(db.Model):
id = db.Column(db.Integer, primary_key=True)
group_id = db.Column(db.Integer, db.ForeignKey('share_group.id'))
payer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
amount = db.Column(db.Float, nullable=False)
description = db.Column(db.String(300))
date = db.Column(db.Date, nullable=False)
