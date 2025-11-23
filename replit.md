# SmartFinanceAI - Personal Finance Tracker

## Overview

SmartFinanceAI is a Flask-based personal finance management application that helps users track income, expenses, budgets, and recurring transactions. The system provides financial insights through an AI-powered analytics service and offers visual reporting through charts and data exports. Built with Python/Flask, it uses SQLAlchemy ORM for database management and provides both web UI and REST API interfaces.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Template Engine & UI Framework**
- **Jinja2** templating for server-side rendering
- **Bootstrap 5** for responsive component library and grid system
- **Chart.js** for financial data visualization (category spending, monthly trends)
- **Inter font** from Google Fonts for clean typography optimized for financial data display

**Design System**
- Material Design-inspired approach focused on data legibility and trust
- Consistent spacing primitives (p-4, p-6, p-8 for padding; gap-4, gap-6 for grids)
- Three-column responsive grid for dashboard stats (grid-cols-1 md:grid-cols-3)
- Color-coded financial indicators (green for income, red for expense, blue for balance)
- Custom CSS variables for theme consistency (--primary-color, --success-color, etc.)

### Backend Architecture

**Web Framework**
- **Flask** as the core web framework with blueprint-based modular routing
- **Flask-Login** for session-based user authentication and authorization
- **ProxyFix** middleware for handling reverse proxy headers (x_proto, x_host)

**Application Structure**
- Factory pattern via `create_app()` for application initialization
- Blueprint organization by feature domain:
  - `auth_bp`: User authentication (login, register, logout)
  - `dashboard_bp`: Main dashboard and transaction management
  - `api_bp`: RESTful API endpoints (v1 prefixed)
  - `budgets_bp`: Budget creation and tracking
  - `reports_bp`: Financial reports and CSV export
  - `recurring_bp`: Recurring transaction management

**Authentication Flow**
- Password hashing using Werkzeug's `generate_password_hash` and `check_password_hash`
- Session-based authentication with login redirects for protected routes
- User loader function for Flask-Login integration

### Data Layer

**ORM & Models**
- **SQLAlchemy** with declarative base for object-relational mapping
- Connection pooling with `pool_recycle` (300s) and `pool_pre_ping` for reliability

**Database Schema**
- **Users**: Core authentication table with username, email, password_hash
- **Transactions**: Financial records with user_id (FK), amount, category, type, date, description
  - Indexed on user_id and date for query performance
  - Cascade deletion when user is deleted
- **Budgets**: Category-based spending limits with period (monthly/weekly/yearly)
  - Unique constraint on (user_id, category, period) to prevent duplicates
- **RecurringTransactions**: Automated transaction templates with frequency patterns
  - Supports daily, weekly, biweekly, monthly, yearly frequencies
  - Tracks last_generated date and active status

**Query Patterns**
- Aggregate functions (SUM, COUNT) for financial summaries
- Date-based filtering and grouping for trend analysis
- Dynamic relationship queries using SQLAlchemy's `lazy='dynamic'`

### Business Logic Layer

**AI Insights Service** (`services/ai_insights.py`)
- Spending trend analysis comparing recent months
- Savings rate calculation and personalized recommendations
- Top spending category identification
- Rule-based insights (not external AI API integration)

**Budget Tracking**
- Real-time spending calculation against budget limits
- Period-based filtering (monthly, weekly, yearly)
- Visual progress indicators with status thresholds (danger >100%, warning >80%, success <80%)

**Recurring Transactions**
- Date calculation engine for next occurrence based on frequency
- Handles edge cases (month-end dates, leap years)
- Active/inactive status management

### API Design

**REST Endpoints** (`/api/v1/*`)
- `POST /auth/register`: User registration with validation
- `POST /auth/login`: API-based authentication with session creation
- `GET /transactions`: List user transactions with filtering
- `POST /transactions`: Create new transaction
- Returns JSON responses with appropriate HTTP status codes (200, 201, 400, 404)

**Error Handling**
- Form validation with flash messages for web UI
- JSON error responses for API endpoints
- User-friendly error messages categorized by severity (danger, warning, info, success)

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web framework (latest stable)
- **Flask-SQLAlchemy**: ORM integration for Flask
- **Flask-Login**: User session management
- **Werkzeug**: WSGI utilities and security helpers

### Database
- **SQLite**: Embedded database (via SQLAlchemy)
- Connection string from `DATABASE_URL` environment variable
- Database file stored in `/instance/smartfinance.db` (auto-created)

### Frontend Libraries (CDN)
- **Bootstrap 5.3.0**: UI components and responsive grid
- **Chart.js 4.4.0**: Data visualization library
- **Google Fonts (Inter)**: Typography

### Configuration Management
- **Environment Variables**:
  - `SESSION_SECRET`: Flask session encryption key (falls back to dev key)
  - `DATABASE_URL`: SQLAlchemy database connection string
- Configuration class in `config.py` with engine options for connection pooling

### Development & Deployment
- **Python 3**: Runtime environment
- **Replit**: Target deployment platform
- No external API integrations (AI insights are rule-based calculations)