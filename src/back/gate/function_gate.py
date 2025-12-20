from src.back.core.run_gemini import run_gemini
from src.back.definition.def_gemini import GeminiInput, GeminiOutput
from src.back.db.supabase_client import select_data
from src.back.definition.prompt import SYSTEM_PROMPT
from src.back.db.supabase_client import get_horse_detail
import json
import os

REQUEST_PATH = os.path.join("src", "app", "requests", "request_horse.json")

class RunGemini():
    def execute(self) -> GeminiOutput:
        # リクエストJSONファイルが存在すれば読み取り（失敗しても継続）
        req = {}
        try:
            if os.path.exists(REQUEST_PATH):
                with open(REQUEST_PATH, "r", encoding="utf-8") as f:
                    req = json.load(f)
                    print(req.get("sire_name"), req.get("dam_name"), req.get("child_name"))
        except Exception:
            req = {}

        # SYSTEM_PROMPT 内には他の波括弧が含まれるため .format を使わず、
        # プレースホルダ文字列だけ安全に置換する
        sire_name = req.get("sire_name", "")
        sire_raw = get_horse_detail(sire_name)
        dam_name = req.get("dam_name", "")
        dam_raw = get_horse_detail(dam_name)
        # convert tuple (horse_data, races) to a JSON string for prompt injection
        def detail_to_str(detail):
            if not detail:
                return ""
            horse, races = detail
            return json.dumps({"horse": horse, "races": races}, ensure_ascii=False)
        sire_data = detail_to_str(sire_raw)
        dam_data = detail_to_str(dam_raw)
        child_name = req.get("child_name", "")
        prompt = SYSTEM_PROMPT
        prompt = prompt.replace("{sire}", sire_data)
        prompt = prompt.replace("{dam}", dam_data)
        prompt = prompt.replace("{child}", child_name)

        input_data = GeminiInput(prompt=prompt)
        print("Prompt prepared for Gemini (truncated):", input_data.prompt)

        # run_gemini は dict (parsed JSON) か文字列を返す
        result = run_gemini(input_data.prompt)

        if isinstance(result, dict):
            return GeminiOutput(**result)
        else:
            return GeminiOutput(response=str(result))

