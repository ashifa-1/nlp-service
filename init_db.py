from app.database import engine, Base

# create all tables
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Database tables created.")
