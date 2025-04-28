class Instruction:
    def __init__(self, action, args):
        self.action = action
        self.args = args

class Function:
    def __init__(self, name, params=None):
        self.name = name
        self.params = params if params else []
        self.body = []

    def add_instruction(self, instruction):
        self.body.append(instruction)


class Program:
    def __init__(self):
        self.instructions = []
        self.functions = {}  # name -> Function

    def add_instruction(self, instruction):
        self.instructions.append(instruction)

    def add_function(self, function):
        self.functions[function.name] = function

    def __iter__(self):
        return iter(self.instructions)
