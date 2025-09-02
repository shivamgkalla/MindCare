from src.database import engine, Base

# Import ALL model modules so they register with Base
from src.auth import auth_models
from src.users import user_models
from src.coaches import coach_models
from src.bookings import booking_models
from src.journals import journal_models


def create_tables():
    print("Creating tables....")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")


if __name__ == "__main__":
    create_tables()
