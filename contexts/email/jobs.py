import uuid

import dramatiq
from dramatiq import Message

from shared.queues import QueueNames
from shared.broker import broker  # ← 明確 import broker
import logging
import time
from shared.events import DomainEvents

logging.info("開始註冊 email actors...")


@dramatiq.actor(queue_name=QueueNames.EMAIL_WELCOME, broker=broker)  # ← 明確指定 broker
def send_welcome_email(user_id: int, email: str):
    logging.info(f"發送歡迎郵件: user_id={user_id}, email={email}")
    time.sleep(2)
    logging.info(f"✓ 郵件已發送: {user_id}")

    DomainEvents.generate_report(9999)
    DomainEvents.send_report(user_id, 9999)


    send_notification.send(user_id, "send_welcome_email->send_notification")


@dramatiq.actor(queue_name=QueueNames.EMAIL_NOTIFICATION, broker=broker)  # ← 明確指定 broker
def send_notification(user_id: int, message: str):
    logging.info(f"發送通知: user_id={user_id}, message={message}")
    time.sleep(1)
    logging.info(f"✓ 通知已發送: {user_id}")


logging.info(f"email actors 註冊完成,actor names: send_welcome_email, send_notification")
