from app import db
from models.transaction import Transaction
from sqlalchemy import func, extract
from datetime import datetime, date, timedelta
from calendar import month_name


def get_spending_trend(user_id, months=3):
    today = date.today()
    monthly_spending = []
    
    for i in range(months, 0, -1):
        month_ago = today - timedelta(days=30 * i)
        start_of_month = date(month_ago.year, month_ago.month, 1)
        
        if month_ago.month == 12:
            next_month = date(month_ago.year + 1, 1, 1)
        else:
            next_month = date(month_ago.year, month_ago.month + 1, 1)
        
        spent = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == 'expense',
            Transaction.date >= start_of_month,
            Transaction.date < next_month
        ).scalar() or 0.0
        
        monthly_spending.append(spent)
    
    if len(monthly_spending) >= 2:
        trend = monthly_spending[-1] - monthly_spending[-2]
        return trend, monthly_spending[-1]
    
    return 0, monthly_spending[-1] if monthly_spending else 0


def get_savings_recommendation(user_id, total_income, total_expense):
    if total_income <= 0:
        return None
    
    savings_rate = ((total_income - total_expense) / total_income) * 100
    
    if savings_rate < 10:
        return "Aim to save at least 10% of your income. Start by identifying one category to reduce spending."
    elif savings_rate < 20:
        return "You're saving {:.1f}% - good start! Try to reach 20% by cutting discretionary expenses.".format(savings_rate)
    elif savings_rate < 30:
        return "Great savings rate of {:.1f}%! Consider increasing to 30% for long-term financial security.".format(savings_rate)
    else:
        return "Excellent {:.1f}% savings rate! You're building strong financial habits.".format(savings_rate)


def analyze_seasonal_spending(user_id):
    today = date.today()
    current_month = today.month
    
    current_month_spending = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'expense',
        extract('month', Transaction.date) == current_month
    ).scalar() or 0.0
    
    avg_spending = db.session.query(func.avg(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'expense'
    ).scalar() or 0.0
    
    all_months = db.session.query(
        extract('month', Transaction.date).label('month'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'expense'
    ).group_by(extract('month', Transaction.date)).all()
    
    if len(all_months) >= 2:
        month_totals = {int(m[0]): float(m[1]) for m in all_months}
        if current_month in month_totals:
            highest_month = max(month_totals, key=month_totals.get)
            lowest_month = min(month_totals, key=month_totals.get)
            
            if highest_month != lowest_month:
                return {
                    'highest_month': month_name[highest_month],
                    'highest_amount': month_totals[highest_month],
                    'lowest_month': month_name[lowest_month],
                    'lowest_amount': month_totals[lowest_month]
                }
    
    return None


def get_ai_insights(user_id):
    insights = []
    
    total_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'income'
    ).scalar() or 0.0
    
    total_expense = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'expense'
    ).scalar() or 0.0
    
    if total_expense > total_income:
        insights.append({
            'type': 'warning',
            'message': 'High spending alert! Your expenses exceed your income.',
            'icon': '⚠️'
        })
    elif total_income > total_expense:
        savings = total_income - total_expense
        savings_rate = (savings / total_income * 100) if total_income > 0 else 0
        insights.append({
            'type': 'success',
            'message': f'Great job! You\'re saving ${savings:.2f} ({savings_rate:.1f}% of income).',
            'icon': '✅'
        })
    
    category_data = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'expense'
    ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).all()
    
    if category_data:
        top_category = category_data[0]
        insights.append({
            'type': 'info',
            'message': f'Your top spending category is "{top_category[0]}" with ${top_category[1]:.2f}.',
            'icon': '📊'
        })
    
    transaction_count = Transaction.query.filter_by(user_id=user_id).count()
    
    if transaction_count == 0:
        insights.append({
            'type': 'info',
            'message': 'Start tracking your finances by adding your first transaction!',
            'icon': '🚀'
        })
    elif transaction_count < 5:
        insights.append({
            'type': 'info',
            'message': 'Add more transactions to get better financial insights.',
            'icon': '💡'
        })
    
    if total_income > 0 and total_expense > 0:
        expense_ratio = (total_expense / total_income * 100)
        if expense_ratio < 50:
            insights.append({
                'type': 'success',
                'message': f'Excellent! You\'re only spending {expense_ratio:.1f}% of your income.',
                'icon': '🌟'
            })
        elif expense_ratio > 90:
            insights.append({
                'type': 'warning',
                'message': f'You\'re spending {expense_ratio:.1f}% of your income. Consider reducing expenses.',
                'icon': '💰'
            })
    
    trend, current_month_spending = get_spending_trend(user_id, months=3)
    if abs(trend) > 50:
        if trend > 0:
            insights.append({
                'type': 'warning',
                'message': f'Spending trend: Your expenses increased by ${abs(trend):.2f} compared to last month.',
                'icon': '📈'
            })
        else:
            insights.append({
                'type': 'success',
                'message': f'Spending trend: Great! You reduced expenses by ${abs(trend):.2f} compared to last month.',
                'icon': '📉'
            })
    
    savings_tip = get_savings_recommendation(user_id, total_income, total_expense)
    if savings_tip:
        insights.append({
            'type': 'info',
            'message': f'Savings tip: {savings_tip}',
            'icon': '💡'
        })
    
    seasonal_data = analyze_seasonal_spending(user_id)
    if seasonal_data:
        difference = seasonal_data['highest_amount'] - seasonal_data['lowest_amount']
        insights.append({
            'type': 'info',
            'message': f'Seasonal insight: Your highest spending was in {seasonal_data["highest_month"]} (${seasonal_data["highest_amount"]:.2f}), lowest in {seasonal_data["lowest_month"]} (${seasonal_data["lowest_amount"]:.2f}).',
            'icon': '📅'
        })
    
    if category_data and len(category_data) >= 2:
        top_two = category_data[:2]
        combined_spending = top_two[0][1] + top_two[1][1]
        if total_expense > 0:
            percentage = (combined_spending / total_expense) * 100
            if percentage > 60:
                insights.append({
                    'type': 'info',
                    'message': f'{percentage:.0f}% of your spending is on {top_two[0][0]} and {top_two[1][0]}. Consider diversifying or optimizing these categories.',
                    'icon': '🎯'
                })
    
    if not insights:
        insights.append({
            'type': 'info',
            'message': 'Keep tracking your transactions for personalized insights!',
            'icon': '📈'
        })
    
    return insights
