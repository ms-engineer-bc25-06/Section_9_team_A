from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc
import structlog
import secrets
from datetime import datetime, timedelta

from app.repositories.invitation_repository import invitation_repository
from app.services.email_service import email_service

logger = structlog.get_logger()


class InvitationService:
    """招待サービス"""

    async def create_invitation(
        self,
        db: AsyncSession,
        inviter_id: int,
        invitee_email: str,
        team_id: Optional[int] = None,
        role: str = "member",
        expires_in_days: int = 7
    ) -> Dict[str, Any]:
        """招待を作成"""
        try:
            # 招待トークンを生成
            invitation_token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

            # 招待データを作成
            invitation_data = {
                "inviter_id": inviter_id,
                "invitee_email": invitee_email,
                "team_id": team_id,
                "role": role,
                "token": invitation_token,
                "expires_at": expires_at,
                "status": "pending"
            }

            # データベースに保存
            invitation = await invitation_repository.create_invitation(db, invitation_data)

            # 招待メールを送信
            if team_id:
                team_name = "チーム"  # 実際のチーム名を取得
                await email_service.send_team_invitation_email(
                    invitee_email, team_name, "招待者"
                )
            else:
                await email_service.send_notification_email(
                    invitee_email,
                    "BridgeLINEへの招待",
                    "BridgeLINEアプリへの招待を受けました。"
                )

            return {
                "invitation_id": invitation.id,
                "token": invitation_token,
                "expires_at": expires_at.isoformat(),
                "status": "created"
            }

        except Exception as e:
            logger.error(f"Failed to create invitation: {str(e)}")
            raise

    async def get_invitation_by_token(
        self, db: AsyncSession, token: str
    ) -> Optional[Any]:
        """トークンで招待を取得"""
        return await invitation_repository.get_invitation_by_token(db, token)

    async def accept_invitation(
        self, db: AsyncSession, token: str, user_id: int
    ) -> bool:
        """招待を受け入れる"""
        try:
            invitation = await self.get_invitation_by_token(db, token)
            if not invitation:
                return False

            if invitation.status != "pending":
                return False

            if invitation.expires_at < datetime.utcnow():
                return False

            # 招待を承認済みに更新
            await invitation_repository.update_invitation_status(
                db, invitation.id, "accepted"
            )

            # チームにメンバーを追加（チーム招待の場合）
            if invitation.team_id:
                from app.services.team_service import team_service
                await team_service.add_member(
                    db, invitation.team_id, user_id, invitation.role
                )

            logger.info(f"Invitation accepted by user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to accept invitation: {str(e)}")
            return False

    async def decline_invitation(
        self, db: AsyncSession, token: str
    ) -> bool:
        """招待を辞退する"""
        try:
            invitation = await self.get_invitation_by_token(db, token)
            if not invitation:
                return False

            await invitation_repository.update_invitation_status(
                db, invitation.id, "declined"
            )

            logger.info(f"Invitation declined: {token}")
            return True

        except Exception as e:
            logger.error(f"Failed to decline invitation: {str(e)}")
            return False

    async def cancel_invitation(
        self, db: AsyncSession, invitation_id: int, user_id: int
    ) -> bool:
        """招待をキャンセルする（招待者のみ）"""
        try:
            invitation = await invitation_repository.get_invitation(db, invitation_id)
            if not invitation:
                return False

            if invitation.inviter_id != user_id:
                return False

            await invitation_repository.update_invitation_status(
                db, invitation_id, "cancelled"
            )

            logger.info(f"Invitation cancelled: {invitation_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to cancel invitation: {str(e)}")
            return False

    async def get_user_invitations(
        self, db: AsyncSession, user_id: int, status: Optional[str] = None
    ) -> List[Any]:
        """ユーザーの招待一覧を取得"""
        return await invitation_repository.get_user_invitations(db, user_id, status)

    async def get_pending_invitations(
        self, db: AsyncSession, email: str
    ) -> List[Any]:
        """保留中の招待を取得"""
        return await invitation_repository.get_pending_invitations(db, email)

    async def resend_invitation(
        self, db: AsyncSession, invitation_id: int, user_id: int
    ) -> bool:
        """招待を再送信"""
        try:
            invitation = await invitation_repository.get_invitation(db, invitation_id)
            if not invitation:
                return False

            if invitation.inviter_id != user_id:
                return False

            if invitation.status != "pending":
                return False

            # 新しい有効期限を設定
            new_expires_at = datetime.utcnow() + timedelta(days=7)
            await invitation_repository.update_invitation_expiry(
                db, invitation_id, new_expires_at
            )

            # 招待メールを再送信
            if invitation.team_id:
                team_name = "チーム"  # 実際のチーム名を取得
                await email_service.send_team_invitation_email(
                    invitation.invitee_email, team_name, "招待者"
                )

            logger.info(f"Invitation resent: {invitation_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to resend invitation: {str(e)}")
            return False


# シングルトンインスタンス
invitation_service = InvitationService()
