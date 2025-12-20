"""
Geminiを実行するモジュール
"""

import os
from dotenv import load_dotenv

try:
    from src.back.definition.prompt import SYSTEM_PROMPT
    from src.back.definition.def_gemini import GeminiInput, GeminiOutput
except Exception:
    from src.back.definition.prompt import SYSTEM_PROMPT
    from src.back.definition.def_gemini import GeminiInput, GeminiOutput

try:
    from google import genai
except Exception:
    genai = None

try:
    from src.back.tools.save_json import save_json
except Exception:
    try:
        from back.tools.save_json import save_json
    except Exception:
        save_json = None

load_dotenv()   # ディレクトリにある.envファイルを読み込む

def run_gemini(prompt: str) -> str:
    """Geminiを実行させてstringで結果を返す

    Args:
        prompt (str): Geminiに渡すプロンプト
    Returns:
        str: generation text or error message
    """
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        return "Error: 環境変数 GOOGLE_API_KEY または GEMINI_API_KEY が見つかりません。.env に設定してください。"

    if genai is None:
        return "Error: google-genai ライブラリがインストールされていません。pip install google-genai を実行してください。"

    response = None
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    if response is None:
        return "Error: Geminiからの応答がありません。"

    text = response.text

    # ```json ... ``` の中身、または最初の {...} を抽出して JSON パースを試みる
    import json
    parsed = None
    try:
        if '```' in text:
            parts = text.split('```')
            for p in parts:
                s = p.strip()
                if s.startswith('{') and s.endswith('}'):
                    parsed = json.loads(s)
                    break
        if parsed is None:
            # 最初の { から最後の } を抜き出してみる
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1 and end > start:
                candidate = text[start:end+1]
                try:
                    parsed = json.loads(candidate)
                except Exception:
                    parsed = None
    except Exception:
        parsed = None

    if isinstance(parsed, dict):
        # JSON オブジェクトが得られたらファイルに保存してその dict を返す
        if save_json:
            try:
                save_json(parsed, folder="data/json")
            except Exception:
                pass
        return parsed
    # JSON にできない場合は生テキストを返す
    if save_json:
        try:
            save_json(text, folder="data/json")
        except Exception:
            pass
    return text


if __name__ == "__main__":
    response = run_gemini(prompt = SYSTEM_PROMPT)
    print(response)
