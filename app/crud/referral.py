from datetime import datetime, timedelta, timezone
from typing import Optional
from app.core.db import AsyncSessionLocal
from app.models.referral import Referral
from app.models.user import User
from sqlalchemy import select
import random
import string

from app.schemas.user import UserInDB

CODE_LENGTH = 10


def generate_random_code():
    characters = string.ascii_letters + string.digits
    random_code = "".join(
        random.choice(characters) for _ in range(CODE_LENGTH)
    )
    return random_code


async def create_referral(
        user: UserInDB, referred_user_id: int = None
) -> Referral:
    """Функция для создания записи в базе данных
    реферальных пользователей"""

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == user.username)
        )
        user = result.scalars().first()
        result = await session.execute(
            select(Referral).where(Referral.user_id == user.id)
        )

        referral = result.scalars().first()
        if referral is None:
            referral_data = {
                "user_id": user.id,
                "referrer_id": referred_user_id,
                "code": None,
                "lifetime": None,
            }
            db_referral = Referral(**referral_data)
            session.add(db_referral)
            await session.commit()
            await session.refresh(db_referral)
            referral = db_referral
    return referral


async def generate_referral_code(user: UserInDB) -> Referral:
    """Фукнция генерации реферального кода с ограниченным сроком действия"""

    referral = await create_referral(user=user)
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Referral).where(Referral.user_id == referral.user_id)
        )
        referral = result.scalars().first()
        expire = datetime.now(timezone.utc) + timedelta(days=30)
        referral.code = generate_random_code()
        referral.lifetime = expire
        await session.commit()
        await session.refresh(referral)
    return referral


async def remove_referral_code(user: UserInDB) -> Referral:
    """Фукнция удаления реферального кода"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == user.username)
        )
    user = result.scalars().first()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Referral).where(Referral.user_id == user.id)
        )
        referral = result.scalars().first()
        referral.code = None
        referral.lifetime = None
        await session.commit()
        await session.refresh(referral)
    return referral


async def get_referral(code: str) -> Optional[Referral]:
    """Функция, возвращающая модель Referral по реф. коду,
    если срок действия не истек"""

    async with AsyncSessionLocal() as session:
        now = datetime.now(timezone.utc)
        result = await session.execute(
            select(Referral).where(
                (Referral.code == code) & (Referral.lifetime > now)
            )
        )
        referral = result.scalar_one_or_none()
        return referral


async def get_referral_by_email(email: str) -> Optional[Referral]:
    """Функция, возвращающая модель Referral по e-mail пользователя,
    если срок действия не истек"""

    async with AsyncSessionLocal() as session:
        now = datetime.now(timezone.utc)
        result = await session.execute(
            select(Referral).where(Referral.lifetime > now).join(
                User, onclause=User.id == Referral.user_id
                ).where(User.email == email)
        )
        referral = result.scalar_one_or_none()
        return referral


async def get_referral_by_id(id: int) -> Optional[Referral]:
    """Функция, возвращающая модель Referral по e-mail пользователя,
    если срок действия не истек"""

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Referral).where(Referral.referrer_id == id).join(
                User, onclause=User.id == Referral.user_id
                )
        )
        result = await session.execute(
            select(User).join(
                Referral, onclause=User.id == Referral.user_id
                ).where(Referral.referrer_id == id)
        )
        referral = result.scalars().all()
        return referral
