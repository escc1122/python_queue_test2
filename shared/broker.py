import dramatiq
from dramatiq.brokers.redis import RedisBroker
import os

# 從環境變數讀取 Redis 配置
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6380"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

broker = RedisBroker(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD
)

dramatiq.set_broker(broker)

# 顯示連接資訊(隱藏密碼)
password_display = "***" if REDIS_PASSWORD else "無密碼"
print(f"✓ Redis Broker 已連接: {REDIS_HOST}:{REDIS_PORT}/{REDIS_DB} (密碼: {password_display})")
