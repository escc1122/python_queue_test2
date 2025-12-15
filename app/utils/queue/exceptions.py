"""Redis Queue 自定義異常

定義模組專用的異常類別，用於更精確的錯誤處理。
"""

from __future__ import annotations


class QueueError(Exception):
    """Redis Queue 模組的基礎異常類別"""
    pass


class QueueConnectionError(QueueError):
    """Redis 連線錯誤"""
    pass


class QueueOperationError(QueueError):
    """佇列操作錯誤"""
    pass


class HandlerError(QueueError):
    """Handler 處理錯誤"""
    pass


class InvalidPayloadError(HandlerError):
    """無效的 payload 格式"""
    pass
