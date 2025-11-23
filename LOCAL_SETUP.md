# SmartFinanceAI - Local Setup Guide

## Running on Your Local System with SQLite

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Download the project** to your local computer

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set the session secret** (create a `.env` file or export):
   ```bash
   export SESSION_SECRET="your-secret-key-here"
   ```
   Or on Windows:
   ```cmd
   set SESSION_SECRET=your-secret-key-here
   ```

4. **Run the application:**
   ```bash
   gunicorn --bind 127.0.0.1:5000 --reuse-port --reload main:app
   ```
   Or simply:
   ```bash
   python -m flask run
   ```

5. **Access the app:**
   Open your browser and go to `http://localhost:5000`

### Database Information

The application is configured to use **SQLite by default** when running locally:
- Database file location: `instance/smartfinance.db`
- The database is created automatically on first run
- All your data is stored in this single file
- You can back up your data by copying this file

### Features Available

1. **User Authentication** - Register and login
2. **Transaction Tracking** - Add, edit, delete transactions
3. **PDF Upload** - Import transactions from PDF bank statements
4. **Budget Management** - Set and track budgets
5. **AI Insights** - Get intelligent financial recommendations
6. **Reports** - View spending analytics and charts
7. **Recurring Transactions** - Manage subscription and regular payments

### PDF Upload Feature

To import transactions from PDF:
1. Go to **Quick Actions** → **Upload PDF**
2. Select your bank statement PDF file
3. The system will automatically extract transactions
4. Review and edit imported transactions as needed

**Supported PDF formats:**
- Bank statements with date, description, and amount
- Transactions are automatically categorized
- Currency: Indian Rupee (₹)

### Troubleshooting

**Database not created?**
- Make sure the `instance/` directory exists (it will be created automatically)
- Check file permissions in the project directory

**PDF upload not working?**
- Ensure the PDF contains clear transaction data
- Check that pypdf is installed: `pip install pypdf`

**Port already in use?**
- Change the port: `--bind 127.0.0.1:8000` instead of 5000

### Notes

- The SQLite database file (`instance/smartfinance.db`) contains all your financial data
- Back up this file regularly to prevent data loss
- For production deployment, consider using PostgreSQL instead of SQLite
