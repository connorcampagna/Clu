from parser import Parser

class Interpreter:
    def __init__(self):
        self.variables = {}
        self.parser = Parser(self.variables)
        self.execution_stack = []
        self.functions = {}  # function name -> Function object

    def should_execute(self):
        if not self.execution_stack:
            return True
        top = self.execution_stack[-1]
        return top in ("if-true", "otherwise")


    def load_program(self, program):
        self.program = program
        self.functions = program.functions  # load defined functions

    def run(self):
        for instr in self.program:
            self.execute_instruction(instr)

    def execute_instruction(self, instruction):
        action = instruction.action
        args = instruction.args

        if action == "output":
            if self.should_execute():
                var = args[0]
                if var in self.variables:
                    print(self.variables[var])
                else:
                    print(f"Undefined variable '{var}'")

        elif action == "assign":
            if self.should_execute():
                var, expr = args
                try:
                    self.variables[var] = self.evaluate_expression(expr)
                except Exception as e:
                    print(f"Error: {e}")

        elif action == "add":
            if self.should_execute():
                a, b = args
                if a in self.variables and b in self.variables:
                    self.variables[a] += self.variables[b]
                else:
                    print(f"Undefined variable '{a}' or '{b}'")

        elif action == "if":
            var1, op, var2 = args
            try:
                result = self.evaluate_condition(var1, op, var2)
                self.execution_stack.append("if-true" if result else "if-false")
            except Exception as e:
                print(f"Error: {e}")
                self.execution_stack.append("if-false")

        elif action == "otherwise":
            if not self.execution_stack:
                print("Error: otherwise without if")
                return
            current = self.execution_stack.pop()
            if current == "if-true":
                self.execution_stack.append("skip-otherwise")
            elif current == "if-false":
                self.execution_stack.append("otherwise")
            else:
                print("Error: invalid otherwise state")

        elif action == "end":
            if self.execution_stack:
                self.execution_stack.pop()

        elif action == "call":
            func_name = args[0]
            call_args = args[1:]
            if func_name in self.functions:
                func = self.functions[func_name]
                if len(func.params) != len(call_args):
                    print(f"Error: {func_name} expects {len(func.params)} arguments.")
                    return
                saved_variables = self.variables.copy()
                for param, arg in zip(func.params, call_args):
                    try:
                        self.variables[param] = int(arg)
                    except ValueError:
                        if arg in saved_variables:
                            self.variables[param] = saved_variables[arg]
                        else:
                            print(f"Unknown argument '{arg}' passed to {func_name}")
                            return
                for instr in func.body:
                    self.execute_instruction(instr)
                self.variables = saved_variables
            else:
                print(f"Unknown function '{func_name}'")

        elif action == "unknown":
            print(f"Unknown command: {args[0]}")

    def evaluate_expression(self, parts):
        # same as before
        if len(parts) == 1:
            try:
                return int(parts[0])
            except ValueError:
                if parts[0] in self.variables:
                    return self.variables[parts[0]]
                raise ValueError(f"Unknown variable or value '{parts[0]}'")
        if len(parts) == 3:
            a, op, b = parts
            if a not in self.variables or b not in self.variables:
                raise ValueError(f"Unknown variables '{a}' or '{b}'")
            if op == "add":
                return self.variables[a] + self.variables[b]
            if op == "subtract":
                return self.variables[a] - self.variables[b]
            if op == "multiply":
                return self.variables[a] * self.variables[b]
            if op == "divide":
                if self.variables[b] == 0:
                    raise ZeroDivisionError("Division by zero")
                return self.variables[a] // self.variables[b]
        raise ValueError(f"Invalid expression: {' '.join(parts)}")

    def evaluate_condition(self, var1, op, var2):
        v1 = self.variables.get(var1)
        v2 = self.variables.get(var2)
        if v1 is None or v2 is None:
            raise ValueError("Unknown variables in condition")

        if op == "greater":
            return v1 > v2
        if op == "less":
            return v1 < v2
        if op == "equal":
            return v1 == v2
        if op == "greater_equal":
            return v1 >= v2
        if op == "less_equal":
            return v1 <= v2
        raise ValueError(f"Unknown operator '{op}' in condition")
