from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder="templates_", static_folder="static_")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance_tracker.db"
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your_secret_key_here")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.routes import auth_bp  
    app.register_blueprint(auth_bp)

    with app.app_context():
      try:
        db.create_all()
      except Exception as e:
        print(f"Error creating database: {e}")

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
