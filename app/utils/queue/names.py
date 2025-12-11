from enum import Enum


class QueueName(str, Enum):
    """Redis 佇列名稱的統一定義"""
    
    HIGH_PRIORITY = "high_priority_tasks"
    LOW_PRIORITY = "low_priority_tasks"
    NOTIFICATIONS = "notifications"
    EMAIL = "email_queue"
    
    def __str__(self) -> str:
        """直接返回值，方便在 Redis 操作中使用"""
        return self.value