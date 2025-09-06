import sys
import os

# Add the current directory to Python path so it can find the app module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal
from app.models import Base, Email, Response
from datetime import datetime

# Create all tables
print("Creating database tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
except Exception as e:
    print(f"❌ Error creating tables: {e}")
    sys.exit(1)

# Test database connection
db = SessionLocal()
try:
    # Create a test email
    test_email = Email(
        sender="test@example.com",
        subject="Test Email",
        body="This is a test email body.",
        sent_date=datetime.now(),
        sentiment="Neutral",
        sentiment_confidence=0.8,
        priority="Normal",
        status="pending"
    )
    
    # Add to database
    db.add(test_email)
    db.commit()
    db.refresh(test_email)
    
    # Query the email back
    stored_email = db.query(Email).filter(Email.id == test_email.id).first()
    
    if stored_email:
        print(f"✅ Database test successful!")
        print(f"   - Email ID: {stored_email.id}")
        print(f"   - Sender: {stored_email.sender}")
        print(f"   - Subject: {stored_email.subject}")
        print(f"   - Priority: {stored_email.priority}")
        print(f"   - Created at: {stored_email.created_at}")
    else:
        print("❌ Database test failed - no email found!")
        
except Exception as e:
    print(f"❌ Database test failed with error: {e}")
    
finally:
    db.close()

print("Database setup complete!")
