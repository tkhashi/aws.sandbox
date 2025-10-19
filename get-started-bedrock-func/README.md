# Bedrock画像生成Lambda関数

このプロジェクトは、Amazon BedrockのTitan Image Generatorを使用してAI画像を生成するLambda関数と、それを呼び出すフロントエンドアプリケーションで構成されています。

## プロジェクト構成

```
get-started-bedrock-func/
├── lambda_function.py     # Lambda関数本体
├── .awsignore            # AWS Toolkitデプロイ時の除外設定
├── README.md             # このファイル
└── frontend/             # フロントエンドアプリ（Lambdaデプロイ対象外）
    ├── index.html        # Webアプリケーション
    └── .env              # 環境設定ファイル
```

## デプロイ方法

### Lambda関数のデプロイ
1. AWS Toolkitを使用してLambda関数をデプロイ
2. `.awsignore`により、frontendディレクトリは自動的に除外されます

### API Gateway設定
1. Lambda関数にAPI Gatewayトリガーを追加
2. POSTメソッドを有効化
3. CORS設定で`http://localhost:3000`からのアクセスを許可

### フロントエンドアプリの設定
1. `frontend/.env`ファイルのAPI_GATEWAY_ENDPOINTを実際のエンドポイントURLに更新
2. フロントエンドディレクトリでローカルサーバーを起動

## 使用方法

1. フロントエンドアプリをローカルで起動:
   ```bash
   cd frontend
   python3 -m http.server 3000
   # または
   npx serve -p 3000
   ```

2. ブラウザで http://localhost:3000 にアクセス

3. 「設定をロード」ボタンで.envファイルから設定を読み込み

4. 画像生成プロンプトを入力して「画像を生成」をクリック

## 必要な権限

Lambda関数には以下のAWS権限が必要です：
- bedrock:InvokeModel (Titan Image Generator用)
- s3:PutObject (画像アップロード用)
- s3:GetObject (署名付きURL生成用)

## 注意事項

- frontendディレクトリはLambdaデプロイに含まれません
- .envファイルの実際のエンドポイントURLは手動で設定が必要です
- ローカル開発時はCORS設定により`http://localhost:3000`からのアクセスのみ許可されます