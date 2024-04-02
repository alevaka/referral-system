from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from app.core.user import create_access_token, get_current_active_user
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.schemas.user import UserCreate, User, Token

from app.core.user import logout_for_invalidate_token

from app.crud.user import authenticate_user, create_user, get_user

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.get("/users/me", tags=["users"])
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@router.post("/token", tags=["tokens"])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = await authenticate_user(
        form_data.username,
        form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/users/register", tags=["users"])
async def register_user(
    new_user: Annotated[UserCreate, Depends()]
):
    user = await get_user(username=new_user.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists",
        )
    else:
        await create_user(new_user)

    return status.HTTP_201_CREATED


@router.post("/users/logout", tags=["tokens"])
async def logout_user(
    blacklist_token: Annotated[str, Depends(logout_for_invalidate_token)]
):
    return blacklist_token
