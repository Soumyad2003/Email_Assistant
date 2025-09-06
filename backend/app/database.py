from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database URL (file will be created automatically)
SQLALCHEMY_DATABASE_URL = "sqlite:///./email_assistant.db"

# Create SQLite engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for our models
Base = declarative_base()

# Dependency function to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
