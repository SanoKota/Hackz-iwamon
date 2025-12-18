from flask import Flask, render_template, request
import sys
import os

# プロジェクトルートをパスに追加してsrcモジュールをインポート可能にする
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.back.gate.function_gate import RunGemini

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    response_text = None
    if request.method == 'POST':
        prompt = request.form.get('prompt')
        if prompt:
            try:
                # Geminiを実行
                gemini = RunGemini()
                output = gemini.execute(prompt=prompt)
                response_text = output.response
            except Exception as e:
                response_text = f"エラーが発生しました: {str(e)}"
    
    return render_template('index.html', response=response_text)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
