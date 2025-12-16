import dramatiq
from shared.queues import QueueNames
import logging
import time

@dramatiq.actor(queue_name=QueueNames.REPORT_GENERATE)
def generate_report(report_id: int):
    logging.info(f"生成報表: {report_id}")
    time.sleep(3)
    logging.info(f"✓ 報表已生成: {report_id}")

@dramatiq.actor(queue_name=QueueNames.REPORT_SEND)
def send_report(user_id: int, report_id: int):
    logging.info(f"發送報表: user_id={user_id}, report_id={report_id}")
    time.sleep(1)
    logging.info(f"✓ 報表已發送: {report_id}")
