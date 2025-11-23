from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models.recurring_transaction import RecurringTransaction
from datetime import datetime, date

recurring_bp = Blueprint('recurring', __name__)


@recurring_bp.route('/recurring')
@login_required
def index():
    recurring_transactions = RecurringTransaction.query.filter_by(user_id=current_user.id).order_by(RecurringTransaction.start_date.desc()).all()
    
    recurring_data = []
    for rt in recurring_transactions:
        next_date = rt.get_next_date() if rt.is_active else None
        recurring_data.append({
            'recurring': rt,
            'next_date': next_date
        })
    
    return render_template('recurring_transactions.html', recurring_data=recurring_data)


@recurring_bp.route('/recurring/add', methods=['GET', 'POST'])
@login_required
def add_recurring():
    if request.method == 'POST':
        transaction_type = request.form.get('transaction_type')
        category = request.form.get('category')
        amount = request.form.get('amount')
        description = request.form.get('description')
        frequency = request.form.get('frequency')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        if not all([transaction_type, category, amount, frequency, start_date_str]):
            flash('All fields except end date and description are required.', 'danger')
            return render_template('add_recurring.html')
        
        try:
            amount = float(amount)
            if amount <= 0:
                flash('Amount must be greater than zero.', 'danger')
                return render_template('add_recurring.html')
        except ValueError:
            flash('Invalid amount format.', 'danger')
            return render_template('add_recurring.html')
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid start date format.', 'danger')
            return render_template('add_recurring.html')
        
        end_date = None
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                if end_date < start_date:
                    flash('End date must be after start date.', 'danger')
                    return render_template('add_recurring.html')
            except ValueError:
                flash('Invalid end date format.', 'danger')
                return render_template('add_recurring.html')
        
        recurring = RecurringTransaction(
            user_id=current_user.id,
            transaction_type=transaction_type,
            category=category,
            amount=amount,
            description=description,
            frequency=frequency,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
        
        db.session.add(recurring)
        db.session.commit()
        
        flash('Recurring transaction created successfully!', 'success')
        return redirect(url_for('recurring.index'))
    
    return render_template('add_recurring.html')


@recurring_bp.route('/recurring/edit/<int:recurring_id>', methods=['GET', 'POST'])
@login_required
def edit_recurring(recurring_id):
    recurring = RecurringTransaction.query.get_or_404(recurring_id)
    
    if recurring.user_id != current_user.id:
        flash('You do not have permission to edit this recurring transaction.', 'danger')
        return redirect(url_for('recurring.index'))
    
    if request.method == 'POST':
        amount = request.form.get('amount')
        description = request.form.get('description')
        frequency = request.form.get('frequency')
        end_date_str = request.form.get('end_date')
        is_active = request.form.get('is_active') == 'on'
        
        if not all([amount, frequency]):
            flash('Amount and frequency are required.', 'danger')
            return render_template('edit_recurring.html', recurring=recurring)
        
        try:
            amount = float(amount)
            if amount <= 0:
                flash('Amount must be greater than zero.', 'danger')
                return render_template('edit_recurring.html', recurring=recurring)
        except ValueError:
            flash('Invalid amount format.', 'danger')
            return render_template('edit_recurring.html', recurring=recurring)
        
        end_date = None
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                if end_date < recurring.start_date:
                    flash('End date must be after start date.', 'danger')
                    return render_template('edit_recurring.html', recurring=recurring)
            except ValueError:
                flash('Invalid end date format.', 'danger')
                return render_template('edit_recurring.html', recurring=recurring)
        
        recurring.amount = amount
        recurring.description = description
        recurring.frequency = frequency
        recurring.end_date = end_date
        recurring.is_active = is_active
        
        db.session.commit()
        
        flash('Recurring transaction updated successfully!', 'success')
        return redirect(url_for('recurring.index'))
    
    return render_template('edit_recurring.html', recurring=recurring)


@recurring_bp.route('/recurring/delete/<int:recurring_id>', methods=['POST'])
@login_required
def delete_recurring(recurring_id):
    recurring = RecurringTransaction.query.get_or_404(recurring_id)
    
    if recurring.user_id != current_user.id:
        flash('You do not have permission to delete this recurring transaction.', 'danger')
        return redirect(url_for('recurring.index'))
    
    db.session.delete(recurring)
    db.session.commit()
    
    flash('Recurring transaction deleted successfully!', 'success')
    return redirect(url_for('recurring.index'))


@recurring_bp.route('/recurring/generate/<int:recurring_id>', methods=['POST'])
@login_required
def generate_now(recurring_id):
    recurring = RecurringTransaction.query.get_or_404(recurring_id)
    
    if recurring.user_id != current_user.id:
        flash('You do not have permission to generate this transaction.', 'danger')
        return redirect(url_for('recurring.index'))
    
    if not recurring.is_active:
        flash('This recurring transaction is inactive.', 'danger')
        return redirect(url_for('recurring.index'))
    
    target_date = recurring.get_next_date()
    
    if recurring.end_date and target_date > recurring.end_date:
        flash('This recurring transaction has ended.', 'danger')
        return redirect(url_for('recurring.index'))
    
    transaction = recurring.generate_transaction(target_date)
    if transaction:
        db.session.add(transaction)
        recurring.last_generated = target_date
        db.session.commit()
        flash(f'Transaction generated successfully for {target_date}!', 'success')
    else:
        flash('Unable to generate transaction.', 'danger')
    
    return redirect(url_for('recurring.index'))
