
import re
from program import Instruction, Program, Function

class Tokenizer:
    def __init__(self, lines):
        self.lines = lines

    def tokenize(self):
        tokenized_lines = []
        for line in self.lines:
            line = re.sub(r'#.*', '', line).strip()
            if not line:
                continue
            tokens = re.findall(r"'[^']*'|->|\w+(?:/\w+)*|[^\s\w]", line)
            tokenized_lines.append(tokens)
        return tokenized_lines


class Parser:
    def __init__(self, variables):
        self.variables = variables

    def parse(self, lines):
        self.tokens = Tokenizer(lines).tokenize()
        self.index = 0
        program = Program()

        while self.index < len(self.tokens):
            tokens = self.tokens[self.index]
            if not tokens:
                self.index += 1
                continue

            if tokens[0] == "function":
                func = self.parse_function(tokens)
                program.add_function(func)
            else:
                instr = self.parse_line(tokens)
                if instr:
                    program.add_instruction(instr)

            self.index += 1

        return program

    def parse_function(self, header_tokens):
        name = header_tokens[1]
        params = []
        if "->" in header_tokens:
            idx = header_tokens.index("->")
            params = header_tokens[idx + 1].split("/")
        func = Function(name, params)

        self.index += 1
        while self.index < len(self.tokens):
            tokens = self.tokens[self.index]
            if tokens and tokens[0] == "end":
                break
            instr = self.parse_line(tokens)
            if instr:
                func.add_instruction(instr)
            self.index += 1

        return func

    def parse_line(self, tokens):
        if not tokens:
            return None

        if tokens[0] == "var" and "is" in tokens:
            idx = tokens.index("is")
            var_name = tokens[1]
            value = tokens[idx + 1:]
            return Instruction("assign", (var_name, value))

        if tokens[0] == "output":
            return Instruction("output", (" ".join(tokens[1:]),))

        if tokens[0] == "if" and len(tokens) == 4:
            return Instruction("if", (tokens[1], tokens[2], tokens[3]))

        if tokens[0] == "otherwise":
            return Instruction("otherwise", ())

        if tokens[0] == "repeat" and len(tokens) >= 4:
            return self.parse_repeat(tokens)

        if tokens[0] == "end":
            return Instruction("end", ())

        return Instruction("call", tuple(tokens))

    def parse_repeat(self, tokens):
        var, op, value = tokens[1], tokens[2], tokens[3]
        body = []

        self.index += 1
        while self.index < len(self.tokens):
            tokens = self.tokens[self.index]
            if tokens and tokens[0] == "end":
                break
            instr = self.parse_line(tokens)
            if instr:
                body.append(instr)
            self.index += 1

        return Instruction("repeat_block", (var, op, value, body))


class Interpreter:
    def __init__(self):
        self.variables = {}
        self.execution_stack = []
        self.functions = {}

    def _apply_op(self, va, op, vb):
        # '+' only for chars
        if op == "+":
            if isinstance(va, str) and isinstance(vb, str):
                return va + vb
            raise ValueError("Operator '+' only works on chars")

        # 'add' only for ints
        if op == "add":
            if isinstance(va, int) and isinstance(vb, int):
                return va + vb
            raise ValueError("Operator 'add' only works on numbers")

        # subtraction
        if op in ("subtract", "-"):
            return va - vb

        # multiplication
        if op in ("multiply", "*"):
            return va * vb

        # integer division
        if op in ("divide", "/"):
            return va // vb

        raise ValueError(f"Unknown operator '{op}'")



    def load_program(self, program):
        self.program = program
        self.functions = program.functions

    def should_execute(self):
        return not self.execution_stack or self.execution_stack[-1] in ("if-true", "otherwise")

    def run(self):
        for instr in self.program:
            self.execute_instruction(instr)

    def execute_instruction(self, instr):
        action, args = instr.action, instr.args

        if action == "output" and self.should_execute():
            expr = args[0].strip()
            value = self.evaluate_output(expr)
            print(value)

        elif action == "assign" and self.should_execute():
            var, expr = args
            self.variables[var] = self.evaluate_expression(expr)

        elif action == "if":
            result = self.evaluate_condition(*args)
            self.execution_stack.append("if-true" if result else "if-false")

        elif action == "otherwise":
            prev = self.execution_stack.pop()
            self.execution_stack.append("otherwise" if prev == "if-false" else "skip")

        elif action == "end":
            if self.execution_stack:
                self.execution_stack.pop()

        elif action == "repeat_block" and self.should_execute():
            var, op, value, body = args
            while self.evaluate_condition(var, op, value):
                for instr in body:
                    self.execute_instruction(instr)

        elif action == "call" and self.should_execute():
            name, *args_passed = args
            func = self.functions.get(name)
            if func:
                backup = self.variables.copy()
                for param, arg in zip(func.params, args_passed):
                    self.variables[param] = int(arg) if arg.isdigit() else self.variables.get(arg, 0)
                for instr in func.body:
                    self.execute_instruction(instr)
                self.variables = backup

    def evaluate_output(self, expr):
        # literal list
        if ',' in expr and all(tok.isdigit() or tok == ',' for tok in expr.replace(' ', '')):
            return [int(x) for x in expr.split(',')]
        if expr.startswith("'") and expr.endswith("'"):
            return expr[1:-1]
        if expr.isdigit():
            return int(expr)
        return self.variables.get(expr, f"Undefined: {expr}")

    def evaluate_expression(self, parts):
        # — LIST LITERAL SUPPORT (if you have it) —
        if len(parts) >= 3 and all(parts[i] == ',' for i in range(1, len(parts), 2)):
            try:
                return [int(parts[i]) for i in range(0, len(parts), 2)]
            except ValueError:
                raise ValueError(f"Invalid list literal: {' '.join(parts)}")

        # — ANY-LENGTH BINARY-OP FOLD (handles 'add', 'multiply', etc.) —
        if len(parts) > 1:
            # resolve the very first term
            left = self.evaluate_expression([parts[0]])
            i = 1
            while i < len(parts):
                op = parts[i]
                right = self.evaluate_expression([parts[i + 1]])
                left = self._apply_op(left, op, right)
                i += 2
            return left

        # — SINGLE-PART LITERAL or VARIABLE —
        token = parts[0]
        if token.startswith("'") and token.endswith("'"):
            return token[1:-1]
        if token.isdigit():
            return int(token)
        return self.variables.get(token, f"Undefined: {token}")




    def evaluate_condition(self, var1, op, var2):
        v1 = self.variables.get(var1, int(var1) if var1.isdigit() else 0)
        v2 = self.variables.get(var2, int(var2) if var2.isdigit() else 0)

        if op == "greater": return v1 > v2
        if op == "less": return v1 < v2
        if op == "equal": return v1 == v2
        if op == "greater_equal": return v1 >= v2
        if op == "less_equal": return v1 <= v2

        raise ValueError(f"Unknown operator: {op}")
