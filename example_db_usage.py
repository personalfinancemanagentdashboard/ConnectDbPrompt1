"""
Example script showing how to use SQLite database with Flask-SQLAlchemy
"""
from app import app, db
from models import User, Transaction, Budget, RecurringTransaction

def example_usage():
    """Examples of database operations"""
    with app.app_context():
        # Example 1: Create a new user
        print("Example 1: Creating a new user...")
        new_user = User(
            username="testuser",
            email="test@example.com"
        )
        new_user.set_password("password123")
        db.session.add(new_user)
        db.session.commit()
        print(f"Created user: {new_user.username} (ID: {new_user.id})")
        
        # Example 2: Query users
        print("\nExample 2: Querying users...")
        users = User.query.all()
        print(f"Total users: {len(users)}")
        for user in users:
            print(f"  - {user.username} ({user.email})")
        
        # Example 3: Query with filters
        print("\nExample 3: Finding user by username...")
        user = User.query.filter_by(username="testuser").first()
        if user:
            print(f"Found user: {user.username}")
        
        # Example 4: Update a record
        print("\nExample 4: Updating user...")
        if user:
            user.email = "updated@example.com"
            db.session.commit()
            print(f"Updated email to: {user.email}")
        
        # Example 5: Delete a record
        print("\nExample 5: Deleting user...")
        if user:
            db.session.delete(user)
            db.session.commit()
            print("User deleted")

if __name__ == "__main__":
    print("=" * 50)
    print("SQLite Database Usage Examples")
    print("=" * 50)
    print("\nNote: This requires all Flask dependencies to be installed.")
    print("Run: pip install -r requirements.txt (or use uv/pip install)\n")
    
    try:
        example_usage()
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        print("\nMake sure all dependencies are installed first!")

