from fastapi import APIRouter

from .users.router import router as users_router

root_router = APIRouter()

root_router.include_router(users_router)
