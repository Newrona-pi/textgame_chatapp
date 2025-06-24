# Google Street View Static API 設定ガイド

このアプリケーションでGoogle Street View Static APIを使用するための設定手順です。

## 1. Google Cloud Console でプロジェクトを作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成するか、既存のプロジェクトを選択
3. プロジェクト名を記録しておく

## 2. Google Maps Platform を有効化

1. Google Cloud Console の左側メニューから「APIとサービス」→「ライブラリ」を選択
2. 検索バーで「Street View Static API」を検索
3. 「Street View Static API」を選択して「有効にする」をクリック

## 3. APIキーを作成

1. Google Cloud Console の左側メニューから「APIとサービス」→「認証情報」を選択
2. 「認証情報を作成」→「APIキー」をクリック
3. 作成されたAPIキーをコピー

## 4. APIキーの制限を設定（推奨）

セキュリティのため、APIキーに制限を設定することを推奨します：

1. 作成したAPIキーをクリック
2. 「アプリケーションの制限」で「HTTPリファラー」を選択
3. 「ウェブサイトの制限」に以下を追加：
   - `http://localhost:5173/*` (開発環境)
   - `http://localhost:3000/*` (開発環境)
   - 本番環境のドメイン（例：`https://yourdomain.com/*`）

## 5. 環境変数ファイルを作成

1. `frontend/env.example` を `frontend/.env` にコピー
2. `frontend/.env` ファイルを開いて、APIキーを設定：

```env
VITE_GOOGLE_API_KEY=your_actual_api_key_here
```

## 6. アプリケーションを起動

```bash
cd frontend
npm run dev
```

## 7. 動作確認

1. ブラウザで位置情報のアクセスを許可
2. アプリが現在地を判定
3. Google Street View画像が背景に表示されることを確認

## 注意事項

- APIキーは絶対にGitにコミットしないでください
- `.env` ファイルは `.gitignore` に含まれています
- Google Maps Platform には使用量制限があります（月間$200相当まで無料）
- 本番環境では適切なドメイン制限を設定してください

## トラブルシューティング

### APIキーが無効な場合
- APIキーが正しく設定されているか確認
- Street View Static APIが有効になっているか確認
- ドメイン制限が正しく設定されているか確認

### 画像が表示されない場合
- 指定した座標にStreet Viewデータが存在するか確認
- ネットワーク接続を確認
- ブラウザの開発者ツールでエラーメッセージを確認

## 料金について

Google Maps Platform の料金体系：
- 月間$200相当まで無料
- Street View Static API: $7 per 1000 requests
- 詳細は [Google Maps Platform 料金](https://cloud.google.com/maps-platform/pricing) を参照 