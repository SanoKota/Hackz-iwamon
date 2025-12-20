from flask import Flask, render_template, request, jsonify
import sys
import os
import json
import traceback

# パス設定
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.back.gate.function_gate import RunGemini
import csv

# アップロードフォルダ設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'requests')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

# CSV読み込みヘルパー
def load_csv_data(filename):
    filepath = os.path.join(BASE_DIR, '../../sample_data', filename)
    data = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    return data

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
        with open(filepath, 'w') as f:
            json.dumps(data, f, ensure_ascii=False, indent=4)
        
        # 値を取り出し
        sire = data.get('sire_name')
        dam = data.get('dam_name')
        child_name = data.get('child_name')

        # プロンプト組み立て（テスト）
        prompt = f"父:{sire}, 母:{dam}, 子:{child_name} の血統を持つ馬の戦績を考えて"

        # Geminiを実行
        gemini = RunGemini()
        output = gemini.execute(prompt)
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

@app.route('/race', methods=['GET'])
def race():
    return render_template('race.html')

@app.route('/gallery', methods=['GET'])
def gallery():
    horses_data = load_csv_data('horses.csv')
    horses = []
    for h in horses_data:
        # CSV structure: horse_id,name,sex,father,mother,mother_father
        horses.append({
            "id": h['horse_id'],
            "name": h['name'],
            "sire": f"{h['father']} (Father)",
            "dam": f"{h['mother']} (Mother)",
            "image": f"https://placehold.co/600x400/1e293b/38bdf8?text={h['name']}",
            "description": f"父: {h['father']}, 母: {h['mother']}, 母父: {h['mother_father']}。幻の名馬。"
        })
    return render_template('gallery.html', horses=horses)

@app.route('/api/horses', methods=['GET'])
def get_horses():
    try:
        horses_data = load_csv_data('horses.csv')
        # Frontend expects a simple list or specific structure
        # Let's return formatted data similar to what's used in gallery
        formatted_horses = []
        for h in horses_data:
            formatted_horses.append({
                "id": h['horse_id'],
                "name": h['name'],
                "value": f"{h['name']} ({h['father']} x {h['mother']})" # Value for race selection
            })
        return jsonify({"status": "success", "horses": formatted_horses})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/races', methods=['GET'])
def get_races():
    try:
        races_data = load_csv_data('races.csv')
        return jsonify({"status": "success", "races": races_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/run_race', methods=['POST'])
def run_race():
    try:
        data = request.json or {}
        selected_horses = data.get('horses', [])
        race_id = data.get('race_id')

        if not selected_horses or len(selected_horses) == 0:
            return jsonify({"status": "error", "message": "No horses selected"}), 400
        
        entries = selected_horses
        
        # Load race info
        races_data = load_csv_data('races.csv')
        target_race = None
        
        if race_id:
            for r in races_data:
                if str(r.get('race_id')) == str(race_id):
                    target_race = r
                    break
        
        # Default if not found or not specified
        if not target_race:
             target_race = races_data[0] if races_data else {"race_name": "Dream Race", "distance": "2400", "course": "Tokyo", "track_type": "Turf"}

        # Construct Prompt
        prompt = f"""
        以下の伝説の競走馬たちによる「{target_race['race_name']}」の実況中継を行ってください。
        
        出走馬: {', '.join(entries)}
        
        条件:
        - 舞台: {target_race['course']} {target_race['track_type']} {target_race['distance']}m
        - 天候: 晴良馬場
        
        指示:
        - スタートからゴールまで、熱狂的な実況スタイルで描写してください。
        - 各馬の特徴（脚質など）を反映させてください。
        - 最後は接戦の末、1頭が優勝します。順位も決めてください。
        """

        # Execute Gemini
        gemini = RunGemini()
        output = gemini.execute(prompt=prompt)
        
        return jsonify({
            "status": "success",
            "result": output.response
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