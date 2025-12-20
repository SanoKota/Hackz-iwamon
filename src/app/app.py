from flask import Flask, render_template, request, jsonify
import sys
import os
import json

# パス設定
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.back.gate.function_gate import RunGemini

# アップロードフォルダ設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'requests')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# JSからのデータ処理
@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        # JSから送られたJSONを受け取る
        data = request.json

        # JSONファイルを保存
        filename = f"request_horse.json"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, 'a') as f:
            json_str = json.dumps(data, ensure_ascii=False, indent=4)
            f.write(json_str + '\n')
        
        # 値を取り出し
        sire = data.get('sire_name')
        dam = data.get('dam_name')
        child_name = data.get('child_name')

        # プロンプト組み立て（テスト）
        prompt = f"父:{sire}, 母:{dam}, 子:{child_name} の血統を持つ馬の戦績を考えて"

        # Geminiを実行
        gemini = RunGemini()
        output = gemini.execute(prompt=prompt)
        response_text = output.response

        return jsonify({
            "status": "success",
            "result": response_text
        })

    except Exception as e:
        error_details = traceback.format_exc()
        return jsonify({
            "status": "error",
            "message": str(e),
            "error_details": error_details
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)