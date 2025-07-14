# 🚀 ミノルキューブ最適配送システム - デプロイメントガイド

## 📋 目次
1. [環境要件](#環境要件)
2. [本番環境セットアップ](#本番環境セットアップ)
3. [Docker デプロイ](#docker-デプロイ)
4. [設定管理](#設定管理)
5. [監視・メンテナンス](#監視メンテナンス)
6. [トラブルシューティング](#トラブルシューティング)

## 🔧 環境要件

### 最小要件
- **CPU**: 2コア以上
- **メモリ**: 4GB以上
- **ストレージ**: 20GB以上
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Docker対応OS

### 推奨要件
- **CPU**: 4コア以上
- **メモリ**: 8GB以上
- **ストレージ**: 50GB以上（SSD推奨）
- **ネットワーク**: 100Mbps以上

### 必要なソフトウェア
- Docker 20.10+
- Docker Compose 2.0+
- Git
- SSL証明書（本番環境）

## 🔒 本番環境セットアップ

### 1. リポジトリクローン
```bash
git clone https://github.com/your-org/minoru-packing-tools.git
cd minoru-packing-tools
```

### 2. 環境設定
```bash
# 環境変数ファイルの作成
cp .env.example .env

# 設定を編集
nano .env
```

### 3. 必須設定項目
```bash
# セキュリティ（必須）
SECRET_KEY=your-secret-key-here-at-least-32-characters-long

# データベース
DB_PASSWORD=secure-database-password

# 環境設定
ENVIRONMENT=production
```

### 4. SSL証明書の準備
```bash
# SSL証明書ディレクトリの作成
mkdir -p ssl

# 証明書ファイルの配置
# ssl/server.crt  - SSL証明書
# ssl/server.key  - 秘密鍵
```

## 🐳 Docker デプロイ

### 1. 基本デプロイ
```bash
# イメージのビルドと起動
docker-compose up -d

# ログの確認
docker-compose logs -f app
```

### 2. スケールアップ
```bash
# アプリケーションのスケール
docker-compose up -d --scale app=3

# ロードバランサーの設定
# nginx.confでupstreamを複数設定
```

### 3. データベース初期化
```bash
# データベース初期化（初回のみ）
docker-compose exec postgres psql -U postgres -d minoru_packing -f /docker-entrypoint-initdb.d/init.sql
```

## ⚙️ 設定管理

### 環境別設定

#### 開発環境
```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
MAX_WORKERS=2
RATE_LIMIT_PER_MINUTE=120
```

#### ステージング環境
```bash
ENVIRONMENT=staging
LOG_LEVEL=INFO
MAX_WORKERS=3
RATE_LIMIT_PER_MINUTE=80
```

#### 本番環境
```bash
ENVIRONMENT=production
LOG_LEVEL=WARNING
MAX_WORKERS=4
RATE_LIMIT_PER_MINUTE=30
```

### パフォーマンス最適化設定

#### 高負荷対応
```bash
# ワーカー数を増加
MAX_WORKERS=8

# キャッシュサイズを増加
CACHE_MAX_SIZE=5000

# タイムアウトを短縮
CALCULATION_TIMEOUT=15
```

#### 低リソース環境
```bash
# ワーカー数を削減
MAX_WORKERS=2

# キャッシュサイズを削減
CACHE_MAX_SIZE=500

# タイムアウトを延長
CALCULATION_TIMEOUT=60
```

## 📊 監視・メンテナンス

### 1. ヘルスチェック
```bash
# アプリケーションの健全性確認
curl -f http://localhost:8501/_stcore/health

# Docker コンテナの状態確認
docker-compose ps
```

### 2. ログ監視
```bash
# リアルタイムログ
docker-compose logs -f app

# エラーログのみ
docker-compose logs app | grep ERROR

# ログファイルの場所
# logs/minoru_packing.log      - 全般ログ
# logs/minoru_packing_error.log - エラーログ
```

### 3. パフォーマンス監視
```bash
# CPU・メモリ使用量
docker stats

# ディスク使用量
df -h

# プロセス確認
docker-compose exec app ps aux
```

### 4. バックアップ
```bash
# データベースバックアップ
docker-compose exec postgres pg_dump -U postgres minoru_packing > backup_$(date +%Y%m%d).sql

# ログファイルのローテーション
find logs/ -name "*.log.*" -mtime +30 -delete
```

## 🔄 デプロイメント手順

### 1. ゼロダウンタイムデプロイ
```bash
# 新しいバージョンのビルド
docker-compose build app

# ローリングアップデート
docker-compose up -d --no-deps app

# 旧コンテナの削除
docker image prune -f
```

### 2. ロールバック手順
```bash
# 前のバージョンに戻す
git checkout previous-version
docker-compose build app
docker-compose up -d --no-deps app
```

## 🔍 トラブルシューティング

### よくある問題と解決策

#### 1. アプリケーションが起動しない
```bash
# ログの確認
docker-compose logs app

# 設定の確認
docker-compose config

# 依存関係の確認
docker-compose exec app pip list
```

#### 2. データベース接続エラー
```bash
# データベース状態確認
docker-compose exec postgres pg_isready

# 接続テスト
docker-compose exec app python -c "import psycopg2; print('DB OK')"
```

#### 3. メモリ不足
```bash
# メモリ使用量確認
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# スワップ確認
free -h

# 設定調整
# docker-compose.ymlのmemory limitを調整
```

#### 4. 高CPU使用率
```bash
# プロファイリング
docker-compose exec app python -m cProfile -s cumulative src/main_production.py

# ワーカー数調整
# MAX_WORKERS環境変数を調整
```

### エラーコードと対処法

| エラーコード | 説明 | 対処法 |
|-------------|------|--------|
| PACKING_ERROR | パッキング計算エラー | 入力データの確認 |
| IMAGE_ERROR | 画像処理エラー | ファイル形式・サイズの確認 |
| VALIDATION_ERROR | 入力検証エラー | 入力値の範囲確認 |
| SYSTEM_ERROR | システムエラー | ログ確認・再起動 |

## 🔒 セキュリティ考慮事項

### 1. 本番環境での必須設定
- SSL/TLS証明書の設定
- ファイアウォールの設定
- 不要ポートの無効化
- 定期的な依存関係更新

### 2. 監査ログ
```bash
# セキュリティイベントの確認
grep "security_event" logs/minoru_packing.log

# 不正アクセスの確認
grep "rate_limit" logs/minoru_packing.log
```

### 3. 定期メンテナンス
```bash
# セキュリティアップデート（月1回）
docker-compose pull
docker-compose up -d

# ログのクリーンアップ（週1回）
find logs/ -name "*.log.*" -mtime +7 -delete

# データベースのメンテナンス（月1回）
docker-compose exec postgres vacuumdb -U postgres -d minoru_packing
```

## 📞 サポート

### 技術サポート
- **ドキュメント**: [システム仕様書](README.md)
- **ログ**: `logs/` ディレクトリ内
- **設定**: `.env` ファイル

### 緊急時対応
1. **サービス停止**: `docker-compose down`
2. **ログ収集**: `docker-compose logs > emergency.log`
3. **状態保存**: `docker-compose ps > status.txt`
4. **再起動**: `docker-compose up -d`

---

このガイドに従って適切にデプロイを行い、安定したサービス運用を実現してください。