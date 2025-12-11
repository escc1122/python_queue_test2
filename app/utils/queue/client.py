import threading
from typing import Optional, Tuple, Dict, Union
import redis
from app.config import settings
from .names import QueueName


class _RedisConnectionSingleton:
    """Redis 連線的單例模式實作，確保全域只有一個連線實例"""
    
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
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
    
    提供常用的 Redis 操作方法，每個實例綁定到特定的 key/list 名稱。
    """
    
    _instances: Dict[str, 'Queue'] = {}
    _instances_lock = threading.Lock()

    def __init__(self, name: Union[str, QueueName]):
        """
        初始化 Queue 實例
        
        Args:
            name: 佇列名稱，可以是 QueueName Enum 或字串
        """
        self._name = str(name)
        self._redis = _RedisConnectionSingleton().connection

    @classmethod
    def get(cls, name: Union[str, QueueName]) -> 'Queue':
        """
        取得或創建指定名稱的 Queue 實例（單例模式）
        同一個 name 只會創建一個實例，避免重複創建。
        
        Args:
            name: 佇列名稱，可以是 QueueName Enum 或字串
            
        Returns:
            Queue 實例
            
        Example:
            >>> from utils.queue import Queue, QueueName
            >>> queue = Queue.get(QueueName.HIGH_PRIORITY)
            >>> queue.push("task1")
        """
        key = str(name)
        if key not in cls._instances:
            with cls._instances_lock:
                if key not in cls._instances:
                    cls._instances[key] = cls(name)
        return cls._instances[key]

    def push(self, item: str) -> int:
        """
        將元素推入佇列尾部（RPUSH）
        
        Args:
            item: 要推入的元素
            
        Returns:
            推入後佇列的長度
        """
        return self._redis.rpush(self._name, item)

    def pop(self, timeout: Optional[int] = None) -> Optional[Tuple[str, str]]:
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

    def hash_set(self, key: str, value: str, expire_seconds: int = 0) -> int:
        """
        設定 hash 欄位值（HSET）
        
        Args:
            key: Hash 欄位名稱
            value: 欄位值
            expire_seconds: 過期秒數，0 表示不設定過期時間
            
        Returns:
            新增的欄位數量（0 或 1）
        """
        count = self._redis.hset(self._name, key, value)
        if expire_seconds > 0:
            self._redis.expire(self._name, expire_seconds)
        return count

    def set_value(self, value: str, expire_seconds: int = 0) -> bool:
        """
        設定字串值（SET）
        
        Args:
            value: 要設定的值
            expire_seconds: 過期秒數，0 表示不設定過期時間
            
        Returns:
            是否設定成功
        """
        return bool(self._redis.set(self._name, value, ex=expire_seconds))

    def get_value(self) -> Optional[str]:
        """
        取得字串值（GET）
        
        Returns:
            值，或 None（不存在）
        """
        return self._redis.get(self._name)