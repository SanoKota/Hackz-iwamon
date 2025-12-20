from flask import Flask, render_template, request, jsonify
import sys
import os

# パス設定
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.back.gate.function_gate import RunGemini

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
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)