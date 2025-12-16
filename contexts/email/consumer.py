from dramatiq import Worker
from shared.broker import broker  # ← broker 先初始化
from shared.queues import ContextQueues
import logging

# 確保 broker 已設置好,再 import jobs
import contexts.email.jobs  # ← 這時候 @dramatiq.actor 才能正確註冊


def start_email_consumer():
    """啟動 Email Consumer"""

    queues = ContextQueues.EMAIL

    logging.info("=" * 50)
    logging.info("Email Consumer 啟動")
    logging.info(f"監聽隊列: {queues}")

    # 檢查註冊的 actors
    logging.info(f"Broker 中的 actors: {list(broker.actors.keys())}")  # ← 加這行!

    logging.info("=" * 50)

    worker = Worker(broker, worker_threads=4, queues=queues)
    logging.info("開始啟動 worker.start()...")

    try:
        worker.start()
    except KeyboardInterrupt:
        logging.info("正在關閉...")
        worker.stop()
        logging.info("已停止")

