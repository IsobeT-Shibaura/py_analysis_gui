FROM python:3.12-slim

# タイムゾーンなど必要なら設定例:
# ENV TZ=Asia/Tokyo

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       tk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./

# コンテナ起動時に GUI アプリを実行
CMD ["python", "app.py"]
