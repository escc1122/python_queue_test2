"""
消費者 - 用 Thread 處理兩個不同的隊列
"""
from dramatiq import Worker
from broker import broker
from threading import Thread
import time
import jobs.email

def start_worker(queue_name, worker_threads, worker_name):
    """啟動一個 Worker 處理指定隊列"""
    print(f"{worker_name} 已啟動,監聽隊列: {queue_name}")

    worker = Worker(
        broker,
        worker_threads=worker_threads,
        queues=[queue_name]
    )

    worker.start()

def main():
    print("=== Consumer: 啟動任務處理器 ===\n")

    # Thread 1: 處理 welcome_email 隊列,2 個線程
    welcome_thread = Thread(
        target=start_worker,
        args=("welcome_email", 2, "WelcomeEmailWorker"),
        daemon=True
    )
    welcome_thread.start()

    # Thread 2: 處理 notification 隊列,3 個線程
    notification_thread = Thread(
        target=start_worker,
        args=("notification", 3, "NotificationWorker"),
        daemon=True
    )
    notification_thread.start()

    print("\n所有 workers 已啟動")
    print("- WelcomeEmailWorker: 2 個線程處理 welcome_email 隊列")
    print("- NotificationWorker: 3 個線程處理 notification 隊列")
    print("\n按 Ctrl+C 停止\n")

    # 保持運行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n正在停止所有 workers...")
        print("所有 workers 已停止")

if __name__ == "__main__":
    main()