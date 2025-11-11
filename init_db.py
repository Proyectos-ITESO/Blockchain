"""
Initialize database tables
Run this script to create all database tables
"""
from app.db.database import engine, Base
from app.db.models import User, Message, Contact

print("Creating database tables...")

# Create all tables
Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
print("\nTables created:")
print("  - users")
print("  - messages")
print("  - contacts")
