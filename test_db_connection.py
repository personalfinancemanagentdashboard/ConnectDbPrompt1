"""
Simple script to test SQLite database connection
"""
from app import app, db
from models import User, Transaction, Budget, RecurringTransaction

def test_connection():
    """Test the SQLite database connection"""
    with app.app_context():
        try:
            # Test connection by executing a simple query
            result = db.session.execute(db.text("SELECT 1"))
            print("✅ SQLite connection successful!")
            print(f"📁 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Check if tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"\n📊 Found {len(tables)} table(s):")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("\n⚠️  No tables found. Run the app to create tables.")
            
            # Try to query User table if it exists
            if 'user' in [t.lower() for t in tables]:
                user_count = User.query.count()
                print(f"\n👥 Users in database: {user_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False

if __name__ == "__main__":
    test_connection()

