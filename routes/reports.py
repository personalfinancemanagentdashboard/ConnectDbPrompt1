from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from app import db
from models.transaction import Transaction
from datetime import datetime, date
from sqlalchemy import func
import csv
import io

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports')
@login_required
def index():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category')
    transaction_type = request.args.get('transaction_type')
    
    query = Transaction.query.filter_by(user_id=current_user.id)
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.date >= start_date_obj)
        except ValueError:
            flash('Invalid start date format.', 'danger')
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.date <= end_date_obj)
        except ValueError:
            flash('Invalid end date format.', 'danger')
    
    if category and category != 'all':
        query = query.filter(Transaction.category == category)
    
    if transaction_type and transaction_type != 'all':
        query = query.filter(Transaction.transaction_type == transaction_type)
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    
    all_categories = db.session.query(Transaction.category).filter(
        Transaction.user_id == current_user.id
    ).distinct().all()
    categories_list = [cat[0] for cat in all_categories]
    
    return render_template('reports.html',
                         transactions=transactions,
                         total_income=total_income,
                         total_expense=total_expense,
                         balance=total_income - total_expense,
                         categories=categories_list,
                         filters={
                             'start_date': start_date,
                             'end_date': end_date,
                             'category': category,
                             'transaction_type': transaction_type
                         })


@reports_bp.route('/reports/export')
@login_required
def export_csv():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category')
    transaction_type = request.args.get('transaction_type')
    
    query = Transaction.query.filter_by(user_id=current_user.id)
    
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.date >= start_date_obj)
        except ValueError:
            flash('Invalid start date format.', 'danger')
            return redirect(url_for('reports.index'))
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Transaction.date <= end_date_obj)
        except ValueError:
            flash('Invalid end date format.', 'danger')
            return redirect(url_for('reports.index'))
    
    if category and category != 'all':
        query = query.filter(Transaction.category == category)
    
    if transaction_type and transaction_type != 'all':
        query = query.filter(Transaction.transaction_type == transaction_type)
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Date', 'Category', 'Description', 'Type', 'Amount'])
    
    for transaction in transactions:
        writer.writerow([
            transaction.date.strftime('%Y-%m-%d'),
            transaction.category,
            transaction.description or '',
            transaction.transaction_type.capitalize(),
            f'{transaction.amount:.2f}'
        ])
    
    writer.writerow([])
    writer.writerow(['Summary'])
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    writer.writerow(['Total Income', f'{total_income:.2f}'])
    writer.writerow(['Total Expenses', f'{total_expense:.2f}'])
    writer.writerow(['Balance', f'{total_income - total_expense:.2f}'])
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=transactions_report.csv'
    response.headers['Content-Type'] = 'text/csv'
    
    return response
