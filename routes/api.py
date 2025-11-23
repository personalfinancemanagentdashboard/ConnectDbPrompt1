from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user, login_user
from app import db
from models.user import User
from models.transaction import Transaction
from services.ai_insights import get_ai_insights
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


@api_bp.route('/auth/register', methods=['POST'])
def api_register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'User registered successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }), 201


@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user is None or not user.check_password(data.get('password')):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    login_user(user)
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }), 200


@api_bp.route('/transactions', methods=['GET'])
@login_required
def api_get_transactions():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    
    return jsonify({
        'transactions': [t.to_dict() for t in transactions]
    }), 200


@api_bp.route('/transactions/create', methods=['POST'])
@login_required
def api_create_transaction():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['transaction_type', 'category', 'amount', 'date']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        amount = float(data.get('amount'))
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than zero'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid amount format'}), 400
    
    try:
        date_obj = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    transaction = Transaction(
        user_id=current_user.id,
        transaction_type=data.get('transaction_type'),
        category=data.get('category'),
        amount=amount,
        description=data.get('description', ''),
        date=date_obj
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'message': 'Transaction created successfully',
        'transaction': transaction.to_dict()
    }), 201


@api_bp.route('/insights', methods=['GET'])
@login_required
def api_get_insights():
    insights = get_ai_insights(current_user.id)
    
    return jsonify({
        'insights': insights
    }), 200
