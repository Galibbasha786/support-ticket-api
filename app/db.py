from sqlalchemy import create_engine # create_engine Creates a connection manager
#Engine know which database to connect to and how to connect to it. It manages a pool of connections and provides a way to execute SQL statements against the database.
from sqlalchemy.orm import sessionmaker, declarative_base
#Every model inherits from Base. declartive_base() creates a base class from which all models will inherit
#sessionmaker() creates a class that can be used to create sessions with the database
from app.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False 
    #SQLite is a lightweight database that doesn't support multiple threads accessing the same database connection at the same time. The check_same_thread=False argument allows multiple threads to use the same connection, which is necessary for FastAPI's asynchronous nature.

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
) # create_engine() creates a new SQLAlchemy engine instance that will connect to the database specified by settings.DATABASE_URL. The connect_args argument is used to pass additional connection parameters to the database driver. In this case, it's used to disable the thread check for SQLite databases.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# sessionmaker() creates a new session factory that will create new database sessions when called. The autocommit=False argument means that changes to the database won't be automatically committed after each operation, and autoflush=False means that changes won't be automatically flushed to the database before each query. The bind=engine argument tells the session factory to use the engine we created earlier to connect to the database.
Base = declarative_base()
#this declartive_base() function creates a new base class that all of our database models will inherit from. This base class contains metadata about the database schema, such as table names and column types, and allows SQLAlchemy to map our Python classes to database tables.

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
#get_db() is a function that returns a new session from the SessionLocal class.
#The yield keyword is used to return the session from the function, and the finally block is used to close the session.