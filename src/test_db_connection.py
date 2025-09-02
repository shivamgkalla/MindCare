import psycopg2
from psycopg2 import OperationalError
from src.core.config import settings  # Make sure this has settings.DATABASE_URL

def test_connection():
    try:
        # psycopg2 needs "postgresql://" not "postgresql+psycopg2://"
        db_url = settings.DATABASE_URL.replace("postgresql+psycopg2", "postgresql")
        
        conn = psycopg2.connect(db_url)
        print("✅ Connection to PostgreSQL successful!")
        conn.close()
    except OperationalError as e:
        print("❌ Failed to connect to PostgreSQL.")
        print(f"Error: {e}")

if __name__ == "__main__":
    test_connection()
