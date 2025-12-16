import dramatiq
import time

@dramatiq.actor(queue_name="welcome_email")
def send_welcome_email(user_id: int, email: str):
    print(f"[歡迎郵件] 發送給 {email}")
    time.sleep(2)
    print(f"✓ 歡迎郵件已發送給用戶 {user_id}")  # ← 改成 print

@dramatiq.actor(queue_name="notification")
def send_notification(user_id: int, message: str):
    print(f"[通知] 用戶 {user_id}: {message}")
    time.sleep(1)
    print("✓ 通知已發送")  # ← 改成 print