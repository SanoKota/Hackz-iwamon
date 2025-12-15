"""
Geminiを実行するモジュール
"""

from dotenv import load_dotenv
import os

try:
    from src.back.definition.prompt import SYSTEM_PROMPT
    from src.back.definition.def_gemini_output import GeminiInput, GeminiOutput
except Exception:
    from src.back.definition.prompt import SYSTEM_PROMPT
    from src.back.definition.def_gemini_output import GeminiInput, GeminiOutput

try:
    from google import genai
except Exception:
    genai = None

load_dotenv()   # ディレクトリにある.envファイルを読み込む

def run_gemini():
    """Geminiを実行させてstringで結果を返す

    Returns:
        str: generation text or error message
    """
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        return "Error: 環境変数 GOOGLE_API_KEY または GEMINI_API_KEY が見つかりません。.env に設定してください。"

    if genai is None:
        return "Error: google-genai ライブラリがインストールされていません。pip install google-genai を実行してください。"

    client = genai.Client(api_key=api_key)

    prompt = GeminiInput(prompt=SYSTEM_PROMPT)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt.prompt,
    )

    # BaseModelで出力の型を定義
    answer = GeminiOutput(response=response.text)
    print(answer)
    return answer.response


if __name__ == "__main__":
    response = run_gemini()
    print(response)
