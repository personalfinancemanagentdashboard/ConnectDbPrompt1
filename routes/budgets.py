from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models.budget import Budget
from models.transaction import Transaction
from sqlalchemy import func, extract
from datetime import datetime, date, timedelta
from calendar import monthrange

budgets_bp = Blueprint('budgets', __name__)


def get_budget_spending(user_id, category, period='monthly'):
    today = date.today()
    
    if period == 'monthly':
        start_date = date(today.year, today.month, 1)
        _, last_day = monthrange(today.year, today.month)
        end_date = date(today.year, today.month, last_day)
    elif period == 'weekly':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    else:
        start_date = date(today.year, 1, 1)
        end_date = date(today.year, 12, 31)
    
    spent = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.category == category,
        Transaction.transaction_type == 'expense',
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).scalar() or 0.0
    
    return spent


@budgets_bp.route('/budgets')
@login_required
def index():
    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    
    budget_data = []
    for budget in budgets:
        spent = get_budget_spending(current_user.id, budget.category, budget.period)
        percentage = (spent / budget.amount * 100) if budget.amount > 0 else 0
        status = 'danger' if spent > budget.amount else 'warning' if percentage > 80 else 'success'
        
        budget_data.append({
            'budget': budget,
            'spent': spent,
            'remaining': budget.amount - spent,
            'percentage': percentage,
            'status': status
        })
    
    return render_template('budgets.html', budget_data=budget_data)


@budgets_bp.route('/budgets/add', methods=['GET', 'POST'])
@login_required
def add_budget():
    if request.method == 'POST':
        category = request.form.get('category')
        amount = request.form.get('amount')
        period = request.form.get('period', 'monthly')
        
        if not category or not amount:
            flash('Category and amount are required.', 'danger')
            return render_template('add_budget.html')
        
        try:
            amount = float(amount)
            if amount <= 0:
                flash('Amount must be greater than zero.', 'danger')
                return render_template('add_budget.html')
        except ValueError:
            flash('Invalid amount format.', 'danger')
            return render_template('add_budget.html')
        
        existing = Budget.query.filter_by(
            user_id=current_user.id,
            category=category,
            period=period
        ).first()
        
        if existing:
            flash(f'A {period} budget for {category} already exists. Please edit it instead.', 'danger')
            return render_template('add_budget.html')
        
        budget = Budget(
            user_id=current_user.id,
            category=category,
            amount=amount,
            period=period
        )
        
        db.session.add(budget)
        db.session.commit()
        
        flash('Budget created successfully!', 'success')
        return redirect(url_for('budgets.index'))
    
    return render_template('add_budget.html')


@budgets_bp.route('/budgets/edit/<int:budget_id>', methods=['GET', 'POST'])
@login_required
def edit_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    
    if budget.user_id != current_user.id:
        flash('You do not have permission to edit this budget.', 'danger')
        return redirect(url_for('budgets.index'))
    
    if request.method == 'POST':
        amount = request.form.get('amount')
        period = request.form.get('period')
        
        if not amount:
            flash('Amount is required.', 'danger')
            return render_template('edit_budget.html', budget=budget)
        
        try:
            amount = float(amount)
            if amount <= 0:
                flash('Amount must be greater than zero.', 'danger')
                return render_template('edit_budget.html', budget=budget)
        except ValueError:
            flash('Invalid amount format.', 'danger')
            return render_template('edit_budget.html', budget=budget)
        
        budget.amount = amount
        budget.period = period
        
        db.session.commit()
        
        flash('Budget updated successfully!', 'success')
        return redirect(url_for('budgets.index'))
    
    return render_template('edit_budget.html', budget=budget)


@budgets_bp.route('/budgets/delete/<int:budget_id>', methods=['POST'])
@login_required
def delete_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    
    if budget.user_id != current_user.id:
        flash('You do not have permission to delete this budget.', 'danger')
        return redirect(url_for('budgets.index'))
    
    db.session.delete(budget)
    db.session.commit()
    
    flash('Budget deleted successfully!', 'success')
    return redirect(url_for('budgets.index'))
