from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

logger = structlog.get_logger()


class EmailService:
    """メールサービス"""

    def __init__(self):
        self.smtp_server = "smtp.gmail.com"  # 設定可能
        self.smtp_port = 587
        self.sender_email = "noreply@bridgeline.com"  # 設定可能
        self.sender_password = ""  # 環境変数から取得

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False
    ) -> bool:
        """メールを送信"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject

            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            # SMTPサーバーに接続
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            # server.login(self.sender_email, self.sender_password)  # 認証情報が必要

            text = msg.as_string()
            server.sendmail(self.sender_email, to_email, text)
            server.quit()

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    async def send_welcome_email(self, to_email: str, username: str) -> bool:
        """ウェルカムメールを送信"""
        subject = "BridgeLINEへようこそ！"
        body = f"""
        <html>
        <body>
            <h2>BridgeLINEへようこそ！</h2>
            <p>こんにちは、{username}さん</p>
            <p>BridgeLINEアカウントの作成が完了しました。</p>
            <p>チームコミュニケーションの改善を始めましょう！</p>
        </body>
        </html>
        """
        return await self.send_email(to_email, subject, body, is_html=True)

    async def send_password_reset_email(
        self, to_email: str, reset_token: str
    ) -> bool:
        """パスワードリセットメールを送信"""
        subject = "パスワードリセットのご案内"
        body = f"""
        <html>
        <body>
            <h2>パスワードリセットのご案内</h2>
            <p>パスワードリセットのリクエストを受け付けました。</p>
            <p>以下のリンクをクリックしてパスワードを再設定してください：</p>
            <a href="https://bridgeline.com/reset-password?token={reset_token}">
                パスワードをリセット
            </a>
            <p>このリンクは24時間有効です。</p>
        </body>
        </html>
        """
        return await self.send_email(to_email, subject, body, is_html=True)

    async def send_team_invitation_email(
        self, to_email: str, team_name: str, inviter_name: str
    ) -> bool:
        """チーム招待メールを送信"""
        subject = f"{team_name}チームへの招待"
        body = f"""
        <html>
        <body>
            <h2>チーム招待のご案内</h2>
            <p>{inviter_name}さんがあなたを{team_name}チームに招待しています。</p>
            <p>以下のリンクからチームに参加してください：</p>
            <a href="https://bridgeline.com/teams/join">
                チームに参加
            </a>
        </body>
        </html>
        """
        return await self.send_email(to_email, subject, body, is_html=True)

    async def send_notification_email(
        self, to_email: str, title: str, message: str
    ) -> bool:
        """通知メールを送信"""
        subject = f"BridgeLINE通知: {title}"
        body = f"""
        <html>
        <body>
            <h2>{title}</h2>
            <p>{message}</p>
            <p>詳細はBridgeLINEアプリでご確認ください。</p>
        </body>
        </html>
        """
        return await self.send_email(to_email, subject, body, is_html=True)


# シングルトンインスタンス
email_service = EmailService()
