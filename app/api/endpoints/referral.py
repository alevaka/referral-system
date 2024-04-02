from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List
from app.core.user import get_current_active_user

from app.api.endpoints.user import register_user
from app.crud.referral import (
    create_referral,
    remove_referral_code,
    generate_referral_code,
    get_referral,
    get_referral_by_email,
    get_referral_by_id
)
from app.crud.user import get_user
from app.schemas.referral import UserCreateRef
from app.schemas.user import UserCreate, User


router = APIRouter()


@router.post("/users/register_ref", tags=["referral"])
async def register_user_ref(
    new_user: Annotated[UserCreateRef, Depends()]
) -> User:
    """Эндпоинт для создания нового пользователя с учётом
    ввода реферального кода"""

    referral_code = new_user.referral_code
    new_user_data = new_user.model_dump()
    referral_code = new_user_data.pop("referral_code")
    referral = await get_referral(code=referral_code)
    if referral is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect referral code.",
        )

    new_user = UserCreate(**new_user_data)
    result_status = await register_user(new_user)
    if result_status == status.HTTP_201_CREATED:
        user = await get_user(username=new_user.username)
    await create_referral(user, referral.user_id)
    return user


@router.post("/referrals/create", tags=["referral"])
async def create_referral_code(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """Эндпоинт для создания реферального кода
    для авторизованного пользователя"""

    referral = await generate_referral_code(user=current_user)
    return referral


@router.post("/referrals/delete", tags=["referral"])
async def delete_referral_code(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """Эндпоинт для удаления реферального кода
    для авторизованного пользователя"""

    referral = await remove_referral_code(user=current_user)
    return referral


@router.get("/referrals/get_by_email", tags=["referral"])
async def get_referral_code(
    referral: Annotated[UserCreateRef, Depends(get_referral_by_email)]
):
    """Эндпоинт для получения реферального кода
    по e-mail пользователя"""

    if referral is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No actual referral code for this e-mail.",
        )
    return referral.code


@router.get("/referrals/get_referrals_by_id", tags=["referral"],
            response_model=List[User])
async def get_referral_id(
    referrals: Annotated[User, Depends(get_referral_by_id)],
):
    """Эндпоинт для получения списка рефералов по id"""

    if referrals is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No actual referral code for this e-mail.",
        )
    return referrals
