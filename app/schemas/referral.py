from typing import ClassVar, List

from pydantic import BaseModel

from app.schemas.user import UserCreate


class ReferralCreate(BaseModel):
    pass


class UserCreateRef(UserCreate):
    referral_code: str | None = None
    disabled: ClassVar[bool] = True
