# Hackz-iwamon

## 概要

架空の馬作成アプリ

実際の馬を2頭選択して、そこから生まれる馬の名前を入力します。
入力されたデータから、Geminiが生まれた馬の4歳までの戦績を出力します。

## 実行方法

```
python3 main.py
```

## 始め方

### 仮想環境の実行

仮想環境に入る
```
source ./venv/bin/activate
```
仮想環境から出る
```
deactivate
```
新しくライブラリを追加する
```
pip install ライブラリ名
```

### APIキーの設定

.envファイルに以下のAPIキーを設定してください
```
GOOGLE_API_KEY="your_api_key"
SUPABASE_KEY="your_api_key"
```
