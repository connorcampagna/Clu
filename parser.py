from program import Instruction, Program, Function


class Parser:
    def __init__(self, variables):
        self.variables = variables

    def parse(self, lines):
        program = Program()
        i = 0
        while i < len(lines):
            parts = lines[i].strip().split()
            if not parts:
                i += 1
                continue

            cmd = parts[0].lower()

            if cmd == "function":
                # Custom parsing for: function name -> param1/param2
                if "->" in parts:
                    idx = parts.index("->")
                    func_name = parts[1]
                    params = parts[idx + 1].split('/')
                else:
                    func_name = parts[1]
                    params = []

                func = Function(func_name, params)
                i += 1
                while i < len(lines):
                    parts_inside = lines[i].strip().split()
                    if not parts_inside:
                        i += 1
                        continue
                    if parts_inside[0].lower() == "end":
                        break
                    instr = self.parse_line(" ".join(parts_inside))
                    if instr:
                        func.add_instruction(instr)
                    i += 1
                program.add_function(func)

            elif cmd == "repeat":
                var = parts[1]
                op = parts[2]
                value = parts[3]
                repeat_body = []
                i += 1
                while i < len(lines):
                    parts_inside = lines[i].strip().split()
                    if not parts_inside:
                        i += 1
                        continue
                    if parts_inside[0].lower() == "end":
                        break
                    instr = self.parse_line(" ".join(parts_inside))
                    if instr:
                        repeat_body.append(instr)
                    i += 1
                program.add_instruction(Instruction("repeat_block", (var, op, value, repeat_body)))

            else:
                instr = self.parse_line(" ".join(parts))
                if instr:
                    program.add_instruction(instr)

            i += 1

        return program

    def parse_line(self, command):
        parts = command.strip().split()
        if not parts:
            return None

        cmd = parts[0].lower()

        if cmd == "output" and len(parts) == 2:
            return Instruction("output", (parts[1],))

        if len(parts) >= 3 and parts[1].lower() == "is":
            var = parts[0]
            expr = parts[2:]
            return Instruction("assign", (var, expr))

        if len(parts) == 3 and parts[1].lower() == "add":
            return Instruction("add", (parts[0], parts[2]))

        if cmd == "if" and len(parts) == 4:
            return Instruction("if", (parts[1], parts[2], parts[3]))

        if cmd == "otherwise":
            return Instruction("otherwise", ())

        if cmd == "loop":
            return Instruction("loop", (parts[1], parts[2], parts[3]))

        if cmd == "end":
            return Instruction("end", ())

        # No repeat here anymore!

        # Default: treat as function call
        return Instruction("call", tuple(parts))



