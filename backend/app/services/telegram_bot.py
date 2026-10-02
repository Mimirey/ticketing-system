import os
import time
import requests

from dotenv import load_dotenv
from app.db.database import SessionLocal
from app.services.telegram_link import link_telegram_account

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN belum dikonfigurasi")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
def get_updates(offset=None):
    response = requests.get(
        f"{BASE_URL}/getUpdates",
        params={
            "offset": offset,
            "timeout": 30,
        },
        timeout=35,
    )
    response.raise_for_status()
    return response.json()
def send_message(chat_id, text):
    response = requests.post(
        f"{BASE_URL}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
        },
        timeout=10,
    )
    response.raise_for_status()
def handle_update(update):
    message = update.get("message")
    if not message:
        return
    text = message.get("text", "")
    chat = message.get("chat")
    if not chat:
        return
    chat_id = str(chat["id"])
    if not text.startswith("/start"):
        return
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        send_message(
            chat_id,
            "Silakan gunakan tombol Hubungkan Telegram dari aplikasi ticketing."
        )
        return
    token = parts[1].strip()
    db = SessionLocal()
    try:
        success, result = link_telegram_account(
            db=db,
            token=token,
            telegram_chat_id=chat_id,
        )
        if success:
            send_message(
                chat_id,
                " Telegram berhasil terhubung ke akun ticketing kamu."
            )
        else:
            send_message(
                chat_id,
                f"{result}"
            )

    except Exception as e:
        db.rollback()
        print(f"Telegram bot error: {e}")
        send_message(
            chat_id,
            "Terjadi kesalahan saat menghubungkan Telegram."
        )

    finally:
        db.close()


def run():
    print("Telegram linking bot started")
    offset = None
    while True:
        try:
            result = get_updates(offset)
            if not result.get("ok"):
                print("Telegram API error:", result)
                time.sleep(5)
                continue
            updates = result.get("result", [])

            for update in updates:
                offset = update["update_id"] + 1

                try:
                    handle_update(update)
                except Exception as e:
                    print(f"Error handling Telegram update: {e}")

        except Exception as e:
            print(f"Telegram polling error: {e}")
            time.sleep(5)
            
if __name__ == "__main__":
    run()