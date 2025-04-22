from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db

class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password_hash = db.Column(db.String(256), nullable=False)
  
  def set_password(self, password):
    self.password_hash = generate_password_hash(password)
    
  def check_password(self, password):
    return check_password_hash(self.password_hash, password)
  
class Category(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False, unique=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  
  def __repr__(self):
    return f'<Category {self.name}>'

class Expense(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  amount = db.Column(db.Float, nullable=False)
  category = db.Column(db.String(100), nullable=False)
  date = db.Column(db.DateTime, default=datetime.utcnow)
  description = db.Column(db.String(255))
  recurring_id = db.Column(db.Integer, nullable=True)
  
  user = db.relationship('User', backref=db.backref('expenses', lazy=True))
  
class Income(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  amount = db.Column(db.Float, nullable=False)
  category = db.Column(db.String(100), nullable=False)
  date = db.Column(db.DateTime, default=datetime.utcnow)
  description = db.Column(db.String(255))
  recurring_id = db.Column(db.Integer, nullable=True)
  
  user = db.relationship('User', backref=db.backref('incomes', lazy=True))
  
class RecurringTransaction(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  type = db.Column(db.String(10), nullable=False)  
  amount = db.Column(db.Float, nullable=False)
  category = db.Column(db.String(100), nullable=False)
  description = db.Column(db.String(255))
  start_date = db.Column(db.Date, nullable=False)
  frequency = db.Column(db.String(20), nullable=False)  
  last_applied = db.Column(db.Date, nullable=True)

  user = db.relationship('User', backref=db.backref('recurring_transactions', lazy=True))
  