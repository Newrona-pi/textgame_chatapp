# Character Chat App

位置情報に応じて背景画像が変化するキャラクター会話アプリです。Google Street View Static APIを使用して実際の風景写真を背景として表示します。

## 🌐 アクセス

**アプリURL**: https://wjktntfb.manus.space

## 📱 機能

### 基本機能
- キャラクターとの対話システム
- リアルタイムの日付・時刻表示
- 位置情報に応じた背景画像の動的変更
- 都道府県別の背景画像（47都道府県対応）

### 位置情報機能
- GPS位置情報の取得
- 都道府県の自動判定
- 現在地の都道府県名表示
- 位置情報に応じた背景画像の自動切り替え

### Google Street View機能
- 現在地の実際の風景写真を背景として表示
- 都道府県の代表的な観光地の風景表示
- 複数の角度から最適な画像を自動選択
- Street Viewデータが利用できない場合のフォールバック機能

## 🎮 使用方法

1. 上記URLにアクセス
2. ブラウザで位置情報のアクセスを許可
3. アプリが自動的に現在地を判定
4. Google Street View画像または対応する都道府県の背景画像が表示
5. キャラクターとの会話を開始

## 🛠 技術スタック

- **フロントエンド**: React + Tailwind CSS
- **バックエンド**: Flask API
- **データ管理**: CSV
- **デプロイ**: Manus Platform

## 📁 プロジェクト構成

```
character-chat-app/
├── frontend/          # React アプリ
│   ├── src/
│   │   ├── assets/    # 画像ファイル
│   │   ├── App.jsx    # メインコンポーネント
│   │   └── App.css    # スタイル
│   └── dist/          # ビルド済みファイル
├── backend/           # Flask API
│   ├── src/
│   │   ├── routes/    # APIルート
│   │   ├── character_service.py  # キャラクター管理
│   │   ├── characters.csv        # キャラクター設定
│   │   └── main.py    # メインアプリ
│   └── requirements.txt
└── data/              # 設定データ
    └── characters.csv # キャラクター人物像
```

## 🔧 カスタマイズ

### キャラクター設定の変更

`data/characters.csv`を編集してキャラクターの設定を変更できます：

- `name`: キャラクター名
- `personality`: 性格
- `tone`: 口調
- `greeting_prompts`: 挨拶メッセージ
- `casual_prompts`: 日常会話メッセージ
- `encouraging_prompts`: 励ましメッセージ

### OpenAI API連携

バックエンドに`.env`ファイルを作成し、OpenAI APIキーを設定することで、AI生成メッセージを利用できます：

```
OPENAI_API_KEY=your_api_key_here
```

### 背景画像の変更
1. `frontend/public/backgrounds/` ディレクトリ内の画像ファイルを置き換え
2. ファイル名は都道府県名（例：`東京.jpg`）に合わせる
3. 推奨サイズ：1920x1080px

### 座標データの調整
`frontend/src/utils/locationUtils.js` 内の `prefectureCoordinates` を編集することで、より正確な座標に調整できます。

### 観光地の変更
`frontend/src/utils/streetViewUtils.js` 内の `getPrefectureLandmark` 関数を編集することで、各都道府県の代表的な観光地を変更できます。

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

