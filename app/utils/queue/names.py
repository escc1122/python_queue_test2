from __future__ import annotations


class QueueName:
    """Redis 佇列名稱註冊管理

    提供動態註冊佇列名稱的功能，讓使用者可以用常量方式引用佇列。

    使用範例：
        >>> # 註冊佇列
        >>> QueueName.register("EMAIL", "email_queue")
        >>> QueueName.register("USER_TASKS", "user_tasks_queue")
        >>>
        >>> # 使用註冊的佇列
        >>> queue = Queue.get(QueueName.EMAIL)
        >>>
        >>> # 或直接使用字串
        >>> queue = Queue.get("my_custom_queue")
    """

    # 儲存註冊的佇列名稱
    _queues: dict[str, str] = {}

    @classmethod
    def register(cls, name: str, value: str) -> None:
        """
        註冊佇列名稱

        Args:
            name: 佇列名稱常量（建議大寫，用於程式碼中引用）
            value: Redis 中實際的佇列名稱

        Raises:
            ValueError: 如果名稱已存在

        Example:
            >>> QueueName.register("EMAIL", "email_queue")
            >>> QueueName.register("USER_TASKS", "user_tasks_queue")
            >>> queue = Queue.get(QueueName.EMAIL)
        """
        # 檢查是否已註冊
        if name in cls._queues:
            raise ValueError(
                f"Queue name '{name}' is already registered with value '{cls._queues[name]}'."
            )

        # 註冊佇列
        cls._queues[name] = value

        # 動態添加為類屬性，方便使用
        setattr(cls, name, value)

    @classmethod
    def unregister(cls, name: str) -> None:
        """
        取消註冊佇列名稱

        Args:
            name: 要取消註冊的佇列名稱

        Raises:
            ValueError: 如果佇列不存在

        Example:
            >>> QueueName.unregister("USER_TASKS")
        """
        # 檢查是否存在
        if name not in cls._queues:
            raise ValueError(f"Queue name '{name}' is not registered.")

        # 從字典中移除
        del cls._queues[name]

        # 移除類屬性
        if hasattr(cls, name):
            delattr(cls, name)

    @classmethod
    def get(cls, name: str) -> str | None:
        """
        取得註冊的佇列值

        Args:
            name: 佇列名稱

        Returns:
            佇列值，如果不存在返回 None

        Example:
            >>> QueueName.register("EMAIL", "email_queue")
            >>> QueueName.get("EMAIL")
            'email_queue'
        """
        return cls._queues.get(name)

    @classmethod
    def list_all(cls) -> dict[str, str]:
        """
        列出所有已註冊的佇列名稱

        Returns:
            包含所有佇列名稱和值的字典

        Example:
            >>> QueueName.register("EMAIL", "email_queue")
            >>> QueueName.list_all()
            {'EMAIL': 'email_queue'}
        """
        return cls._queues.copy()

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """
        檢查佇列名稱是否已註冊

        Args:
            name: 要檢查的佇列名稱

        Returns:
            如果已註冊返回 True，否則返回 False

        Example:
            >>> QueueName.register("EMAIL", "email_queue")
            >>> QueueName.is_registered("EMAIL")
            True
            >>> QueueName.is_registered("UNKNOWN")
            False
        """
        return name in cls._queues

    @classmethod
    def clear(cls) -> None:
        """
        清除所有已註冊的佇列（主要用於測試）

        Example:
            >>> QueueName.clear()
        """
        # 移除所有動態屬性
        for name in list(cls._queues.keys()):
            if hasattr(cls, name):
                delattr(cls, name)

        # 清空字典
        cls._queues.clear()