"""
統一入口
"""
import sys
import time

from shared.logger import setup_logger
import logging
import shared.broker  # ← 明確 import broker 模組

# 初始化 logger
setup_logger()

def run_consumer(context_name: str):
    """啟動 consumer"""
    
    if context_name == "email":
        from contexts.email.consumer import start_email_consumer
        start_email_consumer()
        
    elif context_name == "data":
        from contexts.data.consumer import start_data_consumer
        start_data_consumer()
        
    elif context_name == "report":
        from contexts.report.consumer import start_report_consumer
        start_report_consumer()
        
    else:
        logging.error(f"未知的 context: {context_name}")
        sys.exit(1)

def run_producer():
    """執行 producer"""

    
    from contexts.email.jobs import send_welcome_email
    from contexts.data.jobs import process_csv
    from contexts.report.jobs import generate_report
    
    logging.info("=== Producer 發送任務 ===")
    
    send_welcome_email.send(1, "user1@example.com")
    logging.info("已發送: send_welcome_email(1)")
    
    send_welcome_email.send(2, "user2@example.com")
    logging.info("已發送: send_welcome_email(2)")
    
    process_csv.send("/data/sales.csv")
    logging.info("已發送: process_csv")
    
    generate_report.send(101)
    logging.info("已發送: generate_report(101)")
    
    logging.info("✓ 所有任務已發送")

def main():
    if len(sys.argv) < 2:
        print("使用方式:")
        print("  python app.py consumer <context>")
        print("  python app.py producer")
        print("\n可用 context: email, data, report")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode == "consumer":
        if len(sys.argv) < 3:
            print("請指定 context: email, data, report")
            sys.exit(1)
        context = sys.argv[2].lower()
        run_consumer(context)
        
    elif mode == "producer":
        run_producer()
        
    else:
        logging.error(f"未知模式: {mode}")
        sys.exit(1)

    # 保持運行
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\n正在停止所有 workers...")
        print("所有 workers 已停止")

if __name__ == "__main__":
    main()
