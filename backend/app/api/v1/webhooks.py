from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User

router = APIRouter()
logger = structlog.get_logger()


@router.post("/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Stripe Webhook"""
    # TODO: Stripe Webhook処理を実装
    return {"message": "Stripe webhook - coming soon"}


@router.post("/firebase")
async def firebase_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Firebase Webhook"""
    # TODO: Firebase Webhook処理を実装
    return {"message": "Firebase webhook - coming soon"}


@router.post("/openai")
async def openai_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """OpenAI Webhook"""
    # TODO: OpenAI Webhook処理を実装
    return {"message": "OpenAI webhook - coming soon"}
