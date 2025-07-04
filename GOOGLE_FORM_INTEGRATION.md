# Googleフォーム連携ガイド

## 概要
このドキュメントでは、Googleフォームを使用してキャラクター情報を簡単に追加・管理する方法を説明します。

## システム構成

### 1. Googleフォームの設定

以下のフィールドを含むGoogleフォームを作成してください：

#### 基本情報
- **キャラクターID** (短答式)
  - 英数字のみ、一意である必要があります
  - 例: `mano`, `yuki`, `akari`

- **キャラクター名** (短答式)
  - キャラクターの表示名
  - 例: `真乃`, `雪`, `明里`

- **年齢** (短答式)
  - 数字のみ
  - 例: `17`, `16`, `18`

- **性格** (段落)
  - キャラクターの性格を詳しく記述
  - 例: `感情の起伏が大きい`, `クールで無口`, `明るく活発`

- **話し方のトーン** (短答式)
  - キャラクターの話し方の特徴
  - 例: `ため口`, `丁寧語`, `カジュアル`

- **設定** (短答式)
  - キャラクターの背景設定
  - 例: `高校2年生`, `転校生`, `生徒会長`

#### 詳細情報
- **背景ストーリー** (段落)
  - キャラクターの詳細な背景
  - 例: `女子高生`, `高校1年生`, `高校3年生`

- **キャラクター画像URL** (短答式)
  - キャラクター画像のURL
  - 例: `https://example.com/character.png`

- **背景画像URL** (短答式)
  - 背景画像のURL
  - 例: `https://example.com/background.jpg`

### 2. Google Apps Scriptの設定

#### スクリプトの作成
1. Googleフォームの回答スプレッドシートを開く
2. メニューから「拡張機能」→「Apps Script」を選択
3. 以下のスクリプトを貼り付ける

```javascript
function exportToCSV() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const data = sheet.getDataRange().getValues();
  
  // ヘッダー行
  const headers = [
    'character_id', 'name', 'age', 'personality', 'tone', 
    'setting', 'background', 'character_image_url', 'background_image_url'
  ];
  
  // データ行を処理
  const csvData = [headers];
  
  // 2行目以降（ヘッダーを除く）を処理
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const csvRow = [
      row[0], // character_id
      row[1], // name
      row[2], // age
      row[3], // personality
      row[4], // tone
      row[5], // setting
      row[6], // background
      row[7], // character_image_url
      row[8]  // background_image_url
    ];
    csvData.push(csvRow);
  }
  
  // CSV形式に変換
  const csvContent = csvData.map(row => 
    row.map(cell => `"${cell}"`).join(',')
  ).join('\n');
  
  // ファイルを作成
  const fileName = 'characters_' + new Date().toISOString().split('T')[0] + '.csv';
  const file = DriveApp.createFile(fileName, csvContent, MimeType.CSV);
  
  // ログに出力
  console.log('CSV file created: ' + file.getUrl());
  
  return file.getUrl();
}

// フォーム送信時に自動実行
function onFormSubmit(e) {
  // 新しい回答が追加されたときにCSVを更新
  exportToCSV();
}
```

#### トリガーの設定
1. Apps Scriptエディタで「トリガー」をクリック
2. 「トリガーを追加」をクリック
3. 以下の設定を行う：
   - 実行する関数: `onFormSubmit`
   - 実行するデプロイ: `Head`
   - イベントのソース: `フォームから`
   - イベントの種類: `フォーム送信時`

### 3. 画像アップロード機能

#### Google Drive連携
1. Google Driveに画像をアップロード
2. 画像を右クリック→「共有」→「リンクを取得」
3. 取得したURLをフォームの画像URLフィールドに入力

#### 画像URLの形式
```
https://drive.google.com/uc?export=view&id=【ファイルID】
```

### 4. CSVファイルの配置

1. Google Apps Scriptで生成されたCSVファイルをダウンロード
2. `backend/src/characters.csv` に配置
3. アプリケーションを再起動

## 使用方法

### 1. キャラクター追加
1. Googleフォームにアクセス
2. キャラクター情報を入力
3. フォームを送信
4. Apps Scriptが自動的にCSVを更新
5. アプリケーションで新しいキャラクターが利用可能

### 2. キャラクター編集
1. スプレッドシートで直接編集
2. `exportToCSV()` 関数を手動実行
3. 生成されたCSVファイルをアプリケーションに配置

### 3. キャラクター削除
1. スプレッドシートから該当行を削除
2. `exportToCSV()` 関数を手動実行
3. 生成されたCSVファイルをアプリケーションに配置

## 注意事項

### セキュリティ
- 画像URLは公開アクセス可能なものにしてください
- 機密情報は含めないでください

### データ形式
- キャラクターIDは一意である必要があります
- 年齢は数字のみ入力してください
- URLは有効な形式で入力してください

### パフォーマンス
- 大量のキャラクターを追加する場合は、アプリケーションの起動時間が長くなる可能性があります
- 画像サイズは適切に最適化してください

## トラブルシューティング

### よくある問題

#### 1. キャラクターが表示されない
- CSVファイルの形式を確認
- 文字エンコーディングがUTF-8になっているか確認
- アプリケーションを再起動

#### 2. 画像が表示されない
- 画像URLが正しいか確認
- 画像が公開アクセス可能か確認
- ブラウザの開発者ツールでエラーを確認

#### 3. フォーム送信時にエラーが発生
- Apps Scriptの権限を確認
- トリガーが正しく設定されているか確認
- スプレッドシートの権限を確認

## サポート

問題が発生した場合は、以下を確認してください：
1. ブラウザのコンソールログ
2. Apps Scriptの実行ログ
3. アプリケーションのログ

必要に応じて、開発チームにお問い合わせください。 