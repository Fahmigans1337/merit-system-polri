from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

_is_sqlite = settings.DATABASE_URL.startswith('sqlite')

if _is_sqlite:
    # SQLite - untuk local development tanpa PostgreSQL
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={'check_same_thread': False},
    )
    @event.listens_for(engine, 'connect')
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()
else:
    # PostgreSQL - untuk production / Docker
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    '''FastAPI dependency: yield DB session, close after request.'''
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
