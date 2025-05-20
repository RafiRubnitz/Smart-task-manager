# config/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ניתן להחליף את זה ל-PostgreSQL או MySQL בקלות בהמשך
DATABASE_URL = "sqlite:///task.db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
