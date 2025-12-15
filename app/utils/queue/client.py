from __future__ import annotations
import threading
from typing import Dict
import redis
from .config import settings
from .names import QueueName


class _RedisConnectionSingleton:
    """Redis 連線的單例模式實作，確保全域只有一個連線實例"""

    _instance: _RedisConnectionSingleton | None = None
    _lock = threading.Lock()

    def __new__(cls) -> _RedisConnectionSingleton:
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """初始化 Redis 連線"""
        self._conn = redis.StrictRedis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True,
        )

    @property
    def connection(self) -> redis.StrictRedis:
        """取得 Redis 連線實例"""
        return self._conn


class Queue:
    """Redis 佇列操作的便利包裝類別

    提供 FIFO 佇列的基本操作（push、pop、length）。
    每個實例綁定到特定的 Redis List key。

    使用單例模式確保相同名稱的佇列只有一個實例。
    """

    _instances: Dict[str, Queue] = {}
    _instances_lock = threading.Lock()

    def __init__(self, name: str | QueueName):
        """
        初始化 Queue 實例

        Args:
            name: 佇列名稱，可以是 QueueName Enum 或字串
        """
        self._name = str(name)
        self._redis = _RedisConnectionSingleton().connection

    @classmethod
    def get(cls, name: str | QueueName) -> Queue:
        """
        取得或創建指定名稱的 Queue 實例（單例模式）

        同一個 name 只會創建一個實例，避免重複創建。

        Args:
            name: 佇列名稱，可以是 QueueName Enum 或字串

        Returns:
            Queue 實例

        Example:
            >>> from app.utils.queue import Queue, QueueName
            >>> queue = Queue.get(QueueName.HIGH_PRIORITY)
            >>> queue.push("task1")
        """
        key = str(name)
        if key not in cls._instances:
            with cls._instances_lock:
                if key not in cls._instances:
                    cls._instances[key] = cls(name)
        return cls._instances[key]

    @property
    def name(self) -> str:
        """取得佇列名稱"""
        return self._name

    def push(self, item: str) -> int:
        """
        將元素推入佇列尾部（RPUSH）

        Args:
            item: 要推入的元素（字串格式）

        Returns:
            推入後佇列的長度
        """
        return self._redis.rpush(self._name, item)

    def pop(self, timeout: int | None = None) -> tuple[str, str] | None:
        """
        從佇列頭部彈出元素（BLPOP，阻塞式）

        Args:
            timeout: 等待秒數，None 則使用 settings.blpop_timeout

        Returns:
            (佇列名稱, 元素值) 的 tuple，或 None（逾時）
        """
        wait_time = settings.blpop_timeout if timeout is None else timeout
        return self._redis.blpop(self._name, timeout=wait_time)

    def length(self) -> int:
        """
        取得佇列長度（LLEN）

        Returns:
            佇列中的元素數量
        """
        return self._redis.llen(self._name)

    def clear(self) -> bool:
        """
        清空佇列中的所有元素

        Returns:
            是否成功刪除
        """
        return bool(self._redis.delete(self._name))


class RedisClient:
    """Redis 通用操作客戶端

    提供 Redis 的通用數據結構操作（String、Hash 等）。
    每個實例綁定到特定的 Redis key。
    """

    _instances: Dict[str, RedisClient] = {}
    _instances_lock = threading.Lock()

    def __init__(self, key: str):
        """
        初始化 RedisClient 實例

        Args:
            key: Redis key 名稱
        """
        self._key = key
        self._redis = _RedisConnectionSingleton().connection

    @classmethod
    def get(cls, key: str) -> RedisClient:
        """
        取得或創建指定 key 的 RedisClient 實例（單例模式）

        Args:
            key: Redis key 名稱

        Returns:
            RedisClient 實例
        """
        if key not in cls._instances:
            with cls._instances_lock:
                if key not in cls._instances:
                    cls._instances[key] = cls(key)
        return cls._instances[key]

    @property
    def key(self) -> str:
        """取得當前 key 名稱"""
        return self._key

    def set_value(self, value: str, expire_seconds: int = 0) -> bool:
        """
        設定字串值（SET）

        Args:
            value: 要設定的值
            expire_seconds: 過期秒數，0 表示不設定過期時間

        Returns:
            是否設定成功
        """
        if expire_seconds > 0:
            return bool(self._redis.set(self._key, value, ex=expire_seconds))
        return bool(self._redis.set(self._key, value))

    def get_value(self) -> str | None:
        """
        取得字串值（GET）

        Returns:
            值，或 None（不存在）
        """
        return self._redis.get(self._key)

    def hash_set(self, field: str, value: str, expire_seconds: int = 0) -> int:
        """
        設定 hash 欄位值（HSET）

        Args:
            field: Hash 欄位名稱
            value: 欄位值
            expire_seconds: 過期秒數，0 表示不設定過期時間

        Returns:
            新增的欄位數量（0 表示更新現有欄位，1 表示新增欄位）
        """
        count = self._redis.hset(self._key, field, value)
        if expire_seconds > 0:
            self._redis.expire(self._key, expire_seconds)
        return count

    def hash_get(self, field: str) -> str | None:
        """
        取得 hash 欄位值（HGET）

        Args:
            field: Hash 欄位名稱

        Returns:
            欄位值，或 None（不存在）
        """
        return self._redis.hget(self._key, field)

    def hash_get_all(self) -> dict[str, str]:
        """
        取得所有 hash 欄位值（HGETALL）

        Returns:
            所有欄位的字典
        """
        return self._redis.hgetall(self._key)

    def delete(self) -> bool:
        """
        刪除 key

        Returns:
            是否成功刪除
        """
        return bool(self._redis.delete(self._key))

    def exists(self) -> bool:
        """
        檢查 key 是否存在

        Returns:
            是否存在
        """
        return bool(self._redis.exists(self._key))

    def expire(self, seconds: int) -> bool:
        """
        設定 key 的過期時間

        Args:
            seconds: 過期秒數

        Returns:
            是否設定成功
        """
        return bool(self._redis.expire(self._key, seconds))