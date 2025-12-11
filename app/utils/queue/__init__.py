"""Redis Queue 模組

提供 Redis 佇列操作和消費者功能。

主要元件：
- QueueName: 佇列名稱的統一定義（Enum）
- Queue: Redis 佇列操作類別
- QueueWorker: Redis 佇列消費者類別
- ItemHandler: 項目處理器抽象基類

使用範例：
    >>> from utils.queue import QueueName, Queue, QueueWorker
    >>> from utils.queue.handlers import EmailHandler
    >>>
    >>> # 取得佇列並推入任務
    >>> queue = Queue.get(QueueName.EMAIL)
    >>> queue.push(json.dumps({
    ...     "to": "user@example.com",
    ...     "subject": "Hello",
    ...     "body": "Welcome!"
    ... }))
    >>>
    >>> # 啟動 worker 消費任務
    >>> worker = QueueWorker(
    ...     queue_name=QueueName.EMAIL,
    ...     pop_timeout=5,
    ...     handler=EmailHandler(),
    ...     num_threads=4
    ... )
    >>> worker.start()
    >>>
    >>> # 優雅關機
    >>> QueueWorker.stop_flag.set()
"""

from .names import QueueName
from .client import Queue
from .worker import QueueWorker
from .handlers import ItemHandler

__all__ = [
    'QueueName',
    'Queue',
    'QueueWorker',
    'ItemHandler',
]