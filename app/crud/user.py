from typing import Annotated
from fastapi import Depends
from app.core.db import AsyncSessionLocal
from app.models.user import User
from app.schemas.user import UserCreate, UserInDB
from sqlalchemy import select
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def create_user(
        new_user: Annotated[UserCreate, Depends()]
) -> User:
    new_user_data = new_user.model_dump()
    password = new_user_data.pop("password")
    hashed_password = get_password_hash(password)
    new_user_data.update({"hashed_password": hashed_password})
    new_user_data.update({"disabled": False})
    db_user = User(**new_user_data)

    async with AsyncSessionLocal() as session:
        session.add(db_user)

        await session.commit()

        await session.refresh(db_user)
    return db_user


async def get_user(username: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()
    if user is not None:
        user_dict = user.__dict__
        return UserInDB(**user_dict)
