
# MADE BY CONNOR CAMPAGNA @ 2025

import sys
from interpreter import Interpreter

def main():
    interpreter = Interpreter()

    if len(sys.argv) == 2:
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                program = interpreter.parser.parse(lines)
                interpreter.load_program(program)
                interpreter.run()
        except FileNotFoundError:
            print(f"File '{filename}' not found.")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Usage: python main.py file.clu")

if __name__ == "__main__":
    main()
