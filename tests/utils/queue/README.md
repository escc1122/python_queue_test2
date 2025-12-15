# Queue 模組測試

## 測試文件

- `test_client.py` - 測試 `client.py` 中的 Queue 和 RedisClient 類

## 快速開始

### 前置要求
確保 Redis 服務正在運行：
```bash
redis-cli ping
# 應該返回 PONG
```

### 運行所有 queue 測試
```bash
# 從專案根目錄運行
pytest tests/utils/queue/ -v
```

### 運行特定測試
```bash
# 只測試 Queue 類
pytest tests/utils/queue/test_client.py::TestQueue -v

# 只測試 RedisClient 類
pytest tests/utils/queue/test_client.py::TestRedisClient -v

# 運行單個測試方法
pytest tests/utils/queue/test_client.py::TestQueue::test_push_and_length -v
```

## test_client.py 測試覆蓋

### Queue 類測試（共 12 個測試）
✅ `test_queue_singleton` - 單例模式驗證
✅ `test_queue_different_names` - 不同名稱返回不同實例
✅ `test_queue_with_enum` - 使用 QueueName Enum
✅ `test_queue_name_property` - name 屬性
✅ `test_push_and_length` - push 和 length 方法
✅ `test_push_return_value` - push 返回值驗證
✅ `test_pop` - pop 方法和 FIFO 順序
✅ `test_pop_empty_queue_timeout` - 空隊列超時處理
✅ `test_pop_with_default_timeout` - 默認超時設置
✅ `test_length_empty_queue` - 空隊列長度
✅ `test_clear` - 清空隊列
✅ `test_clear_empty_queue` - 清空空隊列
✅ `test_push_pop_multiple_items` - 多項目操作

### RedisClient 類測試（共 16 個測試）
✅ `test_redis_client_singleton` - 單例模式驗證
✅ `test_redis_client_different_keys` - 不同 key 返回不同實例
✅ `test_key_property` - key 屬性
✅ `test_set_and_get_value` - 設置和獲取字符串值
✅ `test_set_value_with_expire` - 帶過期時間的設置
✅ `test_get_value_nonexistent` - 獲取不存在的值
✅ `test_hash_set_and_get` - Hash 設置和獲取
✅ `test_hash_set_update_existing` - 更新現有 Hash 字段
✅ `test_hash_set_with_expire` - Hash 帶過期時間
✅ `test_hash_get_all` - 獲取所有 Hash 字段
✅ `test_hash_get_all_empty` - 空 Hash 獲取
✅ `test_hash_get_nonexistent_field` - 獲取不存在的 Hash 字段
✅ `test_delete` - 刪除 key
✅ `test_delete_nonexistent` - 刪除不存在的 key
✅ `test_exists` - 檢查 key 是否存在
✅ `test_expire` - 設置過期時間
✅ `test_expire_nonexistent_key` - 對不存在的 key 設置過期
✅ `test_multiple_operations` - 組合操作

### Redis 連接測試（共 2 個測試）
✅ `test_redis_connection_is_alive` - 連接存活檢查
✅ `test_redis_connection_shared` - 連接共享驗證

**總計：30 個測試**

## 注意事項

1. **測試會自動清理數據**
   每個測試都會在結束後清理測試數據，不會影響其他測試

2. **需要真實的 Redis 連接**
   這些是整合測試，需要連接到真實的 Redis 服務

3. **測試數據庫**
   建議在 `.env` 中設置專門的測試數據庫：
   ```
   REDIS_DB=15  # 測試專用
   ```

4. **有些測試會 sleep**
   測試過期功能時會使用 `time.sleep()`，這些測試會比較慢

## 持續監控

使用 pytest-watch 自動運行測試：
```bash
# 安裝
pip install pytest-watch

# 監控並自動運行
ptw tests/utils/queue/
```
