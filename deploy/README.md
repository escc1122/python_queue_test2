# 部署指南

## 環境配置檔案說明

| 檔案 | 用途 | 部署機器 | 啟動服務 |
|------|------|---------|---------|
| `.env.local` | 單機測試 | 開發機 | Redis + 所有 Consumers |
| `.env.redis` | Redis Server | 192.168.1.100 | Redis (Port 6380) |
| `.env.email` | Email Consumer | 192.168.1.101 | Email Consumer |
| `.env.data` | Data Consumer | 192.168.1.102 | Data Consumer |
| `.env.report` | Report Consumer | 192.168.1.103 | Report Consumer |

## 單機測試

```bash
# 1. 複製配置
cp deploy/envs/.env.local .env

# 2. 啟動所有服務
docker-compose up -d

# 3. 查看狀態
docker-compose ps

# 4. 執行 producer (測試)
docker run --rm \
  -e REDIS_HOST=localhost \
  -e REDIS_PORT=6380 \
  -e REDIS_PASSWORD=test_password_123 \
  dramatiq-ddd-app python app.py producer

# 5. 查看日誌
docker-compose logs -f consumer-email
tail -f logs/email/email.log

# 6. 停止
docker-compose down
```

## 多機部署

### 機器 1: Redis Server (192.168.1.100)

```bash
# 1. 複製配置
cp deploy/envs/.env.redis .env

# 2. 修改密碼(如需要)
nano .env

# 3. 啟動 Redis
docker-compose up -d

# 4. 驗證
docker exec -it dramatiq-redis redis-cli -a production_strong_password_456 ping
```

### 機器 2: Email Consumer (192.168.1.101)

```bash
# 1. 複製配置
cp deploy/envs/.env.email .env

# 2. 確認 Redis IP 和密碼
nano .env

# 3. 啟動 Consumer
docker-compose up -d

# 4. 查看日誌
docker-compose logs -f
tail -f logs/email/email.log
```

### 機器 3: Data Consumer (192.168.1.102)

```bash
cp deploy/envs/.env.data .env
docker-compose up -d
docker-compose logs -f
```

### 機器 4: Report Consumer (192.168.1.103)

```bash
cp deploy/envs/.env.report .env
docker-compose up -d
docker-compose logs -f
```

## Producer 執行

在任意可連接到 Redis 的機器:

```bash
docker run --rm \
  -e REDIS_HOST=192.168.1.100 \
  -e REDIS_PORT=6380 \
  -e REDIS_PASSWORD=production_strong_password_456 \
  dramatiq-ddd-app python app.py producer
```

## 監控命令

### 查看 Redis 狀態

```bash
# 連接 Redis
docker exec -it dramatiq-redis redis-cli -a production_strong_password_456

# 查看資訊
INFO

# 查看隊列長度
LLEN "dramatiq:email.welcome"
LLEN "dramatiq:data.process"

# 查看所有 key
KEYS "dramatiq:*"
```

### 查看服務狀態

```bash
# 查看運行狀態
docker-compose ps

# 查看日誌
docker-compose logs -f

# 查看資源使用
docker stats
```

## 防火牆配置 (Redis 機器)

```bash
# 只允許特定 IP 連接 6380
sudo ufw allow from 192.168.1.101 to any port 6380
sudo ufw allow from 192.168.1.102 to any port 6380
sudo ufw allow from 192.168.1.103 to any port 6380
sudo ufw deny 6380
```

## 密碼安全

⚠️ 生產環境請使用強密碼:

```bash
# 生成隨機密碼
openssl rand -base64 32
```

## 常見問題

### Q: Consumer 連不到 Redis?
A: 檢查:
1. Redis 機器的 6380 端口是否開放
2. `.env` 的 `REDIS_HOST` 是否正確
3. `REDIS_PASSWORD` 是否一致
4. 防火牆規則

### Q: 如何重啟服務?
```bash
docker-compose restart
```

### Q: 如何更新程式碼?
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

### Q: 如何擴展 Consumer?
```bash
# 啟動多個 Email Consumer
docker-compose up -d --scale consumer-email=3
```

### Q: 如何查看日誌?
```bash
# 容器日誌
docker-compose logs -f consumer-email

# 檔案日誌
tail -f logs/email/email.log
tail -f logs/email/email_error.log
```
