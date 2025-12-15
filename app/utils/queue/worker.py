from __future__ import annotations
import threading
import time
from .client import Queue
from .names import QueueName
from .handlers import ItemHandler
from .exceptions import QueueError
from ..logging_config import setup_logging


class QueueWorker:
    """Redis 佇列消費者，支援多線程並行處理

    透過注入 ItemHandler 來處理從佇列彈出的項目。
    支援優雅關機機制（全域和實例級別）。

    使用範例：
        >>> from app.utils.queue import QueueWorker, QueueName
        >>> from app.utils.queue.handlers import EmailHandler
        >>>
        >>> worker = QueueWorker(
        ...     queue_name=QueueName.EMAIL,
        ...     pop_timeout=5,
        ...     handler=EmailHandler(),
        ...     num_threads=4
        ... )
        >>> worker.start()
        >>>
        >>> # 停止特定 worker
        >>> worker.stop()
        >>> worker.join()
        >>>
        >>> # 或停止所有 worker
        >>> QueueWorker.stop_all()
    """

    _global_stop_flag = threading.Event()
    """全域停止旗標，用於優雅關機。設定後所有 Worker 實例都會停止"""

    def __init__(
        self,
        queue_name: str | QueueName,
        pop_timeout: int,
        handler: ItemHandler,
        num_threads: int = 1,
        logger_name: str | None = None
    ) -> None:
        """
        初始化 QueueWorker

        Args:
            queue_name: 佇列名稱（QueueName Enum 或字串）
            pop_timeout: BLPOP 的超時秒數
            handler: 處理項目的 handler 實例
            num_threads: 並行處理的線程數量（預設 1）
            logger_name: 自定義 logger 名稱，預設為 "queue.worker.{queue_name}"
        """
        self._queue_name = str(queue_name)
        self._queue = Queue.get(queue_name)
        self._handler = handler
        self._pop_timeout = pop_timeout
        self._num_threads = max(1, num_threads)
        self._threads: list[threading.Thread] = []
        self._stop_flag = threading.Event()

        # 設定 logger
        logger_name = logger_name or f"queue.worker.{self._queue_name}"
        self._logger = setup_logging(logger_name)

    def _worker_loop(self, thread_id: int) -> None:
        """
        單一 worker 線程的執行邏輯

        Args:
            thread_id: 線程編號，用於日誌識別
        """
        self._logger.info(
            f"Worker thread {thread_id} started for queue '{self._queue_name}'"
        )

        while not self._should_stop():
            try:
                item = self._queue.pop(timeout=self._pop_timeout)
                if item is None:
                    # 超時，繼續循環以檢查停止旗標
                    continue

                queue_name, payload = item
                self._handler.handle_item(queue_name, payload)

            except QueueError as e:
                # 佇列相關錯誤，記錄並繼續處理下一個項目
                self._logger.error(
                    f"Worker thread {thread_id} queue error: {e}",
                    exc_info=True
                )
                time.sleep(2)

            except Exception as e:  # noqa: BLE001
                # 未預期的錯誤，記錄詳細資訊
                self._logger.exception(
                    f"Worker thread {thread_id} unexpected error: {e}"
                )
                time.sleep(2)  # 錯誤後稍作等待，避免快速失敗循環

        self._logger.info(
            f"Worker thread {thread_id} stopped for queue '{self._queue_name}'"
        )

    def _should_stop(self) -> bool:
        """
        檢查是否應該停止執行

        Returns:
            如果全域或實例停止旗標被設定，返回 True
        """
        return self._stop_flag.is_set() or QueueWorker._global_stop_flag.is_set()

    def start(self) -> None:
        """
        啟動所有 worker 線程（非阻塞）

        創建並啟動指定數量的線程，每個線程獨立從佇列消費任務。
        如果已經啟動過，會記錄警告並忽略。
        """
        if self._threads:
            self._logger.warning(
                f"Worker for queue '{self._queue_name}' is already running"
            )
            return

        self._logger.info(
            f"Starting {self._num_threads} worker thread(s) for queue '{self._queue_name}'"
        )

        for i in range(self._num_threads):
            thread = threading.Thread(
                target=self._worker_loop,
                args=(i,),
                name=f"QueueWorker-{self._queue_name}-{i}",
                daemon=False
            )
            thread.start()
            self._threads.append(thread)

    def stop(self) -> None:
        """
        停止此 worker 的所有線程（非阻塞）

        設定停止旗標，worker 線程將在當前任務完成後退出。
        使用 join() 方法等待所有線程完全停止。
        """
        if not self._threads:
            self._logger.warning(
                f"Worker for queue '{self._queue_name}' is not running"
            )
            return

        self._logger.info(
            f"Stopping worker for queue '{self._queue_name}'"
        )
        self._stop_flag.set()

    def join(self, timeout: float | None = None) -> bool:
        """
        等待所有 worker 線程結束

        Args:
            timeout: 最長等待秒數，None 表示無限等待

        Returns:
            是否所有線程都已結束（True 表示成功，False 表示超時）
        """
        if not self._threads:
            return True

        self._logger.info(
            f"Waiting for worker threads to finish for queue '{self._queue_name}'"
        )

        for thread in self._threads:
            thread.join(timeout=timeout)
            if thread.is_alive():
                self._logger.warning(
                    f"Thread {thread.name} did not finish within timeout"
                )
                return False

        self._threads.clear()
        self._logger.info(
            f"All worker threads stopped for queue '{self._queue_name}'"
        )
        return True

    def is_running(self) -> bool:
        """
        檢查 worker 是否正在執行

        Returns:
            是否有線程正在執行
        """
        return any(thread.is_alive() for thread in self._threads)

    @classmethod
    def stop_all(cls) -> None:
        """
        停止所有 QueueWorker 實例（全域停止）

        設定全域停止旗標，所有 worker 實例都會停止。
        這是優雅關機的推薦方式。
        """
        logger = setup_logging("queue.worker")
        logger.info("Setting global stop flag for all workers")
        cls._global_stop_flag.set()

    @classmethod
    def reset_global_stop_flag(cls) -> None:
        """
        重置全域停止旗標

        在停止所有 worker 後，如果需要重新啟動新的 worker，
        必須先調用此方法重置全域旗標。
        """
        logger = setup_logging("queue.worker")
        logger.info("Resetting global stop flag")
        cls._global_stop_flag.clear()