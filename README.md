# Dramatiq Producer-Consumer 範例

這是一個使用 Dramatiq 實作的 Producer-Consumer 模式範例。

## 專案結構

```
dramatiq_project/
├── broker.py          # Redis broker 配置
├── jobs/              # 任務定義
│   ├── __init__.py
│   └── email.py       # 郵件相關任務
├── producer.py        # 生產者 - 發送任務
├── consumer.py        # 消費者 - 處理任務
└── README.md
```

## 安裝依賴

```bash
pip install dramatiq[redis]
```

## 使用方式

### 1. 確保 Redis 正在運行

```bash
redis-server
```

### 2. 啟動 Consumer (終端 1)

```bash
python consumer.py
```

輸出:
```
=== Consumer: 啟動任務處理器 ===

Worker-1 已啟動,等待任務...
Worker-2 已啟動,等待任務...
已啟動 2 個 workers
按 Ctrl+C 停止
```

### 3. 執行 Producer 發送任務 (終端 2)

```bash
python producer.py
```

輸出:
```
=== Producer: 發送任務到隊列 ===

發送任務...

✓ 所有任務已發送到隊列!
請確保 consumer.py 正在運行
```

### 4. 觀察 Consumer 處理任務

Consumer 終端會顯示:
```
發送歡迎郵件給 user1@example.com
[Worker-1] ✓ 歡迎郵件已發送給用戶 1
通知用戶 3: 你有新訊息
[Worker-2] ✓ 通知已發送
...
```

## 添加新任務

### 1. 在 jobs 目錄創建新模塊

例如 `jobs/payment.py`:

```python
import dramatiq

@dramatiq.actor
def process_payment(order_id: int, amount: float):
    print(f"處理付款: 訂單 {order_id}, 金額 ${amount}")
    return f"付款成功"
```

### 2. 在 jobs/__init__.py 導出

```python
from .email import send_welcome_email, send_notification
from .payment import process_payment

__all__ = [
    'send_welcome_email',
    'send_notification',
    'process_payment',
]
```

### 3. 在 consumer.py 導入模塊

```python
import jobs.email
import jobs.payment  # 新增
```

### 4. 在 producer.py 使用

```python
from jobs import process_payment

process_payment.send(1001, 99.99)
```

## 配置說明

### 修改 Worker 數量

在 `consumer.py` 中:

```python
num_workers = 4  # 改成你想要的數量
```

### 修改 Redis 連接

在 `broker.py` 中:

```python
broker = RedisBroker(
    host="localhost",
    port=6379,
    db=0,  # 可指定 Redis database
)
```

### 任務配置選項

```python
@dramatiq.actor(
    max_retries=3,        # 最大重試次數
    time_limit=60000,     # 超時時間 (毫秒)
    queue_name="default"  # 隊列名稱
)
def my_task():
    pass
```

## 注意事項

- 確保 Redis 在運行
- Consumer 必須先啟動,才能處理 Producer 發送的任務
- 按 Ctrl+C 停止 Consumer
- 任務會持久化在 Redis 中,即使 Consumer 停止也不會丟失

## 進階功能

### 延遲執行

```python
send_email.send_with_options(
    args=(1, "user@example.com"),
    delay=5000  # 延遲 5 秒
)
```

### 優先級隊列

```python
@dramatiq.actor(queue_name="high_priority")
def urgent_task():
    pass

@dramatiq.actor(queue_name="low_priority")
def background_task():
    pass
```

然後啟動不同的 consumer 處理不同隊列。
