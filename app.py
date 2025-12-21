"""
Gunicorn用ブリッジエントリポイント。
`gunicorn app:app` でルートの `app` モジュールとして読み込まれるようにします。
"""

from src.app.app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
