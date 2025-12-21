import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def _read_secret_file(path: str) -> str | None:
    try:
        if not path:
            return None
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            value = f.read().strip()
        return value or None
    except Exception:
        return None

def get_supabase_credentials() -> tuple[str | None, str | None]:
    """
    SUPABASEのURLとKEYを取得する。
    優先順:
      1. 環境変数 SUPABASE_URL / SUPABASE_KEY
      2. 環境変数で指定されたファイル SUPABASE_URL_FILE / SUPABASE_KEY_FILE
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if url and key:
        return url, key

    url_file = os.environ.get("SUPABASE_URL_FILE")
    key_file = os.environ.get("SUPABASE_KEY_FILE")
    url_from_file = _read_secret_file(url_file)
    key_from_file = _read_secret_file(key_file)

    return url or url_from_file, key or key_from_file

def create_supabase_client() -> Client | None:
    """
    取得した資格情報からSupabaseクライアントを生成する。
    足りない場合はNoneを返し、分かりやすい警告を出す。
    """
    url, key = get_supabase_credentials()
    if not url or not key:
        print(
            "Warning: SUPABASE_URL or SUPABASE_KEY is not set. "
            "Set them via environment variables on Render or a local .env."
        )
        return None
    try:
        return create_client(url, key)
    except Exception as e:
        print(f"Error creating Supabase client: {e}")
        return None

supabase: Client | None = create_supabase_client()

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
    # Optimized version that avoids redundant fetches and index errors
    horse_data = {}
    horse_index = -1

    data = select_data("horse", columns="*")
    if not data:
        return {}, {}

    for h in data:
        if h.get('name') == horse_name:
            horse_data = h
            # The original code did -1, maintaining that logic though it's suspicious
            # Assuming horse_id is present. If not, default to -1 to avoid matching anything
            hid = h.get('horse_id')
            if hid is not None:
                 horse_index = hid - 1
            break
    
    if not horse_data:
        return {}, {}
        
    result_data = select_data("result", columns="*") or []
    race_index = []
    race_date = {}
    
    # Filter results for this horse
    # Note: result_data[i]['horse_id'] compared to horse_index
    count = 0
    for r in result_data:
        if r.get('horse_id') == horse_index:
            race_index.append(r.get('race_id'))
            race_date[count] = r
            count += 1
            
    race_data = select_data("race", columns="*") or []
    race_result = {}
    
    # Match races
    count_r = 0
    for r in race_data:
        if r.get('race_id') in race_index:
            race_result[count_r] = r
            count_r += 1

    # Merge data
    # The original merged logic was slightly confusing (mapping by `count` index).
    # Replicating it safely:
    # `race_date` keys are 0..count-1
    # `race_result` keys are 0..count_r-1
    # Assuming count == count_r because they are filtered by same race_ids logic?
    # Not necessarily if data is inconsistent, but strict logic implies:
    # race_index has N IDs.
    # race_result has M races (where M <= N because some IDs might not exist in race table)
    # But `race_result` keys are 0..M-1.
    # `race_date` keys are 0..N-1.
    # if we loop range(count), we might miss if race is missing.
    
    # Let's map by race_id to be safer and cleaner, as proposed before.
    
    clean_results = {}
    if race_data:
        # Create a lookup for race: id -> data
        race_lookup = {r.get('race_id'): r for r in race_data}
        
        # Iterate through the horse's results
        idx = 0
        for r in result_data:
            if r.get('horse_id') == horse_index:
                rid = r.get('race_id')
                race_info = race_lookup.get(rid, {})
                
                # Merge
                merged = race_info.copy()
                merged['rank'] = r.get('rank')
                merged['date'] = r.get('date')
                
                clean_results[idx] = merged
                idx += 1
                
    return horse_data, clean_results

def get_race_detail(race_name: str) -> dict:
    """
    レース名からレースの詳細情報を取得する関数 
    :param race_name: レース名
    :return: レースの詳細情報
    """
    # Optimized version
    data = select_data("race", columns="*")
    if not data:
        return {}
        
    for r in data:
        if r.get('name') == race_name:
            return r
            
    return {}


if __name__ == "__main__":
    # テスト用コード（環境変数が未設定の場合は警告が出ます）
    index = get_horse_detail(horse_name = "アーモンドアイ")
    # names = select_data(table_name="race")  # 適切なテーブル名に置き換えてください
    print(index)
    # print(names)
    # insert_data("race_names", {'race_name': '天皇賞春', 'place_name': '京都競馬場', 'length': '3200', 'grass_or_dirt': 'grass', 'max_gate': '18'})  # 適切なテーブル名とデータに置き換えてください
    # names = select_data("race_names")  # 適切なテーブル名に置き換えてください
    # print(names)
