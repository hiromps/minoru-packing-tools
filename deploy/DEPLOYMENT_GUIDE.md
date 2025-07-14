# 🚀 ミノルキューブ最適配送システム v3.0.0 デプロイガイド

## 📋 システム概要

**バージョン**: 3.0.0 (Production)  
**リリース日**: 2024年7月  
**環境**: Production Ready  

### 🎯 主要機能
- ✅ 3D重ね配置パッキング最適化
- ✅ AI画像認識による商品自動判定
- ✅ 3D可視化とインタラクティブ表示
- ✅ 複数配送業者の料金比較
- ✅ エンタープライズレベルのセキュリティ
- ✅ 高性能キャッシング・並列処理
- ✅ 詳細ログ・監視機能

## 🔧 システム要件

### 最小要件
- **OS**: Ubuntu 20.04 LTS / CentOS 8 / Amazon Linux 2
- **CPU**: 2 vCPU
- **RAM**: 4GB
- **ストレージ**: 20GB
- **Python**: 3.10以上
- **Docker**: 20.10以上（推奨）

### 推奨要件
- **OS**: Ubuntu 22.04 LTS
- **CPU**: 4 vCPU
- **RAM**: 8GB
- **ストレージ**: 50GB SSD
- **Python**: 3.11
- **Docker**: 24.0以上

## 🐳 Dockerでのデプロイ（推奨）

### 1. 準備
```bash
# リポジトリクローン
git clone https://github.com/your-org/minoru-packing-tools.git
cd minoru-packing-tools

# 環境変数設定
cp deploy/.env.example deploy/.env.production
nano deploy/.env.production  # 必要な値を設定
```

### 2. 重要な環境変数設定
```bash
# 必須: セキュリティキー（32文字以上）
SECRET_KEY=your-super-secure-random-key-here-at-least-32-characters

# 推奨: Redis（パフォーマンス向上）
REDIS_URL=redis://redis:6379/0

# オプション: SSL証明書
SSL_ENABLED=true
SSL_CERT_PATH=/etc/ssl/certs/minoru-packing.crt
SSL_KEY_PATH=/etc/ssl/private/minoru-packing.key
```

### 3. SSL証明書の準備（HTTPS用）
```bash
# 自己署名証明書（開発・テスト用）
mkdir -p deploy/ssl
openssl req -x509 -newkey rsa:4096 -keyout deploy/ssl/minoru-packing.key -out deploy/ssl/minoru-packing.crt -days 365 -nodes

# Let's Encrypt（本番用）
# certbot certonly --standalone -d your-domain.com
```

### 4. デプロイ実行
```bash
# Docker Compose でビルド・起動
cd deploy
docker-compose up -d

# ログ確認
docker-compose logs -f minoru-packing-app

# 状態確認
docker-compose ps
```

### 5. 動作確認
```bash
# ヘルスチェック
curl -f http://localhost:8501/_stcore/health

# アプリケーションアクセス
# HTTP: http://localhost
# HTTPS: https://localhost
```

## 🛠️ 直接デプロイ（非Docker）

### 1. 事前準備
```bash
# システムパッケージ更新
sudo apt update && sudo apt upgrade -y

# 必要なパッケージインストール
sudo apt install -y python3.11 python3.11-pip python3.11-venv nginx redis-server curl

# アプリケーションユーザー作成
sudo useradd -m -s /bin/bash minoru
sudo usermod -aG sudo minoru
```

### 2. アプリケーションデプロイ
```bash
# アプリケーションユーザーに切り替え
sudo su - minoru

# アプリケーションディレクトリ作成
mkdir -p /opt/minoru-packing
cd /opt/minoru-packing

# リポジトリクローン
git clone https://github.com/your-org/minoru-packing-tools.git .

# Python仮想環境作成
python3.11 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r deploy/requirements.txt

# 環境変数設定
cp deploy/.env.example .env
nano .env  # 必要な値を設定
```

### 3. システムサービス設定
```bash
# Systemdサービスファイル作成
sudo nano /etc/systemd/system/minoru-packing.service
```

