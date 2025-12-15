"""
参考資料：Gemini公式ドキュメント
https://ai.google.dev/gemini-api/docs?hl=ja

ノーマルなGeminiを走らせるテンプレート
"""
from dotenv import load_dotenv
import os

try:
    from .prompt import SYSTEM_PROMPT
    from .definition_answer import DefinitionAnswer
except Exception:
    from prompt import SYSTEM_PROMPT
    from definition_answer import DefinitionAnswer

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

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=SYSTEM_PROMPT,
    )

    # BaseModelで出力の型を定義
    answer = DefinitionAnswer(answer=response.text)
    print(answer)
    return answer.answer


if __name__ == "__main__":
    run_gemini()
