from database import engine
from models import Base

def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created!")

if __name__ == "__main__":
    initialize_database()