"""
生產者 - 發送任務到不同隊列
"""
from jobs import send_welcome_email, send_notification

def main():
    print("=== Producer: 發送任務到不同隊列 ===\n")

    # 發送到 welcome_email 隊列
    print("發送歡迎郵件任務...")
    send_welcome_email.send(1, "user1@example.com")
    send_welcome_email.send(2, "user2@example.com")
    send_welcome_email.send(3, "user3@example.com")

    # 發送到 notification 隊列
    print("發送通知任務...")
    send_notification.send(10, "你有新訊息")
    send_notification.send(11, "系統更新通知")
    send_notification.send(12, "密碼修改成功")
    send_notification.send(13, "新訂單提醒")

    print("\n✓ 所有任務已發送到各自的隊列!")
    print("- welcome_email 隊列: 3 個任務")
    print("- notification 隊列: 4 個任務")

if __name__ == "__main__":
    main()