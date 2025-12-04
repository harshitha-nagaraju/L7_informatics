import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv


load_dotenv()


db = SQLAlchemy()




def create_app():
app = Flask(__name__)
app.config.from_object('app.config.Config')
db.init_app(app)


from . import models
from .routes import bp as api_bp
from .cli import register_cli


app.register_blueprint(api_bp, url_prefix='/api')
register_cli(app)


return app
