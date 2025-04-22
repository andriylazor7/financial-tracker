from flask import Blueprint, abort, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Expense, Income, RecurringTransaction
from datetime import date, datetime, timedelta

auth_bp = Blueprint("auth", __name__)
finance_bp = Blueprint("finance", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for("auth.register"))

        new_user = User(name=name, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("auth.dashboard"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html")

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    apply_recurring_transactions(current_user)
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    incomes = Income.query.filter_by(user_id=current_user.id).all()
    recurring_expenses = RecurringTransaction.query.filter_by(user_id=current_user.id, type='expense').all()
    recurring_incomes = RecurringTransaction.query.filter_by(user_id=current_user.id, type='income').all()
    
    return render_template("dashboard.html", name= current_user.name, email=current_user.email, expenses=expenses, incomes=incomes, recurring_expenses=recurring_expenses, recurring_incomes=recurring_incomes)

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

def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, [31,
        29 if year % 4 == 0 and not year % 100 == 0 or year % 400 == 0 else 28,
        31,30,31,30,31,31,30,31,30,31][month-1])
    return date(year, month, day)

def apply_recurring_transactions(user):
    today = date.today()
    recurring_transactions = RecurringTransaction.query.filter_by(user_id=user.id).all()

    for r in recurring_transactions:
        if not should_apply(r.last_applied, r.frequency):
            continue

        months_passed = (today.year - r.start_date.year) * 12 + (today.month - r.start_date.month)
        expected_date = add_months(r.start_date, months_passed)
        if expected_date > today:
            continue

        model = Expense if r.type == 'expense' else Income
        existing = model.query.filter_by(
            user_id=user.id,
            recurring_id=r.id,
            date=expected_date
        ).first()

        if not existing:
            new_transaction = model(
                category=r.category,
                amount=r.amount,
                date=expected_date,
                description=r.description,
                user_id=user.id,
                recurring_id=r.id
            )
            db.session.add(new_transaction)
            r.last_applied = expected_date  

    db.session.commit()


@finance_bp.route('/recurring')
@login_required
def recurring_transactions():
    recurring = RecurringTransaction.query.filter_by(user_id=current_user.id).all()
    return render_template('recurring.html', recurring_transactions=recurring)

@finance_bp.route('/recurring', methods=['POST'])
@login_required
def add_recurring():
    type_ = request.form.get('type')
    amount = request.form.get('amount')
    category = request.form.get('category')
    frequency = request.form.get('frequency')
    start_date = request.form.get('start_date')
    description = request.form.get('description')

    try:
        amount = float(amount)
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        flash('Invalid input for amount or date.', 'danger')
        return redirect(url_for('finance.recurring_transactions'))

    recurring = RecurringTransaction(
        user_id=current_user.id,
        type=type_,
        amount=amount,
        category=category,
        frequency=frequency,
        start_date=start_date,
        description=description
    )
    db.session.add(recurring)
    db.session.commit()
    flash('Recurring transaction added successfully.', 'success')
    return redirect(url_for('finance.recurring_transactions'))

@finance_bp.route('/recurring/delete/<int:recurring_id>', methods=['POST'])
@login_required
def delete_recurring(recurring_id):
    recurring = RecurringTransaction.query.get_or_404(recurring_id)
    if recurring.user_id != current_user.id:
        abort(403)
    
    db.session.delete(recurring)
    db.session.commit()
    flash('Recurring transaction deleted.', 'info')
    return redirect(url_for('finance.recurring_transactions'))

def should_apply(last_applied, freq):
    today = date.today()
    if not last_applied:
        return True

    if freq == "daily":
        return today > last_applied
    elif freq == "weekly":
        return (today - last_applied).days >= 7
    elif freq == "monthly":
        return today.month != last_applied.month or today.year != last_applied.year
    return False


