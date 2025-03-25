from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Category, Expense, Income

auth_bp = Blueprint("auth", __name__)
finance_bp = Blueprint("finance", __name__)

@auth_bp.route("/base")
@login_required
def base():
    return render_template("base.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for("auth.register"))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("auth.dashboard"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html")
  
@auth_bp.route("/dashboard")
@login_required
def dashboard():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    incomes = Income.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", username=current_user.username, expenses=expenses, incomes=incomes)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
  
  
@finance_bp.route('/expenses')
@login_required
def expenses():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    return render_template('expenses.html', expenses=expenses)

@finance_bp.route("/expenses/add", methods=["GET", "POST"])
@login_required
def add_expense():
  if request.method == "POST":
    amount = request.form.get("amount")
    category = request.form.get("category")
    description = request.form.get("description")
    
    if not amount or not category:
      flash("Amount and category are required!", "dagner")
      return redirect(url_for("finance.add_expence"))
    
    expense = Expense(user_id=current_user.id, amount=float(amount), category=category, description=description)
    db.session.add(expense)
    db.session.commit()
    flash("Expence added successfully!", "success")
    return redirect(url_for("finance.expenses"))
  
  return render_template("add_expense.html")

@finance_bp.route("/expenses/delete/<int:expense_id>", methods=["POST"])
@login_required
def delete_expenses(expense_id):
  expense = Expense.query.get_or_404(expense_id)
  if expense.user_id != current_user.id:
    flash("You do not have permission to delete this expense!", "danger")
    return redirect(url_for("finance.expenses"))
  
  db.session.delete(expense)
  db.session.commit()
  flash("Expense deleted successfully!", "success")
  return redirect(url_for("finance.expenses"))

@finance_bp.route('/incomes')
@login_required
def incomes():
    incomes = Income.query.filter_by(user_id=current_user.id).all()
    return render_template('incomes.html', incomes=incomes)

@finance_bp.route("/incomes/add", methods=["GET", "POST"])
@login_required
def add_income():
    if request.method == "POST":
        amount = request.form.get("amount")
        category = request.form.get("category")
        description = request.form.get("description")

        if not amount or not category:
            flash("Amount and category are required!", "danger")
            return redirect(url_for("finance.add_income"))

        income = Income(user_id=current_user.id, amount=float(amount), category=category, description=description)
        db.session.add(income)
        db.session.commit()
        flash("Income added successfully!", "success")
        return redirect(url_for("finance.incomes"))

    return render_template("add_income.html")

@finance_bp.route("/incomes/delete/<int:income_id>", methods=["POST"])
@login_required
def delete_income(income_id):
    income = Income.query.get_or_404(income_id)
    if income.user_id != current_user.id:
        flash("You do not have permission to delete this income!", "danger")
        return redirect(url_for("finance.incomes"))

    db.session.delete(income)
    db.session.commit()
    flash("Income deleted successfully!", "success")
    return redirect(url_for("finance.incomes"))


