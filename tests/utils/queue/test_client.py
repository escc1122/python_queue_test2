"""
client.py 的單元測試

測試 Queue 和 RedisClient 類別的所有功能。
假設 Redis 服務已經在運行。

運行測試：
    pytest tests/test_client.py -v
"""

from __future__ import annotations
import pytest
import time
from app.utils.queue import Queue, RedisClient, QueueName


class TestQueue:
    """測試 Queue 類別"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """每個測試前後的設置和清理"""
        # 測試用的隊列名稱
        self.test_queue_name = "test_queue"
        self.test_queue_name_2 = "test_queue_2"

        yield

        # 清理測試數據
        try:
            queue1 = Queue.get(self.test_queue_name)
            queue1.clear()
        except Exception:
            pass

        try:
            queue2 = Queue.get(self.test_queue_name_2)
            queue2.clear()
        except Exception:
            pass

    def test_queue_singleton(self):
        """測試 Queue 單例模式"""
        queue1 = Queue.get(self.test_queue_name)
        queue2 = Queue.get(self.test_queue_name)

        # 同一個名稱應該返回同一個實例
        assert queue1 is queue2

    def test_queue_different_names(self):
        """測試不同名稱的 Queue 是不同的實例"""
        queue1 = Queue.get(self.test_queue_name)
        queue2 = Queue.get(self.test_queue_name_2)

        # 不同名稱應該返回不同實例
        assert queue1 is not queue2

    def test_queue_with_registered_name(self):
        """測試使用註冊的 QueueName 創建 Queue"""
        # 註冊一個測試佇列
        QueueName.register("TEST_QUEUE", "test_registered_queue")

        try:
            queue = Queue.get(QueueName.TEST_QUEUE)
            assert queue.name == "test_registered_queue"
        finally:
            # 清理
            QueueName.unregister("TEST_QUEUE")

    def test_queue_name_property(self):
        """測試 Queue.name 屬性"""
        queue = Queue.get(self.test_queue_name)

        assert queue.name == self.test_queue_name

    def test_push_and_length(self):
        """測試 push 和 length 方法"""
        queue = Queue.get(self.test_queue_name)

        # 初始長度應該為 0
        initial_length = queue.length()

        # 推入三個元素
        queue.push("item1")
        queue.push("item2")
        queue.push("item3")

        # 長度應該增加 3
        assert queue.length() == initial_length + 3

    def test_push_return_value(self):
        """測試 push 返回值（隊列長度）"""
        queue = Queue.get(self.test_queue_name)
        queue.clear()

        length1 = queue.push("item1")
        assert length1 == 1

        length2 = queue.push("item2")
        assert length2 == 2

        length3 = queue.push("item3")
        assert length3 == 3

    def test_pop(self):
        """測試 pop 方法（FIFO 順序）"""
        queue = Queue.get(self.test_queue_name)
        queue.clear()

        # 推入三個元素
        queue.push("first")
        queue.push("second")
        queue.push("third")

        # 彈出應該按 FIFO 順序
        result1 = queue.pop(timeout=1)
        assert result1 is not None
        assert result1[0] == self.test_queue_name
        assert result1[1] == "first"

        result2 = queue.pop(timeout=1)
        assert result2 is not None
        assert result2[1] == "second"

        result3 = queue.pop(timeout=1)
        assert result3 is not None
        assert result3[1] == "third"

    def test_pop_empty_queue_timeout(self):
        """測試從空隊列 pop 會超時"""
        queue = Queue.get(self.test_queue_name)
        queue.clear()

        # 從空隊列 pop 應該超時返回 None
        result = queue.pop(timeout=1)
        assert result is None

    def test_pop_with_default_timeout(self):
        """測試 pop 使用默認超時"""
        queue = Queue.get(self.test_queue_name)
        queue.clear()

        # 不指定 timeout 應該使用 settings.blpop_timeout
        result = queue.pop()  # 使用默認超時
        assert result is None

    def test_length_empty_queue(self):
        """測試空隊列的長度"""
        queue = Queue.get(self.test_queue_name)
        queue.clear()

        assert queue.length() == 0

    def test_clear(self):
        """測試 clear 方法"""
        queue = Queue.get(self.test_queue_name)

        # 推入一些元素
        queue.push("item1")
        queue.push("item2")
        queue.push("item3")

        assert queue.length() > 0

        # 清空隊列
        result = queue.clear()
        assert result is True
        assert queue.length() == 0

    def test_clear_empty_queue(self):
        """測試清空已經為空的隊列"""
        queue = Queue.get(self.test_queue_name)
        queue.clear()

        # 清空空隊列應該返回 False（因為沒有 key 被刪除）
        result = queue.clear()
        assert result is False

    def test_push_pop_multiple_items(self):
        """測試推入和彈出多個項目"""
        queue = Queue.get(self.test_queue_name)
        queue.clear()

        items = ["apple", "banana", "cherry", "date", "elderberry"]

        # 推入所有項目
        for item in items:
            queue.push(item)

        # 彈出並驗證順序
        for expected_item in items:
            result = queue.pop(timeout=1)
            assert result is not None
            assert result[1] == expected_item

        # 隊列應該為空
        assert queue.length() == 0


class TestRedisClient:
    """測試 RedisClient 類別"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """每個測試前後的設置和清理"""
        # 測試用的 key 名稱
        self.test_key = "test_key"
        self.test_key_2 = "test_key_2"
        self.test_hash_key = "test_hash"

        yield

        # 清理測試數據
        try:
            client1 = RedisClient.get(self.test_key)
            client1.delete()
        except Exception:
            pass

        try:
            client2 = RedisClient.get(self.test_key_2)
            client2.delete()
        except Exception:
            pass

        try:
            hash_client = RedisClient.get(self.test_hash_key)
            hash_client.delete()
        except Exception:
            pass

    def test_redis_client_singleton(self):
        """測試 RedisClient 單例模式"""
        client1 = RedisClient.get(self.test_key)
        client2 = RedisClient.get(self.test_key)

        # 同一個 key 應該返回同一個實例
        assert client1 is client2

    def test_redis_client_different_keys(self):
        """測試不同 key 的 RedisClient 是不同的實例"""
        client1 = RedisClient.get(self.test_key)
        client2 = RedisClient.get(self.test_key_2)

        # 不同 key 應該返回不同實例
        assert client1 is not client2

    def test_key_property(self):
        """測試 RedisClient.key 屬性"""
        client = RedisClient.get(self.test_key)

        assert client.key == self.test_key

    def test_set_and_get_value(self):
        """測試 set_value 和 get_value 方法"""
        client = RedisClient.get(self.test_key)

        # 設置值
        result = client.set_value("hello world")
        assert result is True

        # 獲取值
        value = client.get_value()
        assert value == "hello world"

    def test_set_value_with_expire(self):
        """測試設置值並帶有過期時間"""
        client = RedisClient.get(self.test_key)

        # 設置值，2 秒後過期
        result = client.set_value("temporary", expire_seconds=2)
        assert result is True

        # 立即讀取應該存在
        assert client.get_value() == "temporary"
        assert client.exists() is True

        # 等待 3 秒後應該過期
        time.sleep(3)
        assert client.get_value() is None
        assert client.exists() is False

    def test_get_value_nonexistent(self):
        """測試獲取不存在的值"""
        client = RedisClient.get(self.test_key)
        client.delete()

        value = client.get_value()
        assert value is None

    def test_hash_set_and_get(self):
        """測試 hash_set 和 hash_get 方法"""
        client = RedisClient.get(self.test_hash_key)

        # 設置 hash 字段
        result = client.hash_set("name", "Alice")
        assert result == 1  # 新增字段

        # 獲取 hash 字段
        value = client.hash_get("name")
        assert value == "Alice"

    def test_hash_set_update_existing(self):
        """測試更新已存在的 hash 字段"""
        client = RedisClient.get(self.test_hash_key)

        # 第一次設置
        result1 = client.hash_set("name", "Alice")
        assert result1 == 1  # 新增

        # 更新同一個字段
        result2 = client.hash_set("name", "Bob")
        assert result2 == 0  # 更新現有字段

    def test_hash_set_with_expire(self):
        """測試設置 hash 字段並帶有過期時間"""
        client = RedisClient.get(self.test_hash_key)

        # 設置 hash 字段，2 秒後過期
        client.hash_set("temp_field", "temp_value", expire_seconds=2)

        # 立即讀取應該存在
        assert client.hash_get("temp_field") == "temp_value"

        # 等待 3 秒後應該過期
        time.sleep(3)
        assert client.hash_get("temp_field") is None

    def test_hash_get_all(self):
        """測試 hash_get_all 方法"""
        client = RedisClient.get(self.test_hash_key)
        client.delete()

        # 設置多個 hash 字段
        client.hash_set("name", "Alice")
        client.hash_set("age", "30")
        client.hash_set("city", "Taipei")

        # 獲取所有字段
        all_fields = client.hash_get_all()
        assert all_fields == {
            "name": "Alice",
            "age": "30",
            "city": "Taipei"
        }

    def test_hash_get_all_empty(self):
        """測試獲取空 hash 的所有字段"""
        client = RedisClient.get(self.test_hash_key)
        client.delete()

        all_fields = client.hash_get_all()
        assert all_fields == {}

    def test_hash_get_nonexistent_field(self):
        """測試獲取不存在的 hash 字段"""
        client = RedisClient.get(self.test_hash_key)

        value = client.hash_get("nonexistent")
        assert value is None

    def test_delete(self):
        """測試 delete 方法"""
        client = RedisClient.get(self.test_key)

        # 設置一個值
        client.set_value("test value")
        assert client.exists() is True

        # 刪除
        result = client.delete()
        assert result is True
        assert client.exists() is False

    def test_delete_nonexistent(self):
        """測試刪除不存在的 key"""
        client = RedisClient.get(self.test_key)
        client.delete()  # 確保不存在

        # 刪除不存在的 key 應該返回 False
        result = client.delete()
        assert result is False

    def test_exists(self):
        """測試 exists 方法"""
        client = RedisClient.get(self.test_key)

        # 刪除後應該不存在
        client.delete()
        assert client.exists() is False

        # 設置值後應該存在
        client.set_value("test")
        assert client.exists() is True

    def test_expire(self):
        """測試 expire 方法"""
        client = RedisClient.get(self.test_key)

        # 設置一個值（不帶過期時間）
        client.set_value("test value")

        # 設置 2 秒後過期
        result = client.expire(2)
        assert result is True

        # 立即檢查應該還存在
        assert client.exists() is True

        # 等待 3 秒後應該過期
        time.sleep(3)
        assert client.exists() is False

    def test_expire_nonexistent_key(self):
        """測試對不存在的 key 設置過期時間"""
        client = RedisClient.get(self.test_key)
        client.delete()

        # 對不存在的 key 設置過期時間應該返回 False
        result = client.expire(10)
        assert result is False

    def test_multiple_operations(self):
        """測試多個操作的組合"""
        client = RedisClient.get(self.test_key)

        # 設置、獲取、更新、刪除的完整流程
        client.set_value("value1")
        assert client.get_value() == "value1"

        client.set_value("value2")
        assert client.get_value() == "value2"

        assert client.exists() is True

        client.delete()
        assert client.exists() is False
        assert client.get_value() is None


class TestRedisConnection:
    """測試 Redis 連接"""

    def test_redis_connection_is_alive(self):
        """測試 Redis 連接是否正常"""
        # 嘗試創建一個 Queue 並執行操作
        queue = Queue.get("connection_test")

        try:
            # 如果能成功獲取長度，說明連接正常
            length = queue.length()
            assert isinstance(length, int)
        finally:
            queue.clear()

    def test_redis_connection_shared(self):
        """測試所有實例共享同一個 Redis 連接"""
        queue1 = Queue.get("test1")
        queue2 = Queue.get("test2")
        client1 = RedisClient.get("key1")

        # 所有實例應該使用同一個 Redis 連接
        # 這個測試通過確保它們都能正常工作來間接驗證
        queue1.push("test")
        queue2.push("test")
        client1.set_value("test")

        assert queue1.length() >= 1
        assert queue2.length() >= 1
        assert client1.get_value() == "test"

        # 清理
        queue1.clear()
        queue2.clear()
        client1.delete()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
