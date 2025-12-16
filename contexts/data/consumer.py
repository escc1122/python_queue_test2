from dramatiq import Worker
from shared.broker import broker
from shared.queues import ContextQueues
import logging
import contexts.data.jobs

def start_data_consumer():
    """啟動 Data Consumer"""

    queues = ContextQueues.DATA

    logging.info("=" * 50)
    logging.info("Data Consumer 啟動")
    logging.info(f"監聽隊列: {queues}")
    logging.info("=" * 50)

    worker = Worker(broker, worker_threads=8, queues=queues)

    try:
        worker.start()
    except KeyboardInterrupt:
        logging.info("正在關閉...")
        worker.stop()
        logging.info("已停止")
