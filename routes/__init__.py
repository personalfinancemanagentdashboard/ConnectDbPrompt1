from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.api import api_bp
from routes.budgets import budgets_bp
from routes.reports import reports_bp
from routes.recurring import recurring_bp

__all__ = ['auth_bp', 'dashboard_bp', 'api_bp', 'budgets_bp', 'reports_bp', 'recurring_bp']
