import os
from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, current_user
from werkzeug.middleware.proxy_fix import ProxyFix

# Import db from models
from models import db

# Initialize LoginManager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # ------------------------
    # CONFIGURATION
    # ------------------------
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
    app.config['SECRET_KEY'] = "your-secret-key"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ------------------------
    # INITIALIZE EXTENSIONS
    # ------------------------
    db.init_app(app)
    login_manager.init_app(app)

    # ------------------------
    # REGISTER BLUEPRINTS
    # ------------------------
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.budgets import budgets_bp
    from routes.reports import reports_bp   # ★ ADD REPORTS BLUEPRINT

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(reports_bp)       # ★ REGISTER REPORTS BLUEPRINT

    # ------------------------
    # HOME ROUTE
    # ------------------------
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return render_template('landing.html')

    # ------------------------
    # CREATE DATABASE TABLES
    # ------------------------
    with app.app_context():
        from models.user import User
        from models.transaction import Transaction
        from models.budget import Budget     # ★ INCLUDE BUDGET MODEL

        db.create_all()

    return app


# ------------------------
# USER LOADER FOR LOGIN
# ------------------------
from models.user import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ------------------------
# RUN APPLICATION
# ------------------------
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
