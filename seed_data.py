from app import create_app, db
from app.models import User, Category


app = create_app()
with app.app_context():
if not User.query.filter_by(email='demo@example.com').first():
u = User(name='Demo', email='demo@example.com')
db.session.add(u)
for cat in ['Food','Transport','Entertainment','Rent','Utilities']:
if not Category.query.filter_by(name=cat).first():
db.session.add(Category(name=cat))
db.session.commit()
print('Seeded')
