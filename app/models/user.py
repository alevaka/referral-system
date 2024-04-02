from sqlalchemy import Column, String, Boolean

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    username = Column(String(16), unique=True, nullable=False)
    full_name = Column(String(50), unique=False, nullable=True)
    email = Column(String(50), unique=True, nullable=True)
    hashed_password = Column(String(100), unique=True, nullable=False)
    disabled = Column(Boolean)
