from fastapi import FastAPI, Request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))


@app.get("/")
def health_check():
    return {"status": "ok", "message": "FastAPI is running!"}


@app.post("/webhook")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()

    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    print(f"[受信] {user_message}")  # ログ出力

    # エコー返信
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=f"『{user_message}』と言いましたね！")
    )
