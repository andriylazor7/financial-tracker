from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = "SECRET_KEY"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app import routes, models

