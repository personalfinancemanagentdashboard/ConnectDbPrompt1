"""
Initialize the SQLite database and create all tables
"""
from app import app, db
import models

def init_database():
    """Create all database tables"""
    with app.app_context():
        try:
            print("Creating database tables...")
            db.create_all()
            print("[SUCCESS] Database tables created successfully!")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"\n[INFO] Created {len(tables)} table(s):")
            for table in tables:
                print(f"   - {table}")
            
            return True
        except Exception as e:
            print(f"[ERROR] Failed to create tables: {str(e)}")
            return False

if __name__ == "__main__":
    init_database()

