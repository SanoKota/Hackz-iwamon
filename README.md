# Hackz-iwamon

## 概要

俺の配合

実際の馬を2頭選択して、そこから生まれる馬の名前を入力します。
入力されたデータから、Geminiが生まれた馬の4歳までの戦績を出力します。

URL: デプロイ先
```
https://hackz-iwamon.onrender.com/
```
## 実行方法

アプリの実行
```
python -m src.app.app
```

Geminiを含めたバックのみ実行
```
python -m src.back.main
```

Geminiだけの実行
```
python -m src.back.core.run_gemini
```

## 始め方

### APIキーの設定

.envファイルに以下のAPIキーを設定してください
```
GOOGLE_API_KEY="your_api_key"
SUPABASE_KEY="your_api_key"
```
