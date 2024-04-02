from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.core.db import Base


class Referral(Base):
    __tablename__ = "referrals"

    code = Column(String(10), unique=True, nullable=True)  # код
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)  # User
    referrer_id = Column(Integer, ForeignKey('users.id'))  # User кто привел
    lifetime = Column(DateTime, unique=False, nullable=True)  # время жизни
