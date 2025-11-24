FROM python:3.11-slim

# wxPython が依存する GTK3 等をインストール
RUN apt-get update \
     && apt-get install -y --no-install-recommends \
         curl libgtk-3-0 libgtk-3-dev libjpeg-dev libtiff-dev libpng-dev \
         libgstreamer1.0-0 libgstreamer-plugins-base1.0-0 libwebkit2gtk-4.0-37 tk \
     && rm -rf /var/lib/apt/lists/* \
     && curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:${PATH}" 
ENV UV_PREFER_BINARY=1

WORKDIR /app
COPY pyproject.toml ./
# uv.lock は生成後にコピー (初回は存在しない可能性あり)
COPY uv.lock* ./
RUN uv sync --frozen --no-dev || uv sync --no-dev 

COPY app.py wx_app.py ./

CMD ["uv", "run", "wx_app.py"]
