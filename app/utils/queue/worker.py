from __future__ import annotations
import logging
import threading
import time
from typing import List, Union
from .client import Queue
from .names import QueueName
from .handlers import ItemHandler


class QueueWorker:
    """Redis 佇列消費者，支援多線程並行處理
    
    透過注入 ItemHandler 來處理從佇列彈出的項目。
    支援優雅關機機制。
    """
    
    stop_flag = threading.Event()
    """全域停止旗標，用於優雅關機。設定後所有 Worker 實例都會停止"""

    def __init__(
        self, 
        queue_name: Union[str, QueueName], 
        pop_timeout: int, 
        handler: ItemHandler,
        num_threads: int = 1
    ) -> None:
        """
        初始化 QueueWorker
        
        Args:
            queue_name: 佇列名稱（QueueName Enum 或字串）
            pop_timeout: BLPOP 的超時秒數
            handler: 處理項目的 handler 實例
            num_threads: 並行處理的線程數量（預設 1）
        """
        self._queue_name = str(queue_name)
        self._queue = Queue.get(queue_name)
        self._handler = handler
        self._pop_timeout = pop_timeout
        self._num_threads = max(1, num_threads)
        self._threads: List[threading.Thread] = []

    def _worker_loop(self, thread_id: int) -> None:
        """
        單一 worker 線程的執行邏輯
        
        Args:
            thread_id: 線程編號，用於日誌識別
        """
        logging.info(
            f"Worker thread {thread_id} started for queue '{self._queue_name}'"
        )
        
        while not QueueWorker.stop_flag.is_set():
            try:
                item = self._queue.pop(timeout=self._pop_timeout)
                if item is None:
                    # 超時，繼續循環以檢查 stop_flag
                    continue
                
                queue_name, payload = item
                self._handler.handle_item(queue_name, payload)
                
            except Exception as e:  # noqa: BLE001
                logging.exception(
                    f"Worker thread {thread_id} error while processing task: %s", e
                )
                time.sleep(2)  # 錯誤後稍作等待，避免快速失敗循環
        
        logging.info(
            f"Worker thread {thread_id} stopped for queue '{self._queue_name}'"
        )

    def start(self) -> None:
        """
        啟動所有 worker 線程（非阻塞）
        
        創建並啟動指定數量的線程，每個線程獨立從佇列消費任務。
        如果已經啟動過，會記錄警告並忽略。
        """
        if self._threads:
            logging.warning(
                f"Worker for queue '{self._queue_name}' is already running"
            )
            return
        
        logging.info(
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