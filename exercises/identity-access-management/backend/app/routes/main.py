import logging

from fastapi import APIRouter, Request

from app.models import User

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("/documents")
async def documents(request: Request) -> User:
    user: User = request.state.user

    return user
