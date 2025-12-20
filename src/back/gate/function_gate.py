from src.back.core.run_gemini import run_gemini
from src.back.definition.def_gemini import GeminiInput, GeminiOutput

class RunGemini():
    def execute(self, prompt: str) -> GeminiOutput:
        input_data = GeminiInput(prompt=prompt)
        result = run_gemini(input_data.prompt)
        # run_gemini は dict (parsed JSON) か文字列を返す
        if isinstance(result, dict):
            return GeminiOutput(**result)
        else:
            return GeminiOutput(response=str(result))

