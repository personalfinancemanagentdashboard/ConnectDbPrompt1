from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models.transaction import Transaction
from services.ai_insights import get_ai_insights
from datetime import datetime
from sqlalchemy import func, extract

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).limit(10).all()
    
    total_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == 'income'
    ).scalar() or 0.0
    
    total_expense = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == 'expense'
    ).scalar() or 0.0
    
    balance = total_income - total_expense
    
    category_data = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == 'expense'
    ).group_by(Transaction.category).all()
    
    categories = [cat[0] for cat in category_data]
    amounts = [float(cat[1]) for cat in category_data]
    
    monthly_data = db.session.query(
        extract('month', Transaction.date).label('month'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == 'expense'
    ).group_by(extract('month', Transaction.date)).order_by('month').all()
    
    months = [f"Month {int(m[0])}" for m in monthly_data]
    monthly_amounts = [float(m[1]) for m in monthly_data]
    
    insights = get_ai_insights(current_user.id)
    
    return render_template('dashboard.html',
                         transactions=transactions,
                         total_income=total_income,
                         total_expense=total_expense,
                         balance=balance,
                         categories=categories,
                         amounts=amounts,
                         months=months,
                         monthly_amounts=monthly_amounts,
                         insights=insights)


@dashboard_bp.route('/add-transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        transaction_type = request.form.get('transaction_type')
        category = request.form.get('category')
        amount = request.form.get('amount')
        description = request.form.get('description')
        date_str = request.form.get('date')
        
        if not transaction_type or not category or not amount or not date_str:
            flash('All fields except description are required.', 'danger')
            return render_template('add_transaction.html')
        
        try:
            amount = float(amount)
            if amount <= 0:
                flash('Amount must be greater than zero.', 'danger')
                return render_template('add_transaction.html')
        except ValueError:
            flash('Invalid amount format.', 'danger')
            return render_template('add_transaction.html')
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('add_transaction.html')
        
        transaction = Transaction(
            user_id=current_user.id,
            transaction_type=transaction_type,
            category=category,
            amount=amount,
            description=description,
            date=date_obj
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('add_transaction.html')


@dashboard_bp.route('/transactions')
@login_required
def all_transactions():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    return render_template('transactions.html', transactions=transactions)


@dashboard_bp.route('/edit-transaction/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    
    if transaction.user_id != current_user.id:
        flash('You do not have permission to edit this transaction.', 'danger')
        return redirect(url_for('dashboard.all_transactions'))
    
    if request.method == 'POST':
        transaction_type = request.form.get('transaction_type')
        category = request.form.get('category')
        amount = request.form.get('amount')
        description = request.form.get('description')
        date_str = request.form.get('date')
        
        if not transaction_type or not category or not amount or not date_str:
            flash('All fields except description are required.', 'danger')
            return render_template('edit_transaction.html', transaction=transaction)
        
        try:
            amount = float(amount)
            if amount <= 0:
                flash('Amount must be greater than zero.', 'danger')
                return render_template('edit_transaction.html', transaction=transaction)
        except ValueError:
            flash('Invalid amount format.', 'danger')
            return render_template('edit_transaction.html', transaction=transaction)
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('edit_transaction.html', transaction=transaction)
        
        transaction.transaction_type = transaction_type
        transaction.category = category
        transaction.amount = amount
        transaction.description = description
        transaction.date = date_obj
        
        db.session.commit()
        
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('dashboard.all_transactions'))
    
    return render_template('edit_transaction.html', transaction=transaction)


@dashboard_bp.route('/delete-transaction/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    
    if transaction.user_id != current_user.id:
        flash('You do not have permission to delete this transaction.', 'danger')
        return redirect(url_for('dashboard.all_transactions'))
    
    db.session.delete(transaction)
    db.session.commit()
    
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('dashboard.all_transactions'))
