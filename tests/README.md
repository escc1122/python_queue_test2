# 測試說明

## 前置要求

1. **Redis 服務必須運行**
   ```bash
   # 檢查 Redis 是否運行
   redis-cli ping
   # 應該返回 PONG
   ```

2. **安裝測試依賴**
   ```bash
   # 如果使用 pipenv
   pipenv install pytest --dev

   # 或使用 pip
   pip install pytest
   ```

## 運行測試

### 運行所有測試
```bash
# 使用 pytest
pytest

# 或使用 pipenv
pipenv run pytest

# 詳細輸出
pytest -v

# 顯示測試覆蓋率（需要安裝 pytest-cov）
pytest --cov=app.utils.queue --cov-report=html
```

### 運行特定測試文件
```bash
# 只測試 client.py
pytest tests/utils/queue/test_client.py -v
```

### 運行特定測試類
```bash
# 只測試 Queue 類
pytest tests/utils/queue/test_client.py::TestQueue -v

# 只測試 RedisClient 類
pytest tests/utils/queue/test_client.py::TestRedisClient -v
```

### 運行特定測試方法
```bash
# 測試單例模式
pytest tests/utils/queue/test_client.py::TestQueue::test_queue_singleton -v

# 測試 push 和 pop
pytest tests/utils/queue/test_client.py::TestQueue::test_push_and_length -v
```

## 測試覆蓋範圍

### TestQueue 類
測試 Queue 類的所有功能：
- ✅ 單例模式
- ✅ 使用 QueueName Enum
- ✅ push() 方法
- ✅ pop() 方法（含超時）
- ✅ length() 方法
- ✅ clear() 方法
- ✅ FIFO 順序驗證
- ✅ name 屬性

### TestRedisClient 類
測試 RedisClient 類的所有功能：
- ✅ 單例模式
- ✅ set_value() / get_value() 方法
- ✅ 過期時間設置
- ✅ hash_set() / hash_get() 方法
- ✅ hash_get_all() 方法
- ✅ delete() 方法
- ✅ exists() 方法
- ✅ expire() 方法
- ✅ key 屬性

### TestRedisConnection 類
測試 Redis 連接：
- ✅ 連接是否正常
- ✅ 連接是否共享

## 測試數據清理

所有測試都使用 `@pytest.fixture(autouse=True)` 自動清理測試數據，確保：
- 每個測試開始時有乾淨的環境
- 測試結束後清理所有測試數據
- 不會影響其他測試或生產數據

## 故障排除

### Redis 連接失敗
```
ConnectionError: Error connecting to Redis
```
**解決方案**：
1. 確認 Redis 服務正在運行：`redis-cli ping`
2. 檢查 `.env` 文件中的 Redis 配置
3. 確認 Redis 端口和主機設置正確

### 測試超時
如果測試運行很慢，可能是：
1. Redis 服務響應緩慢
2. 網絡延遲
3. 可以調整測試中的 `timeout` 參數

### 清理測試數據
如果需要手動清理測試數據：
```bash
# 連接到 Redis
redis-cli

# 刪除測試相關的 key
DEL test_queue test_queue_2 test_key test_key_2 test_hash

# 或清空整個數據庫（謹慎使用！）
FLUSHDB
```

## 持續整合

可以將測試加入 CI/CD 流程：

```yaml
# GitHub Actions 範例
- name: Run tests
  run: |
    pytest tests/ -v --cov=app.utils.queue
```

## 建議

1. **開發時使用專用的 Redis 數據庫**
   - 在 `.env` 中設置 `REDIS_DB=15`（測試用）
   - 生產環境使用 `REDIS_DB=0`

2. **定期運行測試**
   ```bash
   # 監視文件變化並自動運行測試
   pipenv install pytest-watch --dev
   pipenv run ptw
   ```

3. **測試覆蓋率目標**
   - 目標：>=90% 代碼覆蓋率
   - 安裝：`pipenv install pytest-cov --dev`
   - 運行：`pytest --cov=app.utils.queue --cov-report=term-missing`
