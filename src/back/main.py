from src.back.gate.function_gate import RunGemini

def main():
    RunGemini_instance = RunGemini()
    output = RunGemini_instance.execute()
    print(output)

if __name__ == "__main__":
    main()
