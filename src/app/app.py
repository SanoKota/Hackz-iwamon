from flask import Flask, render_template, request, jsonify
import os
import json
import traceback
import sys

# パス設定
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.back.gate.function_gate import RunGemini
from src.back.db.supabase_client import select_data

# アップロードフォルダ設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'requests')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 監視対象のJSONファイルパス (../../data/json/geminioutput.json)
JSON_OUTPUT_PATH = os.path.abspath(os.path.join(BASE_DIR, '../../data/json/geminioutput.json'))

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
        with open(filepath, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        # Geminiを実行
        # ※ ここでRunGeminiがgeminioutput.jsonを更新することを想定しています
        gemini = RunGemini()
        output = gemini.execute()
        
        # Consider structure data if response is None
        response_text = output.response
        if not response_text:
            # Format structured data to Markdown (Logic restored from previous check_update)
            name = output.name or 'Unknown Horse'
            characteristics = output.characteristics or ''
            race_record = output.race_record or []

            response_text = f"# {name}\n\n"
            if characteristics:
                response_text += f"**特徴**: {characteristics}\n\n"
            
            response_text += "## 戦績\n"
            if race_record:
                for race in race_record:
                    if isinstance(race, dict):
                        r_name = race.get('race_name', '-')
                        rank = race.get('ranking', '-')
                        date = race.get('date', '-')
                        detail = race.get('detail', '')
                        response_text += f"- **{r_name}** ({date}): {rank}着\n"
                        if detail:
                            response_text += f"  - {detail}\n"
                    else:
                        response_text += f"- {str(race)}\n"
            else:
                response_text += "戦績なし\n"

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
        }, 500)

@app.route('/race', methods=['GET'])
def race():
    return render_template('race.html')

@app.route('/gallery', methods=['GET'])
def gallery():
    horses_data = select_data('horse')
    if horses_data is None:
        horses_data = []
    
    horses = []
    for h in horses_data:
        # DB columns: id, name, father, mother, mother_father, etc.
        name = h.get('name', 'Unknown')
        father = h.get('father', '')
        mother = h.get('mother', '')
        grandpa = h.get('grandpa', '')
        
        horses.append({
            "id": h.get('id'), # Assuming DB uses 'id' as primary key
            "name": name,
            "sire": father,
            "dam": mother,
            "grandpa": grandpa,
            "image": f"https://placehold.co/600x400/1e293b/38bdf8?text={name}",
        })
    return render_template('gallery.html', horses=horses)

@app.route('/api/horses', methods=['GET'])
def get_horses():
    try:
        horses_data = select_data('horse')
        if horses_data is None:
            horses_data = []
            
        formatted_horses = []
        for h in horses_data:
            name = h.get('name', 'Unknown')
            father = h.get('father', '?')
            mother = h.get('mother', '?')
            
            formatted_horses.append({
                "id": h.get('id'),
                "name": name,
                "value": name,
                "sex": h.get('sex', 'Unknown')
            })
        return jsonify({"status": "success", "horses": formatted_horses})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/races', methods=['GET'])
def get_races():
    try:
        races_data = select_data('race')
        if races_data is None:
            races_data = []
        
        formatted_races = []
        for r in races_data:
            formatted_races.append({
                "race_id": r.get('race_id') or r.get('id'),
                "race_name": r.get('race_name') or r.get('name', 'Unknown Race'),
                "racetrack": r.get('racetrack') or r.get('course', 'Unknown'),
                "track_type": r.get('ground') or r.get('track_type', 'Turf'),
                "distance": r.get('distance', '2400')
            })
        return jsonify({"status": "success", "races": formatted_races})
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
        
        # Load race info from DB
        races_data = select_data('race')
        if races_data is None:
            races_data = []
            
        target_race = None
        
        if race_id:
            for r in races_data:
                # DB column might be 'id' or 'race_id'. Trying both.
                r_id = r.get('race_id') or r.get('id')
                if str(r_id) == str(race_id):
                    target_race = r
                    break
        
        # Default if not found or not specified
        if not target_race:
             target_race = races_data[0] if races_data else {"race_name": "Dream Race", "distance": "2400", "course": "Tokyo", "track_type": "Turf"}
             
        # Strip pedigree info from names (e.g. "Name (Sire x Dam)" -> "Name")
        cleaned_entries = [e.split(' (')[0] for e in entries]

        # Save request_dream.json
        try:
            dream_request_data = {
                "race_name": target_race.get('race_name') or target_race.get('name', 'Unknown Race'),
                "entries": cleaned_entries
            }
            dream_json_path = os.path.join(UPLOAD_FOLDER, "request_dream.json")
            with open(dream_json_path, 'w', encoding='utf-8') as f:
                json.dump(dream_request_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving request_dream.json: {e}")

        # Execute Gemini
        gemini = RunGemini()
        output = gemini.dream_race()
        
        return jsonify({
            "status": "success",
            "result": output
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