```ini
[Unit]
Description=Minoru Packing Tools v3.0.0
After=network.target

[Service]
Type=simple
User=minoru
Group=minoru
WorkingDirectory=/opt/minoru-packing
Environment=PATH=/opt/minoru-packing/venv/bin
ExecStart=/opt/minoru-packing/venv/bin/python -m streamlit run src/main_production.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4. サービス起動
```bash
# サービス有効化・起動
sudo systemctl daemon-reload
sudo systemctl enable minoru-packing
sudo systemctl start minoru-packing

# 状態確認
sudo systemctl status minoru-packing
```

## 🔒 セキュリティ設定

### 1. ファイアウォール設定
```bash
# UFW設定
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw --force enable
```

### 2. Nginx設定（リバースプロキシ）
```bash
# 提供されたnginx.confを使用
sudo cp deploy/nginx.conf /etc/nginx/nginx.conf
sudo nginx -t
sudo systemctl restart nginx
```

### 3. 定期的なセキュリティ更新
```bash
# 自動更新設定
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 📊 監視・ログ設定

### 1. ログローテーション
```bash
sudo nano /etc/logrotate.d/minoru-packing
```

```
/var/log/minoru-packing/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 minoru minoru
    postrotate
        systemctl reload minoru-packing
    endscript
}
```

### 2. 監視スクリプト
```bash
# ヘルスチェックスクリプト
cat > /opt/minoru-packing/health_check.sh << 'EOF'
#!/bin/bash
if ! curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    echo "Application health check failed"
    systemctl restart minoru-packing
fi
EOF

chmod +x /opt/minoru-packing/health_check.sh

# Cronジョブ設定
echo "*/5 * * * * /opt/minoru-packing/health_check.sh" | sudo crontab -
```

## 🔄 アップデート手順

### 1. Docker環境
```bash
# 新しいイメージをビルド
docker-compose build --no-cache

# ダウンタイムなしでアップデート
docker-compose up -d

# 古いイメージクリーンアップ
docker image prune -f
```

### 2. 直接デプロイ環境
```bash
# メンテナンスモード
sudo systemctl stop minoru-packing

# コード更新
cd /opt/minoru-packing
git pull origin main

# 依存関係更新
source venv/bin/activate
pip install -r deploy/requirements.txt

# アプリケーション再起動
sudo systemctl start minoru-packing
```

## 🚨 トラブルシューティング

### よくある問題

#### 1. アプリケーションが起動しない
```bash
# ログ確認
docker-compose logs minoru-packing-app
# または
journalctl -u minoru-packing -f

# 一般的な原因:
# - SECRET_KEYが設定されていない
# - ポート8501が使用中
# - 権限不足
```

#### 2. 画像認識が動作しない
```bash
# OpenCV依存関係確認
pip list | grep opencv

# システムライブラリ確認
ldd /usr/local/lib/python3.11/site-packages/cv2/cv2.so
```

#### 3. パフォーマンスが遅い
```bash
# Redis接続確認
redis-cli ping

# リソース使用量確認
htop
df -h
```

## 📈 パフォーマンス最適化

### 1. Redis設定
```bash
# Redis設定ファイル
sudo nano /etc/redis/redis.conf

# 推奨設定
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### 2. Nginx最適化
```bash
# worker_connections調整
worker_connections 2048;

# Gzip圧縮有効化
gzip on;
gzip_min_length 1000;
```

## 📞 サポート

### 🔧 技術サポート
- **GitHub Issues**: https://github.com/your-org/minoru-packing-tools/issues
- **ドキュメント**: https://docs.minoru-packing.com
- **Email**: support@minoru-packing.com

### 📋 システム情報取得
```bash
# システム情報収集スクリプト
cat > system_info.sh << 'EOF'
#!/bin/bash
echo "=== System Information ==="
uname -a
cat /etc/os-release
echo "=== Python Version ==="
python3 --version
echo "=== Docker Version ==="
docker --version
echo "=== Memory Usage ==="
free -h
echo "=== Disk Usage ==="
df -h
echo "=== Application Status ==="
systemctl status minoru-packing
EOF

chmod +x system_info.sh
./system_info.sh
```

---

## 🎉 デプロイ完了！

正常にデプロイされると、以下の機能が利用可能になります：

- **メインアプリケーション**: https://your-domain.com
- **ヘルスチェック**: https://your-domain.com/_stcore/health
- **システム監視**: Redis, Nginx, アプリケーションログ

**📦 ミノルキューブ最適配送システム v3.0.0 へようこそ！**