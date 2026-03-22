from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text
import os
from config import settings
import logging

logger = logging.getLogger(__name__)

load_dotenv()

def get_engine():
    database_url = settings.database_url
    if not database_url:
        error_msg = "DATABASE_URL is not set in environment variables"
        logger.error(error_msg)
        raise ValueError(error_msg)
    try:
        engine = create_engine(database_url, echo=True)
        logger.info("Database engine created successfully")
        return engine
    except Exception as e:
        error_msg = f"Failed to create database engine: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

engine = get_engine()

# Import models to ensure metadata is populated
from models import User, Product, Order, OrderItem, Session as DBSession, CartItem

def get_db():
    with Session(engine) as session:
        yield session

def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False