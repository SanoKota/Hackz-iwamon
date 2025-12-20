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

def select_data(table_name: str, columns: str = "*", row: int = None):
    """
    データを読み出す関数
    :param table_name: テーブル名
    :param columns: 取得するカラム（デフォルトは全て）
    :param row: 取得する行数の上限（指定しない場合は全件）
    :return: レスポンス
    """
    if not supabase:
        print("Supabase client is not initialized.")
        return None
    try:
        query = supabase.table(table_name).select(columns)
        if row is not None:
            try:
                # Treat `row` as 1-based index and fetch only that single row via range
                idx = int(row)
                if idx > 0:
                    start = idx - 1
                    query = query.range(start, start)
            except Exception:
                pass
        response = query.execute()
        # Try to extract actual row data from the response object
        data = None
        try:
            # supabase-py / postgrest response usually has `.data`
            data = getattr(response, "data", None)
        except Exception:
            data = None
        if data is None:
            try:
                # sometimes response is a dict-like
                if isinstance(response, dict) and "data" in response:
                    data = response.get("data")
            except Exception:
                data = None
        # Fallback: if still None, return the raw response
        if data is None:
            print(response)
            return response
        return data
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

def get_horse_detail(horse_name: str) -> dict:
    """
    馬名から馬の詳細情報を取得する関数
    :param horse_name: 馬名
    :return: 馬の詳細情報
    """
    # Basic wrapper: try to fetch a single row for the given horse name
    horse_data = ""

    data = select_data("horse", columns="*")
    # iterate rows until a matching name is found (1-based index)
    for i in range(len(data)):
        if data[i]['name'] == horse_name:
            i += 1
            horse_data = select_data("horse", columns="*", row=i)  # 1-based index
            horse_index = data[i]['horse_id'] - 1
            break
    result_data = select_data("result", columns="*")
    race_index = []
    count = 0
    race_date = {}
    for i in range(len(result_data)):
        if result_data[i]['horse_id'] == horse_index:
            race_index.append(result_data[i]['race_id'])
            race_date[count] = result_data[i]
            count += 1
    race_data = select_data("race", columns="*")
    race_result = {}
    count = 0
    for i in range(len(race_data)):
        if race_data[i]['race_id'] in race_index:
            race_result[count] = race_data[i]
            count += 1

    result_data = {}
    for i in range(count):
        rr = race_result.get(i, {})
        rd = race_date.get(i, {})
        merged = rr.copy() if isinstance(rr, dict) else {}
        merged['rank'] = rd.get('rank')
        merged['date'] = rd.get('date')
        result_data[i] = merged

    return horse_data[0], result_data    


if __name__ == "__main__":
    # テスト用コード（環境変数が未設定の場合は警告が出ます）
    # index = get_horse_detail(horse_name = "アーモンドアイ")
    names = select_data(table_name="race")  # 適切なテーブル名に置き換えてください
    # print(index)
    print(names)
    # insert_data("race_names", {'race_name': '天皇賞春', 'place_name': '京都競馬場', 'length': '3200', 'grass_or_dirt': 'grass', 'max_gate': '18'})  # 適切なテーブル名とデータに置き換えてください
    # names = select_data("race_names")  # 適切なテーブル名に置き換えてください
    # print(names)
