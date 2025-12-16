from src.back.core.run_gemini import run_gemini
from src.back.schema.new_horse import GeminiInput, GeminiOutput

class RunGemini():
    def execute(self, prompt: str) -> GeminiOutput:
        input_data = GeminiInput(prompt=prompt)
        return GeminiOutput(response=run_gemini(input_data.prompt))

