from src.back.gate.function_gate import RunGemini
from src.back.definition.prompt import SYSTEM_PROMPT

def main():
    RunGemini_instance = RunGemini()
    RunGemini_instance.execute(SYSTEM_PROMPT)

if __name__ == "__main__":
    main()
