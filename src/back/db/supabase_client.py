import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 環境変数の読み込み
load_dotenv()

# Supabaseの設定
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# クライアントの初期化（URLとKeyが設定されている場合のみ）
supabase: Client = None
if url and key and url != "your_supabase_url" and key != "your_api_key":
    supabase = create_client(url, key)
else:
    print("Warning: SUPABASE_URL or SUPABASE_KEY is not set correctly in .env file.")

def insert_data(table_name: str, data: dict):
    """
    データを挿入する関数
    :param table_name: テーブル名
    :param data: 挿入するデータ（辞書形式）
    :return: レスポンス
    """
    if not supabase:
        print("Supabase client is not initialized.")
        return None
    try:
        response = supabase.table(table_name).insert(data).execute()
        return response
    except Exception as e:
        print(f"Error inserting data: {e}")
        return None

def select_data(table_name: str, columns: str = "*"):
    """
    データを読み出す関数
    :param table_name: テーブル名
    :param columns: 取得するカラム（デフォルトは全て）
    :return: レスポンス
    """
    if not supabase:
        print("Supabase client is not initialized.")
        return None
    try:
        response = supabase.table(table_name).select(columns).execute()
        return response
    except Exception as e:
        print(f"Error selecting data: {e}")
        return None

def update_data(table_name: str, data: dict, record_id: int):
    """
    データを更新する関数
    :param table_name: テーブル名
    :param data: 更新するデータ
    :param record_id: 更新対象のID
    :return: レスポンス
    """
    if not supabase:
        print("Supabase client is not initialized.")
        return None
    try:
        response = supabase.table(table_name).update(data).eq("id", record_id).execute()
        return response
    except Exception as e:
        print(f"Error updating data: {e}")
        return None

def delete_data(table_name: str, record_id: int):
    """
    データを削除する関数
    :param table_name: テーブル名
    :param record_id: 削除対象のID
    :return: レスポンス
    """
    if not supabase:
        print("Supabase client is not initialized.")
        return None
    try:
        response = supabase.table(table_name).delete().eq("id", record_id).execute()
        return response
    except Exception as e:
        print(f"Error deleting data: {e}")
        return None


if __name__ == "__main__":
    # テスト用コード
    names = select_data("race_names")  # 適切なテーブル名に置き換えてください
    print(names)
    # insert_data("race_names", {'race_name': '天皇賞春', 'place_name': '京都競馬場', 'length': '3200', 'grass_or_dirt': 'grass', 'max_gate': '18'})  # 適切なテーブル名とデータに置き換えてください
    # names = select_data("race_names")  # 適切なテーブル名に置き換えてください
    # print(names)
