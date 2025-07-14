# マルチステージビルドで最適化
FROM python:3.10-slim as builder

# ビルド依存関係のインストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libopencv-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 本番イメージ
FROM python:3.10-slim

# 非rootユーザーの作成
RUN groupadd -r appuser && useradd -r -g appuser appuser

# システム依存関係のインストール（最小限）
RUN apt-get update && apt-get install -y \
    libopencv-core4.5 \
    libopencv-imgproc4.5 \
    libopencv-imgcodecs4.5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Pythonパッケージのコピー
COPY --from=builder /root/.local /home/appuser/.local

# アプリケーションディレクトリの作成
WORKDIR /app

# アプリケーションファイルのコピー
COPY src/ src/
COPY requirements.txt .

# ログディレクトリの作成
RUN mkdir -p logs && chown -R appuser:appuser logs

# 権限設定
RUN chown -R appuser:appuser /app

# 非rootユーザーに切り替え
USER appuser

# PATH設定
ENV PATH=/home/appuser/.local/bin:$PATH

# 環境変数設定
ENV ENVIRONMENT=production
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_MAX_UPLOAD_SIZE=10
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_ENABLE_CORS=false

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# ポート公開
EXPOSE 8501

# アプリケーション起動
CMD ["streamlit", "run", "src/main_enhanced.py", "--server.address", "0.0.0.0", "--server.port", "8501"]