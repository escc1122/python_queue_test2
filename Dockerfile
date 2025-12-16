FROM python:3.14-slim

WORKDIR /app

# 安裝 pipenv
RUN pip install --no-cache-dir pipenv

# 複製 Pipfile 和 Pipfile.lock
COPY Pipfile Pipfile.lock ./

# 安裝依賴 (使用 Pipfile.lock,安裝到系統)
RUN pipenv install --system --deploy --ignore-pipfile

# 複製應用程式
COPY . .

# 預設執行 consumer
CMD ["python", "app.py", "consumer", "email"]
