import os
from google import genai
from google.genai.errors import APIError
from PIL import Image
from io import BytesIO
from google.genai import types
from .prompt import SYSTEM_PROMPT

from dotenv import load_dotenv
load_dotenv()

# 環境変数から API キーを取得
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY が設定されていません。環境変数を確認してください。")

# クライアントの初期化
# GEMINI_API_KEYが環境変数に設定されていれば、引数なしで初期化できます。
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    print(f"クライアントの初期化中にエラーが発生しました: {e}")
    exit()

# 出力ファイル名
output_filename = "generated_image.png"

def generate_and_save_image(output_path: str) -> None:
    """
    Geminiによる画像生成関数
    Args:
        output_path: 出力する画像の名前
    """

    print(f"プロンプト: '{SYSTEM_PROMPT}' に基づいて画像を生成中...")
    
    try:
        # 画像生成API (Imagenモデル) の呼び出し
        # result = client.models.generate_images(
        #     model='gemini-2.5-flash-image',
        #     prompt=SYSTEM_PROMPT,
        #     config=dict(
        #         number_of_images=1, # 生成する画像の数
        #         output_mime_type="image/png", # 出力形式
        #         aspect_ratio="1:1" # アスペクト比 (例: "16:9", "1:1")
        #     )
        # )
        result = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[SYSTEM_PROMPT],
            config=types.GenerateContentConfig(
                image_config=types.ImageConfig(
                    aspect_ratio="16:9",
                )
            )
        )

        # 生成された画像データを取り出す
        if not result.generated_images:
            print("エラー: 画像が生成されませんでした。プロンプトを見直してください。")
            return

        # 最初の画像を処理
        generated_image_data = result.generated_images[0].image.image_bytes

        # バイナリデータをPIL Imageオブジェクトに変換
        image = Image.open(BytesIO(generated_image_data))
        
        # ファイルとして保存
        image.save(output_path)
        print(f"✅ 画像が正常に生成され、'{output_path}' に保存されました。")

    except APIError as e:
        print(f"APIエラーが発生しました: {e}")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")

if __name__ == "__main__":
    generate_and_save_image(output_filename)
