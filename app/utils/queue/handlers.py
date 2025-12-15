from __future__ import annotations
from abc import ABC, abstractmethod
import logging
import json
from typing import Any
from .exceptions import InvalidPayloadError


class ItemHandler(ABC):
    """佇列項目處理器的抽象基類

    所有自定義的 handler 都必須繼承此類別並實作 handle_item 方法。
    """

    @abstractmethod
    def handle_item(self, queue_name: str, payload: str) -> None:
        """
        處理從佇列彈出的項目

        Args:
            queue_name: 佇列名稱
            payload: 項目內容（字串格式）

        Raises:
            Exception: 處理失敗時應該拋出異常，由 Worker 記錄錯誤
        """
        pass


class LoggingHandler(ItemHandler):
    """簡單的日誌 handler（用於測試或除錯）

    將接收到的項目記錄到日誌中。
    """

    def __init__(self):
        """初始化 LoggingHandler"""
        self._logger = logging.getLogger(f"{__name__}.LoggingHandler")

    def handle_item(self, queue_name: str, payload: str) -> None:
        """記錄接收到的項目"""
        self._logger.info(f"[{queue_name}] Received item: {payload}")


class JsonHandler(ItemHandler):
    """JSON 格式的 handler 基類

    自動將 payload 解析為 JSON，子類別只需實作 process_data 方法。
    """

    def __init__(self):
        """初始化 JsonHandler"""
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def handle_item(self, queue_name: str, payload: str) -> None:
        """處理 JSON 格式的項目"""
        try:
            data = json.loads(payload)
            self.process_data(queue_name, data)
        except json.JSONDecodeError as e:
            self._logger.error(f"Failed to parse JSON from queue '{queue_name}': {e}")
            self._logger.error(f"Raw payload: {payload}")
            raise InvalidPayloadError(f"Invalid JSON payload: {e}") from e

    @abstractmethod
    def process_data(self, queue_name: str, data: dict[str, Any]) -> None:
        """
        處理解析後的 JSON 資料

        Args:
            queue_name: 佇列名稱
            data: 解析後的 JSON 資料
        """
        pass


# ===== 範例實作 =====

class EmailHandler(JsonHandler):
    """電子郵件發送 handler（範例）

    預期的 JSON 格式：
    {
        "to": "user@example.com",
        "subject": "標題",
        "body": "內容"
    }
    """

    def process_data(self, queue_name: str, data: dict[str, Any]) -> None:
        """處理郵件發送任務"""
        to_email = data.get("to")
        subject = data.get("subject")
        body = data.get("body")

        if not all([to_email, subject, body]):
            raise InvalidPayloadError("Missing required fields: to, subject, or body")

        # 這裡實作實際的郵件發送邏輯
        self._logger.info(f"Sending email to {to_email}")
        self._logger.info(f"Subject: {subject}")
        self._logger.info(f"Body: {body[:50]}...")  # 只顯示前 50 字元

        # TODO: 實際的郵件發送邏輯
        # send_email(to_email, subject, body)


class NotificationHandler(JsonHandler):
    """通知發送 handler（範例）

    預期的 JSON 格式：
    {
        "user_id": 123,
        "message": "通知內容",
        "type": "info|warning|error"
    }
    """

    def process_data(self, queue_name: str, data: dict[str, Any]) -> None:
        """處理通知發送任務"""
        user_id = data.get("user_id")
        message = data.get("message")
        notification_type = data.get("type", "info")

        if not all([user_id, message]):
            raise InvalidPayloadError("Missing required fields: user_id or message")

        self._logger.info(f"Sending {notification_type} notification to user {user_id}")
        self._logger.info(f"Message: {message}")

        # TODO: 實際的通知發送邏輯
        # send_notification(user_id, message, notification_type)


class TaskProcessHandler(JsonHandler):
    """任務處理 handler（範例）

    預期的 JSON 格式：
    {
        "task_id": "uuid",
        "task_type": "process_image|generate_report|...",
        "params": {...}
    }
    """

    def process_data(self, queue_name: str, data: dict[str, Any]) -> None:
        """處理任務"""
        task_id = data.get("task_id")
        task_type = data.get("task_type")
        params = data.get("params", {})

        if not all([task_id, task_type]):
            raise InvalidPayloadError("Missing required fields: task_id or task_type")

        self._logger.info(f"Processing task {task_id} (type: {task_type})")

        # 根據任務類型執行不同的處理邏輯
        if task_type == "process_image":
            self._process_image(task_id, params)
        elif task_type == "generate_report":
            self._generate_report(task_id, params)
        else:
            raise InvalidPayloadError(f"Unknown task type: {task_type}")

    def _process_image(self, task_id: str, params: dict[str, Any]) -> None:
        """處理圖片任務"""
        self._logger.info(f"Processing image for task {task_id}")
        # TODO: 實作圖片處理邏輯

    def _generate_report(self, task_id: str, params: dict[str, Any]) -> None:
        """生成報告任務"""
        self._logger.info(f"Generating report for task {task_id}")
        # TODO: 實作報告生成邏輯