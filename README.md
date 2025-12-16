# Dramatiq DDD Producer-Consumer 專案

基於 DDD (Domain-Driven Design) 架構的分散式任務隊列系統。

## 專案結構

```
project/
├── deploy/
│   ├── envs/              # 環境配置集中管理
│   │   ├── .env.local    # 單機測試
│   │   ├── .env.redis    # Redis 機器
│   │   ├── .env.email    # Email Context
│   │   ├── .env.data     # Data Context
│   │   └── .env.report   # Report Context
│   └── README.md
│
├── contexts/              # 按業務領域劃分
│   ├── email/
│   │   ├── jobs.py       # Email 相關任務
│   │   ├── consumer.py   # Email Consumer
│   │   └── services.py   # Email 業務邏輯 (可選)
│   ├── data/
│   └── report/
│
├── shared/                # 共享內核
│   ├── broker.py         # Redis broker 配置
│   ├── queues.py         # Queue Names 集中管理
│   └── logger.py         # 日誌配置
│
├── logs/                  # 日誌目錄 (自動生成)
│
├── docker-compose.yml     # Docker Compose 配置
├── Dockerfile
├── app.py                # 統一入口
├── Pipfile
└── README.md
```

## 關鍵設計

### DDD 架構
- **按 Context 劃分** - Email, Data, Report 三個獨立的業務領域
- **高內聚低耦合** - 每個 Context 包含自己的 jobs, consumer, services
- **通過 Queue 通信** - Context 之間透過 Message Queue 解耦

### 技術棧
- **Pipenv** - Python 依賴管理
- **Dramatiq** - 分散式任務隊列
- **Redis** - Message Broker (Port: 6380, 密碼保護)
- **Docker Compose** - 容器編排 (用 profiles 控制)

### 部署架構
- **機器 1**: Redis Server (Port 6380)
- **機器 2**: Email Context Consumer
- **機器 3**: Data Context Consumer  
- **機器 4**: Report Context Consumer
- **其他**: Producer (可在任意機器執行)

### Queue 管理
- 集中定義在 `shared/queues.py`
- `QueueNames` - 所有 Queue 名稱
- `ContextQueues` - 每個 Context 監聽的隊列
- Context 之間可共用 Queue (如 notification, log)

### 日誌系統
- 從環境變數 `CONTEXT_NAME` 讀取
- Volume 掛載到宿主機 `./logs/{context}/`
- 自動輪轉 (10MB per file, 5 backups)
- 分離 error log

## 快速開始

### 安裝依賴

```bash
pipenv install
```

### 單機測試

```bash
# 1. 複製配置
cp deploy/envs/.env.local .env

# 2. 啟動所有服務
docker-compose up -d

# 3. 查看狀態
docker-compose ps

# 4. 查看日誌
docker-compose logs -f consumer-email
tail -f logs/email/email.log

# 5. 執行 producer (測試)
docker run --rm \
  -e REDIS_HOST=127.0.0.1 \
  -e REDIS_PORT=6380 \
  -e REDIS_PASSWORD=test_password_123 \
  dramatiq-app python app.py producer

# 6. 停止
docker-compose down
```

### 多機部署

詳見 `deploy/README.md`

## 環境變數

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `COMPOSE_PROFILES` | 啟動的服務 | - |
| `CONTEXT_NAME` | Context 名稱 (email/data/report) | app |
| `LOG_DIR` | 日誌目錄 | ./logs |
| `REDIS_HOST` | Redis 主機 | localhost |
| `REDIS_PORT` | Redis 端口 | 6380 |
| `REDIS_DB` | Redis 資料庫 | 0 |
| `REDIS_PASSWORD` | Redis 密碼 | - |
| `REDIS_EXPOSE` | Redis 暴露位址 | 0.0.0.0 |

## 監控

### 查看 Redis 狀態

```bash
docker exec -it dramatiq-redis redis-cli -a your_password

# 查看隊列長度
LLEN "dramatiq:email.welcome"

# 查看所有 key
KEYS "dramatiq:*"
```

### 查看日誌

```bash
# 容器日誌
docker-compose logs -f consumer-email

# 檔案日誌
tail -f logs/email/email.log
tail -f logs/email/email_error.log
```

## 開發指南

### 新增 Context

1. 在 `contexts/` 建立新目錄
2. 新增 `jobs.py`, `consumer.py`
3. 在 `shared/queues.py` 定義 Queue Names
4. 在 `app.py` 註冊 Consumer
5. 在 `docker-compose.yml` 新增服務
6. 建立對應的 `.env` 配置

### 新增任務

1. 在對應 Context 的 `jobs.py` 新增 `@dramatiq.actor`
2. 在 `shared/queues.py` 定義 Queue Name
3. 在其他地方呼叫 `task_name.send(args)`

## 安全建議

- 使用強密碼: `openssl rand -base64 32`
- 配置防火牆規則限制 6380 端口訪問
- 生產環境使用 TLS/SSL (Redis 6+)
- 定期備份 Redis 資料

## License

MIT
