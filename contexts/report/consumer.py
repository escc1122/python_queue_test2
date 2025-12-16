from dramatiq import Worker
from shared.broker import broker
from shared.queues import ContextQueues
import logging
import contexts.report.jobs

def start_report_consumer():
    """啟動 Report Consumer"""
    
    queues = ContextQueues.REPORT
    
    logging.info("=" * 50)
    logging.info("Report Consumer 啟動")
    logging.info(f"監聽隊列: {queues}")
    logging.info("=" * 50)
    
    worker = Worker(broker, worker_threads=2, queues=queues)
    
    try:
        worker.start()
    except KeyboardInterrupt:
        logging.info("正在關閉...")
        worker.stop()
        logging.info("已停止")
