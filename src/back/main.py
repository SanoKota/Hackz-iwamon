from src.back.gate.function_gate import RunGemini

def main():
    RunGemini_instance = RunGemini()
    output = RunGemini_instance.execute()
    print(output)
    dream_output = RunGemini_instance.dream_race()
    print(dream_output)

if __name__ == "__main__":
    main()
