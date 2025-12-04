
from datetime import date

class UserSchema:
    @staticmethod
    def dump(user):
        if not user:
            return None
        return {
            'id': user.id,
            'name': user.name,
            'email': user.email
        }

class CategorySchema:
    @staticmethod
    def dump(category):
        if not category:
            return None
        return {
            'id': category.id,
            'name': category.name
        }

class ExpenseSchema:
    @staticmethod
    def dump(expense):
        if not expense:
            return None
        return {
            'id': expense.id,
            'user_id': expense.user_id,
            'category_id': expense.category_id,
            'category': getattr(expense, 'category').name if getattr(expense, 'category', None) else None,
            'amount': float(expense.amount),
            'description': expense.description,
            'date': expense.date.isoformat() if isinstance(expense.date, date) else str(expense.date)
        }

class BudgetSchema:
    @staticmethod
    def dump(budget):
        if not budget:
            return None
        return {
            'id': budget.id,
            'user_id': budget.user_id,
            'category_id': budget.category_id,
            'category': getattr(budget, 'category').name if getattr(budget, 'category', None) else None,
            'year': budget.year,
            'month': budget.month,
            'amount': float(budget.amount)
        }

class SharedExpenseSchema:
    @staticmethod
    def dump(se):
        if not se:
            return None
        return {
            'id': se.id,
            'group_id': se.group_id,
            'payer_id': se.payer_id,
            'payer_email': getattr(se, 'payer').email if getattr(se, 'payer', None) else None,
            'amount': float(se.amount),
            'description': se.description,
            'date': se.date.isoformat() if isinstance(se.date, date) else str(se.date)
        }

class ShareGroupSchema:
    @staticmethod
    def dump(group):
        if not group:
            return None
        members = []
        for m in getattr(group, 'members', []) or []:
            u = getattr(m, 'user', None)
            members.append({'id': u.id, 'email': u.email} if u else {'id': m.user_id})
        return {
            'id': group.id,
            'name': group.name,
            'owner_id': group.owner_id,
            'members': members
        }
