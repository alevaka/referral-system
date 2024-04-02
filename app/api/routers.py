from fastapi import APIRouter

from app.api.endpoints import (
    referral_router,
    user_router
)

main_router = APIRouter()
main_router.include_router(user_router)
main_router.include_router(referral_router)
