from app import db
from datetime import datetime, timedelta
from models.transaction import Transaction


class RecurringTransaction(db.Model):
    __tablename__ = 'recurring_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    frequency = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    last_generated = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_next_date(self, from_date=None):
        if not from_date:
            from_date = self.last_generated or self.start_date
        
        if self.frequency == 'daily':
            return from_date + timedelta(days=1)
        elif self.frequency == 'weekly':
            return from_date + timedelta(weeks=1)
        elif self.frequency == 'biweekly':
            return from_date + timedelta(weeks=2)
        elif self.frequency == 'monthly':
            month = from_date.month + 1
            year = from_date.year
            if month > 12:
                month = 1
                year += 1
            day = from_date.day
            while day > 0:
                try:
                    return from_date.replace(year=year, month=month, day=day)
                except ValueError:
                    day -= 1
            return from_date
        elif self.frequency == 'yearly':
            try:
                return from_date.replace(year=from_date.year + 1)
            except ValueError:
                return from_date.replace(year=from_date.year + 1, day=28)
        return from_date
    
    def generate_transaction(self, target_date):
        if self.end_date and target_date > self.end_date:
            return None
        
        transaction = Transaction(
            user_id=self.user_id,
            transaction_type=self.transaction_type,
            category=self.category,
            amount=self.amount,
            description=f"{self.description} (Recurring)",
            date=target_date
        )
        
        return transaction
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'category': self.category,
            'transaction_type': self.transaction_type,
            'description': self.description,
            'frequency': self.frequency,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'last_generated': self.last_generated.isoformat() if self.last_generated else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<RecurringTransaction {self.id} - {self.frequency} {self.transaction_type} ${self.amount}>'
