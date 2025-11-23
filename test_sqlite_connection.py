"""
Simple standalone script to test SQLite database connection
"""
import sqlite3
import os

def test_sqlite_connection():
    """Test SQLite database connection directly"""
    db_path = 'instance/smartfinance.db'  # Flask-SQLAlchemy default location
    alt_db_path = 'smartfinance.db'  # Alternative location
    
    # Try to find the database file
    db_file = None
    if os.path.exists(db_path):
        db_file = db_path
        print(f"[OK] Found database at: {db_path}")
    elif os.path.exists(alt_db_path):
        db_file = alt_db_path
        print(f"[OK] Found database at: {alt_db_path}")
    else:
        print(f"[INFO] Database file not found. Will create new one at: {db_path}")
        # Create instance directory if it doesn't exist
        os.makedirs('instance', exist_ok=True)
        db_file = db_path
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Test connection with a simple query
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        print("[SUCCESS] SQLite connection successful!")
        print(f"[INFO] SQLite version: {sqlite3.sqlite_version}")
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if tables:
            print(f"\n[INFO] Found {len(tables)} table(s):")
            for table in tables:
                table_name = table[0]
                # Get row count for each table
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"   - {table_name}: {count} row(s)")
        else:
            print("\n[WARNING] No tables found. Run the Flask app to create tables.")
        
        # Close connection
        conn.close()
        print(f"\n[SUCCESS] Connection closed successfully.")
        return True
        
    except sqlite3.Error as e:
        print(f"[ERROR] SQLite error: {str(e)}")
        return False
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_sqlite_connection()

