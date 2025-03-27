from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Category, Expense, Income
from datetime import datetime

auth_bp = Blueprint("auth", __name__)
finance_bp = Blueprint("finance", __name__)

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
    today = datetime.today().strftime('%Y-%m-%d')
    category_filter = request.args.get('category', '').strip()
    date_filter = request.args.get('filter_date', '').strip()  
    amount_filter = request.args.get('amount', '').strip()

    query = Expense.query.filter(Expense.user_id == current_user.id)  

    if category_filter:
        query = query.filter(Expense.category == category_filter)

    if date_filter:
        try:
            date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Expense.date) == date_obj)
        except ValueError:
            flash("Invalid date format.", "warning")

    if amount_filter:
        try:
            max_amount = float(amount_filter)
            query = query.filter(Expense.amount <= max_amount)
        except ValueError:
            flash("Invalid amount value.", "warning")

    expenses = query.order_by(Expense.date.desc()).all()
    categories = [c[0] for c in db.session.query(Expense.category.distinct()).filter(Expense.user_id == current_user.id).all()]
    return render_template('expenses.html', expenses=expenses, categories=categories, today=today)


@finance_bp.route("/expenses/add", methods=["POST"])
@login_required
def add_expense():
    amount = request.form.get("amount")
    category = request.form.get("category")
    description = request.form.get("description")
    date = request.form.get("date")

    if not amount or not category:
        flash("Amount and category are required!", "danger")
        return redirect(url_for("finance.expenses"))

    expense = Expense(user_id=current_user.id, amount=float(amount), category=' '.join(category.split()), description=description, date=datetime.strptime(date, '%Y-%m-%d'))
    db.session.add(expense)
    db.session.commit()
    flash("Expense added successfully!", "success")
    return redirect(url_for("finance.expenses"))

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
    today = datetime.today().strftime('%Y-%m-%d')
    category_filter = request.args.get('category', '').strip()
    date_filter = request.args.get('filter_date', '').strip()
    amount_filter = request.args.get('amount', '').strip()

    query = Income.query.filter(Income.user_id == current_user.id)

    if category_filter:
        query = query.filter(Income.category == category_filter)
        
    if date_filter:
        try:
            date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Income.date) == date_obj)
        except ValueError:
            flash("Invalid date format.", "warning")
            
    if amount_filter:
        try:
            max_amount = float(amount_filter)
            query = query.filter(Income.amount <= max_amount)
        except ValueError:
            flash("Invalid amount value.", "warning")

    incomes = query.order_by(Income.date.desc()).all()
    categories = [c[0] for c in db.session.query(Income.category.distinct()).filter_by(user_id=current_user.id).all()]
    return render_template('incomes.html', incomes=incomes, categories=categories, today=today)

@finance_bp.route("/incomes/add", methods=["POST"])
@login_required
def add_income():
    amount = request.form.get("amount")
    category = request.form.get("category")
    description = request.form.get("description")
    date = request.form.get("date")

    if not amount or not category:
        flash("Amount and category are required!", "danger")
        return redirect(url_for("finance.incomes"))

    income = Income(user_id=current_user.id, amount=float(amount), category=' '.join(category.split()), description=description, date=datetime.strptime(date, '%Y-%m-%d'))
    db.session.add(income)
    db.session.commit()
    flash("Income added successfully!", "success")
    return redirect(url_for("finance.incomes"))

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