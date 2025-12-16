import dramatiq
from shared.queues import QueueNames
import logging
import time

@dramatiq.actor(queue_name=QueueNames.DATA_PROCESS)
def process_csv(file_path: str):
    logging.info(f"處理 CSV: {file_path}")
    time.sleep(3)
    logging.info(f"✓ CSV 處理完成: {file_path}")

@dramatiq.actor(queue_name=QueueNames.DATA_ANALYZE)
def analyze_data(data_id: int):
    logging.info(f"分析數據: {data_id}")
    time.sleep(2)
    logging.info(f"✓ 數據分析完成: {data_id}")
