"""
領域事件 - 跨 Context 通信介面

DomainEvents 負責:
1. 封裝跨 Context 的任務發送邏輯
2. 避免循環依賴
3. 統一事件命名和參數
"""
from dramatiq import Message
from shared.broker import broker
from shared.queues import QueueNames
import logging
import uuid
import time


class DomainEvents:
    """
    領域事件發布器

    使用方式:
        from shared.events import DomainEvents
        DomainEvents.email_sent(user_id, "welcome", "user@example.com")
    """

    @staticmethod
    def _send_task(actor_name: str, queue_name: str, *args, **kwargs):
        """
        內部方法:發送任務到隊列

        Args:
            actor_name: actor 函數名稱 (字串)
            queue_name: 目標隊列名稱
            *args: 任務的位置參數
            **kwargs: 任務的關鍵字參數
        """
        try:
            # 方式 1: 嘗試從已註冊的 actors 取得 (如果在同一個進程)
            if actor_name in broker.actors:
                actor = broker.actors[actor_name]
                msg = actor.message(*args, **kwargs)
                logging.debug(f"使用已註冊 actor: {actor_name}")
            else:
                # 方式 2: 手動構造 Message (跨服務通信)
                msg = Message(
                    queue_name=queue_name,
                    actor_name=actor_name,
                    args=args,
                    kwargs=kwargs,
                    options={},
                    message_id=str(uuid.uuid4()),
                    message_timestamp=int(time.time() * 1000)
                )
                logging.debug(f"手動構造 message: {actor_name}")

            # 發送到隊列
            broker.enqueue(msg)
            logging.info(f"📤 [Event] {actor_name} → {queue_name}")

        except Exception as e:
            logging.error(f"✗ 發送任務失敗: {actor_name}, error={e}", exc_info=True)

    @staticmethod
    def generate_report(report_id: int):
        DomainEvents._send_task(
            "generate_report",
            QueueNames.REPORT_GENERATE,
            report_id,
        )

    @staticmethod
    def send_report(user_id: int, report_id: int):
        DomainEvents._send_task(
            "send_report",
            QueueNames.REPORT_GENERATE,
            user_id,
            report_id,
        )