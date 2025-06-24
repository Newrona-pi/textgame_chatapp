# デプロイ手順書

このプロジェクトをGitHub Pages（フロントエンド）とRender（バックエンド）にデプロイする手順です。

## 前提条件

- GitHubアカウント
- Renderアカウント
- Google Cloud Consoleアカウント（Google Maps API用）

## 1. バックエンド（Render）のデプロイ

### 1.1 Renderアカウントの準備
1. [Render](https://render.com/) にアクセス
2. GitHubアカウントでサインアップ/ログイン

### 1.2 新しいWeb Serviceを作成
1. Dashboardで「New +」→「Web Service」をクリック
2. GitHubリポジトリを選択
3. 以下の設定を行う：
   - **Name**: `character-chat-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python src/main.py`

### 1.3 環境変数の設定
Renderの管理画面で以下の環境変数を設定：
- `OPENAI_API_KEY`: OpenAI APIキー
- `PYTHON_VERSION`: `3.9.16`

### 1.4 デプロイの実行
1. 「Create Web Service」をクリック
2. デプロイが完了するまで待機（数分）
3. 発行されたURLをメモ（例：`https://character-chat-backend.onrender.com`）

## 2. フロントエンド（GitHub Pages）のデプロイ

### 2.1 GitHubリポジトリの準備
1. プロジェクトをGitHubにプッシュ
2. リポジトリの設定で「Pages」を有効化：
   - Settings → Pages
   - Source: 「GitHub Actions」を選択

### 2.2 GitHub Secretsの設定
リポジトリの設定で以下のSecretsを追加：
- `VITE_GOOGLE_API_KEY`: Google Maps APIキー
- `VITE_API_BASE_URL`: Renderで発行されたバックエンドURL

### 2.3 デプロイの実行
1. mainブランチにプッシュ
2. GitHub Actionsが自動的に実行される
3. デプロイが完了すると、GitHub PagesのURLが発行される

## 3. 動作確認

### 3.1 フロントエンドの確認
- GitHub PagesのURLにアクセス
- アプリが正常に表示されることを確認

### 3.2 バックエンドの確認
- Renderの管理画面でログを確認
- エラーがないことを確認

### 3.3 機能テスト
- 位置情報の取得
- 会話機能
- 好感度システム
- 背景画像の変更

## 4. トラブルシューティング

### 4.1 CORSエラー
- バックエンドでCORSが正しく設定されているか確認
- フロントエンドのAPI URLが正しいか確認

### 4.2 環境変数エラー
- GitHub Secretsが正しく設定されているか確認
- Renderの環境変数が正しく設定されているか確認

### 4.3 ビルドエラー
- 依存関係が正しくインストールされているか確認
- ビルドログを確認してエラーの詳細を確認

## 5. 本番環境での注意事項

### 5.1 セキュリティ
- APIキーは絶対にGitにコミットしない
- 本番環境ではHTTPSを使用
- 適切なCORS設定を行う

### 5.2 パフォーマンス
- 画像の最適化
- API呼び出しの最適化
- キャッシュの活用

### 5.3 監視
- ログの監視
- エラーの監視
- パフォーマンスの監視

## 6. 更新手順

### 6.1 フロントエンドの更新
1. コードを変更
2. mainブランチにプッシュ
3. GitHub Actionsが自動的にデプロイ

### 6.2 バックエンドの更新
1. コードを変更
2. mainブランチにプッシュ
3. Renderが自動的にデプロイ

## 7. ドメイン設定（オプション）

### 7.1 カスタムドメイン
- GitHub Pages: Settings → Pages → Custom domain
- Render: Settings → Custom Domains

### 7.2 SSL証明書
- GitHub Pages: 自動的にHTTPSが有効
- Render: 自動的にHTTPSが有効 