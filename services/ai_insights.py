import os
from models import db
from models.transaction import Transaction

from sqlalchemy import func, extract
from datetime import date, timedelta
from calendar import month_name

import google.generativeai as genai


# ---------------------------------------------
# GEMINI API SETUP
# ---------------------------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def generate_gemini_summary(prompt):
    """Generate an AI summary using Gemini API"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI Error: {str(e)}"


# ---------------------------------------------
# ANALYTICS HELPERS
# ---------------------------------------------
def get_spending_trend(user_id, months=3):
    today = date.today()
    monthly_spending = []

    for i in range(months, 0, -1):
        month_ago = today - timedelta(days=30 * i)
        start_of_month = date(month_ago.year, month_ago.month, 1)

        # Determine next month
        if month_ago.month == 12:
            next_month = date(month_ago.year + 1, 1, 1)
        else:
            next_month = date(month_ago.year, month_ago.month + 1, 1)

        spent = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "expense",
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
        return "Try to save at least 10% of your income. Reduce a small spend category."
    elif savings_rate < 20:
        return f"You are saving {savings_rate:.1f}%. Try reaching 20% by cutting optional expenses."
    elif savings_rate < 30:
        return f"Great! You save {savings_rate:.1f}%. Aim for 30% for stronger financial health."
    else:
        return f"Amazing! {savings_rate:.1f}% savings rate. Keep it up!"


def analyze_seasonal_spending(user_id):
    today = date.today()
    current_month = today.month

    all_months = db.session.query(
        extract("month", Transaction.date).label("month"),
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "expense"
    ).group_by(extract("month", Transaction.date)).all()

    if not all_months or len(all_months) < 2:
        return None

    month_totals = {int(m[0]): float(m[1]) for m in all_months}

    highest_month = max(month_totals, key=month_totals.get)
    lowest_month = min(month_totals, key=month_totals.get)

    return {
        "highest_month": month_name[highest_month],
        "highest_amount": month_totals[highest_month],
        "lowest_month": month_name[lowest_month],
        "lowest_amount": month_totals[lowest_month]
    }


# ---------------------------------------------
# MAIN INSIGHTS FUNCTION
# ---------------------------------------------
def get_ai_insights(user_id):
    insights = []

    # Income / Expense summary
    total_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "income"
    ).scalar() or 0.0

    total_expense = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "expense"
    ).scalar() or 0.0

    # High spending
    if total_expense > total_income:
        insights.append({
            "type": "warning",
            "message": "Your expenses are higher than your income this month.",
            "icon": "⚠️"
        })
    else:
        savings = total_income - total_expense
        rate = (savings / total_income * 100) if total_income > 0 else 0
        insights.append({
            "type": "success",
            "message": f"You saved ₹{savings:.2f} ({rate:.1f}% of income).",
            "icon": "💰"
        })

    # Top category
    category_data = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "expense"
    ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).all()

    if category_data:
        top_category = category_data[0]
        insights.append({
            "type": "info",
            "message": f"Top spending category: {top_category[0]} (₹{top_category[1]:.2f}).",
            "icon": "📊"
        })

    # Few transactions → beginner user
    transaction_count = Transaction.query.filter_by(user_id=user_id).count()
    if transaction_count < 5:
        insights.append({
            "type": "info",
            "message": "Add more transactions for deeper insights.",
            "icon": "💡"
        })

    # Spending ratio
    if total_income > 0:
        ratio = (total_expense / total_income) * 100
        if ratio < 50:
            insights.append({
                "type": "success",
                "message": f"Great! You are spending only {ratio:.1f}% of your income.",
                "icon": "🌟"
            })
        elif ratio > 90:
            insights.append({
                "type": "warning",
                "message": f"Warning: You are spending {ratio:.1f}% of your income.",
                "icon": "💸"
            })

    # Trend analysis
    trend, current_month_spending = get_spending_trend(user_id)
    if abs(trend) > 50:
        if trend > 0:
            insights.append({
                "type": "warning",
                "message": f"Your spending increased by ₹{trend:.2f} from last month.",
                "icon": "📈"
            })
        else:
            insights.append({
                "type": "success",
                "message": f"You reduced spending by ₹{abs(trend):.2f} since last month!",
                "icon": "📉"
            })

    # Savings suggestion
    suggestion = get_savings_recommendation(user_id, total_income, total_expense)
    if suggestion:
        insights.append({
            "type": "info",
            "message": f"Savings tip: {suggestion}",
            "icon": "💡"
        })

    # Seasonal pattern
    seasonal_data = analyze_seasonal_spending(user_id)
    if seasonal_data:
        insights.append({
            "type": "info",
            "message": f"Highest spending: {seasonal_data['highest_month']} (₹{seasonal_data['highest_amount']:.2f}), lowest: {seasonal_data['lowest_month']} (₹{seasonal_data['lowest_amount']:.2f}).",
            "icon": "📅"
        })

    # ---------------------------------------------
    # GEMINI AI SUMMARY (Main AI Assistant Output)
    # ---------------------------------------------
    prompt = f"""
You are SmartFinanceAI, an expert financial assistant.

Based on this user's monthly data:

Income: ₹{total_income}
Expenses: ₹{total_expense}
Top categories: {category_data}
User insights: {', '.join([i['message'] for i in insights])}

Create a short, helpful financial advice summary in 2–3 sentences.
"""

    ai_summary = generate_gemini_summary(prompt)

    if ai_summary and not ai_summary.startswith("AI Error"):
        insights.append({
            "type": "info",
            "message": ai_summary,
            "icon": "🤖"
        })
    else:
        insights.append({
            "type": "warning",
            "message": "AI assistant is temporarily unavailable.",
            "icon": "⚠️"
        })

    return insights
