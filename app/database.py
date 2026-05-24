from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

async def init_db():
    """Initialize database with default data"""
    from app.models import User, Task
    from app.auth import get_password_hash
    
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            admin_user = User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            print("Default admin user created")
        
        # Create a demo user if needed
        demo_user = db.query(User).filter(User.email == "demo@example.com").first()
        if not demo_user:
            demo_user = User(
                email="demo@example.com",
                username="demo",
                hashed_password=get_password_hash("demo123"),
                is_active=True,
                is_admin=False
            )
            db.add(demo_user)
            db.commit()
            print("Demo user created")
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()