from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__, template_folder="templates_", static_folder="static_")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance_tracker.db"
    app.config["SECRET_KEY"] = "your_secret_key_here"

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes import auth_bp  
    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
