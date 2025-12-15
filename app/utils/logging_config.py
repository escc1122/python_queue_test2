"""Redis Queue 日誌配置

提供統一的日誌配置功能。
"""

from __future__ import annotations
import logging
import sys


def setup_logging(
    name: str = "queue",
    level: str | None = None,
    format_string: str | None = None,
) -> logging.Logger:
    """
    設定並返回配置好的 logger

    Args:
        name: Logger 名稱，預設為 "queue"
        level: 日誌級別，預設使用 settings.log_level
        format_string: 日誌格式字串，預設使用標準格式

    Returns:
        配置好的 Logger 實例

    Example:
        >>> logger = setup_logging("my_worker")
        >>> logger.info("Worker started")
    """
    logger = logging.getLogger(name)

    # 避免重複添加 handler
    if logger.handlers:
        return logger

    # 設定日誌級別
    logger.setLevel(logging.INFO)

    # 創建 console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logger.level)

    # 設定格式
    default_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "[%(filename)s:%(lineno)d] - %(message)s"
    )
    formatter = logging.Formatter(format_string or default_format)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    # 防止日誌向上傳播（避免重複輸出）
    logger.propagate = False

    return logger
