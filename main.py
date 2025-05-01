from clucore import Parser, Interpreter
from program import Program

import sys

if len(sys.argv) != 2:
    print("Usage: python main.py program.clu")
    exit()

filename = sys.argv[1]
with open(filename, "r") as f:
    lines = f.readlines()

interpreter = Interpreter()
parser = Parser(interpreter.variables)
program = parser.parse(lines)
interpreter.load_program(program)
interpreter.run()
