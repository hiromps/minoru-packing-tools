# 🚀 GitHubプッシュ＆デプロイガイド

## 📋 概要

**リポジトリ**: `git@github.com:hiromps/minoru-packing-tools.git`  
**バージョン**: 3.0.0 (Production)  
**デプロイ方法**: 複数のプラットフォーム対応

## 🔧 事前準備

### 1. GitHubリポジトリのセットアップ

```bash
# 現在のディレクトリで初期化
git init
git remote add origin git@github.com:hiromps/minoru-packing-tools.git

# または既存リポジトリをクローン
git clone git@github.com:hiromps/minoru-packing-tools.git
cd minoru-packing-tools
```

### 2. GitHub Secretsの設定

GitHubリポジトリの Settings > Secrets and variables > Actions で以下を設定:

#### 🔐 必須Secrets

```bash
# Streamlit Community Cloud（最優先）
STREAMLIT_SHARING_EMAIL=your-email@example.com

# Docker Hub（オプション）
DOCKER_HUB_USERNAME=your-dockerhub-username
DOCKER_HUB_TOKEN=your-dockerhub-token

# Heroku（オプション）
HEROKU_API_KEY=your-heroku-api-key
HEROKU_APP_NAME=minoru-packing-tools
HEROKU_EMAIL=your-email@example.com

# Railway（オプション）
RAILWAY_TOKEN=your-railway-token

# Render（オプション）
RENDER_API_KEY=your-render-api-key
RENDER_SERVICE_ID=your-render-service-id

# Vercel（オプション）
VERCEL_TOKEN=your-vercel-token
VERCEL_ORG_ID=your-vercel-org-id
VERCEL_PROJECT_ID=your-vercel-project-id

# 通知（オプション）
SLACK_WEBHOOK=your-slack-webhook-url
DISCORD_WEBHOOK=your-discord-webhook-url
```

## 🚀 デプロイ手順

### 1. Streamlit Community Cloud（推奨・無料）

```bash
# コードをプッシュ
git add .
git commit -m "Deploy v3.0.0 to Streamlit Community Cloud"
git push origin main
```

**手動デプロイ手順:**
1. [Streamlit Community Cloud](https://share.streamlit.io/) にアクセス
2. GitHubアカウントでログイン
3. 「New app」をクリック
4. Repository: `hiromps/minoru-packing-tools`
5. Branch: `main`
6. Main file path: `src/main_production.py`
7. 「Deploy!」をクリック

**🔗 デプロイ後のURL**: `https://hiromps-minoru-packing-tools-main-srcmain-production-xyz.streamlit.app/`

### 2. 自動デプロイ（GitHub Actions）

```bash
# mainブランチにプッシュすると自動デプロイ
git add .
git commit -m "🚀 Deploy v3.0.0 - 3D packing optimization"
git push origin main
```

**実行される処理:**
- ✅ テスト実行
- 🐳 Dockerイメージビルド＆プッシュ
- 🚀 複数プラットフォームへの同時デプロイ
- 📢 Slack/Discord通知

### 3. 手動デプロイ（ワークフロー実行）

```bash
# GitHub Actionsページで手動実行
# Actions > Deploy Minoru Packing Tools v3.0.0 > Run workflow
```

## 🐳 プラットフォーム別デプロイ

### Streamlit Community Cloud
```bash
# requirements.txtが自動で読み込まれる
# 設定ファイル: なし（自動設定）
# 起動コマンド: streamlit run src/main_production.py
```

### Heroku
```bash
# Dockerfileでデプロイ
# 設定ファイル: deploy/Dockerfile
# 環境変数: Heroku Config Vars
```

### Railway
```bash
# Dockerまたはソースコードデプロイ
# 設定ファイル: railway.toml（自動生成）
# 環境変数: Railway Variables
```

### Render
```bash
# Dockerfileでデプロイ
# 設定ファイル: render.yaml（自動生成）
# 環境変数: Render Environment Variables
```

### Vercel
```bash
# Serverless Functionsとしてデプロイ
# 設定ファイル: vercel.json（自動生成）
# 環境変数: Vercel Environment Variables
```

## 🔍 デプロイ状況確認

### GitHub Actions
```bash
# ブラウザで確認
https://github.com/hiromps/minoru-packing-tools/actions

# CLI確認（gh CLI必要）
gh run list
gh run view --log
```

### アプリケーション確認
```bash
# ヘルスチェック
curl -f https://your-app-url.streamlit.app/_stcore/health

# 機能確認
curl -f https://your-app-url.streamlit.app/
```

## 📊 モニタリング

### ログ確認
```bash
# GitHub Actions ログ
gh run view --log latest

# Streamlit Community Cloud
# アプリページの右下「Manage app」> 「Logs」
```

### エラー対応
```bash
# よくあるエラー
1. requirements.txtの依存関係エラー
2. メモリ不足（Community Cloudの制限）
3. 環境変数未設定
4. ファイルパス問題
```

## 🛠️ トラブルシューティング

### 1. Streamlit Community Cloud
```bash
# エラー: Module not found
# 解決: requirements.txtに依存関係を追加

# エラー: Memory limit exceeded
# 解決: 軽量化または有料プランへ移行

# エラー: App crashed
# 解決: ログを確認してエラー箇所を特定
```

### 2. GitHub Actions
```bash
# エラー: Secrets not found
# 解決: GitHub Settings > Secrets で設定確認

# エラー: Docker build failed
# 解決: Dockerfileの構文確認

# エラー: Tests failed
# 解決: ローカルでテスト実行してデバッグ
```

## 🎯 最適なデプロイ戦略

### 開発フェーズ
1. **開発**: ローカル環境
2. **テスト**: GitHub Actions（PR時）
3. **ステージング**: Streamlit Community Cloud
4. **本番**: Heroku/Railway/Render

### 簡単デプロイ（推奨）
```bash
# 1. コードを更新
git add .
git commit -m "Update feature"
git push origin main

# 2. Streamlit Community Cloudで自動デプロイ
# 3. 数分で本番環境で利用可能
```

## 📞 サポート

### 🔧 デプロイ関連
- **GitHub Issues**: https://github.com/hiromps/minoru-packing-tools/issues
- **Streamlit Community**: https://discuss.streamlit.io/

### 🚨 緊急時対応
```bash
# ロールバック
git revert HEAD
git push origin main

# 緊急メンテナンス
# Streamlit Community Cloudアプリを一時停止
```

---

## 🎉 デプロイ完了！

正常にデプロイされると以下のようなURLでアクセス可能:

**🔗 Streamlit Community Cloud**: `https://hiromps-minoru-packing-tools-main-srcmain-production-xyz.streamlit.app/`

**📦 ミノルキューブ最適配送システム v3.0.0 が本番環境で利用可能です！**