# Fixed CLU Language Interpreter
# Written By Connor Campagna @ 2025
# UOFG STUDENT
# Fixed parsing issues and enhanced with new features

import re
from typing import List, Dict, Any, Union, Optional
from dataclasses import dataclass

from program import Instruction, Program, Function


@dataclass
class CLUError(Exception):
    """Base exception for CLU runtime errors"""
    message: str
    line_number: Optional[int] = None

    def __str__(self):
        if self.line_number:
            return f"Line {self.line_number}: {self.message}"
        return self.message


class CLUTypeError(CLUError):
    """Type-related errors in CLU"""
    pass


class CLUNameError(CLUError):
    """Name/variable not found errors"""
    pass


class CLUIndexError(CLUError):
    """Index out of bounds errors"""
    pass


class Tokenizer:
    def __init__(self, lines: List[str]):
        self.lines = lines
        self.token_pattern = r'\d+\.\d+|\w+\([^\)]+\)|\w+\[[^\]]+\]|->|\w+(?:/\w+)*|".*?"|\'.*?\'|\d+|\w+|[^\s\w]'

    def tokenize(self) -> List[tuple]:
        tokenized = []
        for line_num, line in enumerate(self.lines, 1):
            # Strip comments and whitespace
            line = re.sub(r'#.*', '', line).strip()
            if not line:
                continue

            try:
                tokens = re.findall(self.token_pattern, line)
                if tokens:
                    tokenized.append((tokens, line_num))
            except re.error as e:
                raise CLUError(f"Tokenization error: {e}", line_num)

        return tokenized


class Parser:
    def __init__(self):
        pass

    def parse(self, lines: List[str]) -> Program:
        self.tokenized_lines = Tokenizer(lines).tokenize()
        self.i = 0
        program = Program()

        while self.i < len(self.tokenized_lines):
            tokens, line_num = self.tokenized_lines[self.i]

            if not tokens:
                self.i += 1
                continue

            try:
                if tokens[0] == "function":
                    func = self._parse_function(tokens, line_num)
                    program.add_function(func)
                else:
                    instr = self._parse_line(tokens, line_num)
                    if instr:
                        program.add_instruction(instr)
            except CLUError:
                raise
            except Exception as e:
                raise CLUError(f"Parse error: {e}", line_num)

            self.i += 1

        return program

    def _parse_line(self, tokens: List[str], line_num: int) -> Optional[Instruction]:
        """Parse a single line of code efficiently with boolean logic support"""
        if not tokens:
            return None

        # Get first token for efficient dispatch
        first_token = tokens[0]

        # Use dictionary-based dispatch for better performance
        parser_functions = {
            "var": self._parse_var_assignment,
            "output": self._parse_output,
            "if": self._parse_if,
            "otherwise": self._parse_otherwise,
            "repeat": self._parse_repeat,
            "foreach": self._parse_foreach,
            "end": self._parse_end
        }

        # Call specific parser function if available
        if first_token in parser_functions:
            return parser_functions[first_token](tokens, line_num)

        # Default case: function calls
        instr = Instruction("call", tuple(tokens))
        instr.line_number = line_num
        return instr

    def _parse_var_assignment(self, tokens: List[str], line_num: int) -> Instruction:
        """Parse variable assignment"""
        if "is" not in tokens:
            raise CLUError("Missing 'is' in variable assignment", line_num)

        idx = tokens.index("is")
        if len(tokens) < idx + 2 or idx < 1:  # Must have: var, name, is, value
            name = tokens[1] if len(tokens) > 1 else "unknown"
            raise CLUError(f"Variable '{name}' assignment is incomplete", line_num)

        name = tokens[1]
        expr = tokens[idx + 1:]

        instr = Instruction("assign", (name, expr))
        instr.line_number = line_num
        return instr

    def _parse_output(self, tokens: List[str], line_num: int) -> Instruction:
        """Parse output statement"""
        if len(tokens) <= 1:
            raise CLUError("Output statement requires an expression", line_num)

        instr = Instruction("output", (" ".join(tokens[1:]),))
        instr.line_number = line_num
        return instr

    def _parse_if(self, tokens: List[str], line_num: int) -> Instruction:
        """Parse if statement with enhanced boolean logic support"""
        # Simple case: if x op y
        if len(tokens) == 4 and tokens[2] in ["greater", "less", "equal", "greater_equal", "less_equal", "not_equal"]:
            instr = Instruction("if", (tokens[1], tokens[2], tokens[3]))
            instr.line_number = line_num
            return instr

        # Complex boolean expressions case
        elif "and" in tokens[1:] or "or" in tokens[1:] or "not" in tokens[1:] or len(tokens) > 1 and tokens[1] in [
            "True", "False"]:
            # Get the entire condition as a string
            condition = " ".join(tokens[1:])
            instr = Instruction("if_complex", (condition,))
            instr.line_number = line_num
            return instr

        # Boolean variable case: "if is_valid"
        elif len(tokens) == 2:
            instr = Instruction("if_bool", (tokens[1],))
            instr.line_number = line_num
            return instr

        # Invalid if statement
        else:
            raise CLUError("Invalid if statement syntax", line_num)

    def _parse_otherwise(self, tokens: List[str], line_num: int) -> Instruction:
        """Parse otherwise statement"""
        instr = Instruction("otherwise", ())
        instr.line_number = line_num
        return instr

    def _parse_end(self, tokens: List[str], line_num: int) -> Instruction:
        """Parse end statement"""
        instr = Instruction("end", ())
        instr.line_number = line_num
        return instr

    def _parse_repeat(self, tokens: List[str], line_num: int) -> Instruction:
        if len(tokens) < 4:
            raise CLUError("Invalid repeat statement", line_num)

        var, op, value = tokens[1], tokens[2], tokens[3]
        body = []

        self.i += 1
        nested = 1

        while self.i < len(self.tokenized_lines):
            curr_tokens, curr_line = self.tokenized_lines[self.i]

            if curr_tokens and curr_tokens[0] == "end":
                nested -= 1
                if nested == 0:
                    break
            elif curr_tokens and curr_tokens[0] in ("repeat", "if", "function", "foreach"):
                nested += 1

            instr = self._parse_line(curr_tokens, curr_line)
            if instr:
                body.append(instr)
            self.i += 1

        instr = Instruction("repeat_block", (var, op, value, body))
        instr.line_number = line_num
        return instr

    def _parse_foreach(self, tokens: List[str], line_num: int) -> Instruction:
        var_name = tokens[1]
        list_name = tokens[3]
        body = []

        self.i += 1
        while self.i < len(self.tokenized_lines):
            curr_tokens, curr_line = self.tokenized_lines[self.i]
            if curr_tokens and curr_tokens[0] == "end":
                break
            instr = self._parse_line(curr_tokens, curr_line)
            if instr:
                body.append(instr)
            self.i += 1

        instr = Instruction("foreach", (var_name, list_name, body))
        instr.line_number = line_num
        return instr


class Interpreter:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.execution_stack: List[str] = []
        self.functions: Dict[str, Function] = {}
        self.program: Optional[Program] = None

        # Built-in functions registry
        self.builtin_functions = {
            "sum": lambda x: sum(x) if isinstance(x, list) and all(
                isinstance(i, (int, float)) for i in x) else self._type_error("sum", x),
            "max": lambda x: max(x) if isinstance(x, list) and x and all(
                isinstance(i, (int, float)) for i in x) else self._type_error("max", x),
            "min": lambda x: min(x) if isinstance(x, list) and x and all(
                isinstance(i, (int, float)) for i in x) else self._type_error("min", x),
            "len": lambda x: len(x) if isinstance(x, (list, str)) else self._type_error("len", x),
            "sorted": lambda x: sorted(x) if isinstance(x, list) else self._type_error("sorted", x),
            "reversed": lambda x: list(reversed(x)) if isinstance(x, list) else self._type_error("reversed", x),
            "average": lambda x: sum(x) / len(x) if isinstance(x, list) and x and all(
                isinstance(i, (int, float)) for i in x) else self._type_error("average", x),
            "first": lambda x: x[0] if isinstance(x, list) and x else self._type_error("first", x),
            "last": lambda x: x[-1] if isinstance(x, list) and x else self._type_error("last", x),

            # New conversion functions
            "str": self._to_string,
            "int": self._to_int,
            "float": self._to_float,
            "bool": self._to_bool,

            # BOOL
            "all": lambda x: all(x) if isinstance(x, list) else self._type_error("all", x),
            "any": lambda x: any(x) if isinstance(x, list) else self._type_error("any", x),
            "is_bool": lambda x: isinstance(x, bool),

            # New utility functions
            "type": lambda x: type(x).__name__,
            "empty": lambda x: len(x) == 0 if isinstance(x, (list, str)) else False,
            "contains": self._contains,
        }

    def _type_error(self, func_name: str, value: Any) -> None:
        raise CLUTypeError(f"Function '{func_name}' cannot be applied to {type(value).__name__}: {value}")

    def _to_string(self, value: Any) -> str:
        """Convert any value to string"""
        if isinstance(value, str):
            return value
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, list):
            return "[" + ", ".join(self._to_string(item) for item in value) + "]"
        else:
            return str(value)

    def _to_int(self, value: Any) -> int:
        """Convert value to integer"""
        if isinstance(value, int):
            return value
        elif isinstance(value, float):
            return int(value)
        elif isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                raise CLUTypeError(f"Cannot convert '{value}' to integer")
        else:
            raise CLUTypeError(f"Cannot convert {type(value).__name__} to integer")

    def _to_float(self, value: Any) -> float:
        """Convert value to float"""
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                raise CLUTypeError(f"Cannot convert '{value}' to float")
        else:
            raise CLUTypeError(f"Cannot convert {type(value).__name__} to float")

    def _contains(self, container: Any, item: Any) -> bool:
        """Check if container contains item"""
        if isinstance(container, (list, str)):
            return item in container
        else:
            raise CLUTypeError(f"Contains operation not supported for {type(container).__name__}")

    def load_program(self, program: Program):
        self.program = program
        self.functions = program.functions

    def should_execute(self) -> bool:
        return not self.execution_stack or self.execution_stack[-1] in ("if-True", "otherwise")

    def run(self):
        if not self.program:
            raise CLUError("No program loaded")

        try:
            for instr in self.program:
                self.execute_instruction(instr)
        except CLUError:
            raise
        except Exception as e:
            raise CLUError(f"Runtime error: {e}")

    def execute_instruction(self, instr: Instruction):
        action, args = instr.action, instr.args

        try:
            if action == "output" and self.should_execute():
                self._execute_output(args, instr)
            elif action == "assign" and self.should_execute():
                self._execute_assign(args, instr)
            elif action == "if":
                self._execute_if(args, instr)
            elif action == "otherwise":
                self._execute_otherwise(instr)
            elif action == "end":
                self._execute_end(instr)
            elif action == "repeat_block" and self.should_execute():
                self._execute_repeat(args, instr)
            elif action == "foreach" and self.should_execute():
                self._execute_foreach(args, instr)
            elif action == "call" and self.should_execute():
                self._execute_call(args, instr)
            elif action == "if_complex":
                self._execute_complex_if(args, instr)
            elif action == "if_bool" and self.should_execute():
                self._execute_if_bool(args, instr)
        except CLUError:
            raise
        except Exception as e:
            line_info = f" (Line {instr.line_number})" if hasattr(instr, 'line_number') else ""
            raise CLUError(f"Error in {action}: {e}{line_info}")

    def _execute_output(self, args, instr):
        expr = args[0].strip()
        parts = self._tokenize_expression(expr)
        value = self.evaluate_expression(parts)
        print(self._to_string(value))

    def _execute_if_bool(self, args, instr):
        """Execute a boolean variable if statement"""
        var_name = args[0]

        # Handle boolean literals directly
        if var_name == "True":
            self.execution_stack.append("if-True")
            return
        elif var_name == "False":
            self.execution_stack.append("if-False")
            return

        # For variables, evaluate and convert to boolean
        try:
            tokens = self._tokenize_expression(var_name)
            value = self.evaluate_expression(tokens)
            result = bool(value)
            self.execution_stack.append("if-True" if result else "if-False")
        except CLUNameError:
            # If it's not a variable, try evaluating it as an expression
            raise CLUNameError(f"Variable or expression '{var_name}' not recognized")


    def _execute_assign(self, args, instr):
        var, expr = args
        value = self.evaluate_expression(expr)
        self.variables[var] = value

    def _execute_if(self, args, instr):
        result = self.evaluate_condition(*args)
        self.execution_stack.append("if-True" if result else "if-False")

    def _execute_otherwise(self, instr):
        if not self.execution_stack:
            raise CLUError("'otherwise' without matching 'if'")
        prev = self.execution_stack.pop()
        self.execution_stack.append("otherwise" if prev == "if-False" else "skip")

    def _execute_end(self, instr):
        if self.execution_stack:
            self.execution_stack.pop()

    def _execute_repeat(self, args, instr):
        var, op, val, body = args
        max_iterations = 10000
        iterations = 0

        while self.evaluate_condition(var, op, val):
            if iterations >= max_iterations:
                raise CLUError(f"Infinite loop detected (over {max_iterations} iterations)")
            for sub_instr in body:
                self.execute_instruction(sub_instr)
            iterations += 1

     # complexIF
    def _execute_complex_if(self, args, instr):
        """Execute a complex if statement with boolean operators"""
        condition = args[0]
        result = self._evaluate_complex_condition(condition)
        self.execution_stack.append("if-True" if result else "if-False")

    def _evaluate_complex_condition(self, condition: str) -> bool:
        """Evaluate a boolean expression with AND/OR operators"""
        # Simple implementation - could be enhanced for more complex expressions
        if " and " in condition:
            parts = condition.split(" and ")
            return all(self._evaluate_simple_condition(part.strip()) for part in parts)
        elif " or " in condition:
            parts = condition.split(" or ")
            return any(self._evaluate_simple_condition(part.strip()) for part in parts)
        else:
            return self._evaluate_simple_condition(condition)

    def _evaluate_simple_condition(self, condition: str) -> bool:
        """Evaluate a simple boolean condition"""
        if condition.strip() == "True":
            return True
        elif condition.strip() == "False":
            return False

        # Handle "not" operator
        if condition.strip().startswith("not "):
            inner = condition.strip()[4:].strip()
            return not self._evaluate_simple_condition(inner)

        # Parse and evaluate regular conditions
        tokens = self._tokenize_expression(condition)
        if len(tokens) == 1:
            # Single token (variable or literal)
            value = self.evaluate_expression(tokens)
            return bool(value)
        elif len(tokens) >= 3:
            # Regular comparison
            if tokens[1] in ["greater", "less", "equal", "greater_equal", "less_equal", "not_equal"]:
                left = " ".join(tokens[:1])
                op = tokens[1]
                right = " ".join(tokens[2:])
                return self.evaluate_condition(left, op, right)

        raise CLUError(f"Invalid condition: {condition}")

#Foreach

    def _execute_foreach(self, args, instr):
        var, list_name, body = args

        if list_name not in self.variables:
            raise CLUNameError(f"Variable '{list_name}' not defined")

        list_val = self.variables[list_name]
        if not isinstance(list_val, list):
            raise CLUTypeError(f"'{list_name}' is not a list, it's a {type(list_val).__name__}")
        for item in list_val:
            self.variables[var] = item
            for sub_instr in body:
                self.execute_instruction(sub_instr)

    def _execute_call(self, args, instr):
        name = args[0]
        call_args = args[1:]

        if name not in self.functions:
            raise CLUNameError(f"Function '{name}' not defined")

        func = self.functions[name]
        if len(call_args) != len(func.params):
            raise CLUError(f"Function '{name}' expects {len(func.params)} arguments, got {len(call_args)}")

        # Save current variable state
        saved_vars = self.variables.copy()

        # Set parameter values
        for param, arg in zip(func.params, call_args):
            tokens = self._tokenize_expression(arg)
            self.variables[param] = self.evaluate_expression(tokens)

        # Execute function body
        for sub_instr in func.body:
            self.execute_instruction(sub_instr)

        # Restore variable state
        self.variables = saved_vars

    def _tokenize_expression(self, expr: str) -> List[str]:
        """Tokenize an expression string using the same pattern as main tokenizer"""
        # Use the same pattern as the main tokenizer to ensure consistency
        return re.findall(r'\w+\[[^\]]+\]|\'.*?\'|".*?"|\d+\.\d+|\d+|\w+|[^\s\w]', expr)

    @property
    def token_pattern(self):
        return r'\d+\.\d+|\w+\([^\)]+\)|\w+\[[^\]]+\]|->|\w+(?:/\w+)*|".*?"|\'.*?\'|\d+|\w+|[^\s\w]'

    def evaluate_expression(self, parts: List[str]) -> Any:
        if not parts:
            raise CLUError("Empty expression")

        #Boolean Support
        if len(parts) == 1:
            if parts[0] == "True":
                return True
            elif parts[0] == "False":
                return False

        # Handle list literals first
        if len(parts) >= 3 and len(parts) % 2 == 1:
            if all(parts[i] == ',' for i in range(1, len(parts), 2)):
                return self._parse_list_literal(parts)

        # Handle simple "function of variable" (3 parts exactly)
        if len(parts) == 3 and parts[1] == "of":
            return self._evaluate_builtin_function(parts[0], parts[2])

        # Handle single values (including floats)
        if len(parts) == 1:
            part = parts[0]
            # Handle floating point number
            if re.match(r'^\d+\.\d+$', part):
                return float(part)
            # Handle integer
            elif re.match(r'^\d+$', part):
                return int(part)
            # Handle string
            elif (part.startswith("'") and part.endswith("'")) or (part.startswith('"') and part.endswith('"')):
                return part[1:-1]
            # Handle variable
            elif part in self.variables:
                return self.variables[part]
            else:
                raise CLUNameError(f"Variable '{part}' not defined")

        # Use the expression parser for more complex expressions
        return self._parse_expression(parts, 0)[0]

    def _parse_expression(self, parts: List[str], pos: int) -> tuple[Any, int]:
        """Parse expression and return (result, new_position)"""

        # Parse first term
        result, pos = self._parse_term(parts, pos)

        # Handle binary operations
        while pos < len(parts) - 1:
            if parts[pos] in ['+', 'add', '-', 'subtract', '*', 'multiply', '/', 'divide']:
                op = parts[pos]
                right, pos = self._parse_term(parts, pos + 1)
                result = self._apply_operator(result, op, right)
            else:
                break

        return result, pos

    def _parse_term(self, parts: List[str], pos: int) -> tuple[Any, int]:
        """Parse a single term (variable, function call, or literal)"""

        if pos >= len(parts):
            raise CLUError("Unexpected end of expression")

        # Check for function call pattern
        if pos + 2 < len(parts) and parts[pos + 1] == "of":
            func_name = parts[pos]

            # Recursively parse the argument (could be another function call)
            arg_value, new_pos = self._parse_term(parts, pos + 2)

            if func_name in self.builtin_functions:
                result = self.builtin_functions[func_name](arg_value)
                return result, new_pos
            else:
                raise CLUNameError(f"Unknown function '{func_name}'")

        # Regular value
        value = self._evaluate_single_value(parts[pos])
        return value, pos + 1

    def _evaluate_mixed_binary_operations(self, parts: List) -> Any:
        """Handle binary operations with mixed types (some already evaluated)"""
        # Start with first part
        if isinstance(parts[0], str):
            result = self._evaluate_single_value(parts[0])
        else:
            result = parts[0]  # Already evaluated

        i = 1
        while i < len(parts) - 1:
            operator = str(parts[i])  # Ensure operator is string

            # Handle next operand
            if isinstance(parts[i + 1], str):
                operand = self._evaluate_single_value(parts[i + 1])
            else:
                operand = parts[i + 1]  # Already evaluated

            result = self._apply_operator(result, operator, operand)
            i += 2

        return result

    def _parse_list_literal(self, parts: List[str]) -> List[Any]:
        """Parse comma-separated list literal with mixed types"""
        elements = []
        for i in range(0, len(parts), 2):  # Skip commas
            if i < len(parts):
                part = parts[i]
                # Handle floating point numbers
                if re.match(r'^\d+\.\d+$', part):
                    elements.append(float(part))
                # Handle integers
                elif re.match(r'^\d+$', part):
                    elements.append(int(part))
                # Handle string literals
                elif (part.startswith("'") and part.endswith("'")) or (part.startswith('"') and part.endswith('"')):
                    elements.append(part[1:-1])
                # Handle variables
                elif part in self.variables:
                    elements.append(self.variables[part])
                else:
                    raise CLUNameError(f"Variable '{part}' not defined")
        return elements

    def _evaluate_builtin_function(self, func_name: str, arg_name: str) -> Any:
        """Evaluate built-in function call"""
        if func_name not in self.builtin_functions:
            raise CLUNameError(f"Unknown built-in function '{func_name}'")

        # IMPORTANT: Don't just evaluate as single token, use full expression evaluation
        arg_tokens = self._tokenize_expression(arg_name)
        arg_value = self.evaluate_expression(arg_tokens)
        return self.builtin_functions[func_name](arg_value)

    def _evaluate_binary_operations(self, parts: List[str]) -> Any:
        """Evaluate binary operations left to right"""
        result = self._evaluate_single_value(parts[0])

        i = 1
        while i < len(parts) - 1:
            operator = parts[i]
            operand = self._evaluate_single_value(parts[i + 1])
            result = self._apply_operator(result, operator, operand)
            i += 2

        return result

    def _evaluate_single_value(self, token: str) -> Any:
        """Evaluate a single token with proper boolean literal handling"""

        # Boolean literals - check these FIRST
        if token == "True":
            return True
        elif token == "False":
            return False

        # Floating point numbers - check next
        if re.match(r'^\d+\.\d+$', token):
            return float(token)

        # Array indexing
        match = re.fullmatch(r'(\w+)\[(.+)\]', token)
        if match:
            return self._evaluate_array_access(match.group(1), match.group(2))

        # String literals
        if (token.startswith("'") and token.endswith("'")) or (token.startswith('"') and token.endswith('"')):
            return token[1:-1]

        # Integer literals
        if re.match(r'^\d+$', token):
            return int(token)

        # Variable lookup - must come AFTER checking for literals
        if token in self.variables:
            return self.variables[token]

        # Special case for null/none value
        if token.lower() in ["null", "none"]:
            return None

        # Variable not found
        raise CLUNameError(f"Variable '{token}' is not defined")

    def _evaluate_array_access(self, array_name: str, index_expr: str) -> Any:
        """Evaluate array[index] access"""
        if array_name not in self.variables:
            raise CLUNameError(f"Variable '{array_name}' not defined")

        array_value = self.variables[array_name]
        if not isinstance(array_value, list):
            raise CLUTypeError(f"'{array_name}' is not a list")

        # Evaluate index expression
        index_tokens = self._tokenize_expression(index_expr)
        index_value = self.evaluate_expression(index_tokens)

        if not isinstance(index_value, int):
            raise CLUTypeError(f"Array index must be integer, got {type(index_value).__name__}")

        # Convert from 1-based to 0-based indexing
        index_value -= 1

        try:
            return array_value[index_value]
        except IndexError:
            raise CLUIndexError(f"Index {index_value + 1} out of range for '{array_name}' (length {len(array_value)})")

    def _apply_operator(self, left: Any, op: str, right: Any) -> Any:
        """Apply binary operator"""
        if op in ("+", "add"):
            # For string concatenation, convert both operands to strings
            if isinstance(left, str) or isinstance(right, str):
                return self._to_string(left) + self._to_string(right)
            return left + right
        elif op in ("-", "subtract"):
            return left - right
        elif op in ("*", "multiply"):
            return left * right
        elif op in ("/", "divide"):
            if right == 0:
                raise CLUError("Division by zero")
            return left // right if isinstance(left, int) and isinstance(right, int) else left / right
        else:
            raise CLUError(f"Unknown operator '{op}'")

    def _apply_not(self, value):
        """Apply logical NOT operator"""
        if isinstance(value, bool):
            return not value
        raise CLUTypeError(f"Cannot apply 'not' to {type(value).__name__}")

    def _to_bool(self, value: Any) -> bool:
        """Convert value to boolean"""
        if isinstance(value, bool):
            return value
        elif isinstance(value, (int, float)):
            return value != 0
        elif isinstance(value, str):
            return value != ""
        elif isinstance(value, list):
            return len(value) > 0
        return bool(value)

    def evaluate_condition(self, left: str, op: str, right: str) -> bool:
        """Evaluate conditional expression"""
        # Handle special case for logical operators
        if op == "and":
            return self.evaluate_expression(self._tokenize_expression(left)) and \
                self.evaluate_expression(self._tokenize_expression(right))
        elif op == "or":
            return self.evaluate_expression(self._tokenize_expression(left)) or \
                self.evaluate_expression(self._tokenize_expression(right))

        # Continue with existing code for >, <, ==, etc.
        left_tokens = self._tokenize_expression(left)
        right_tokens = self._tokenize_expression(right)

        left_val = self.evaluate_expression(left_tokens)
        right_val = self.evaluate_expression(right_tokens)

        operators = {
            "greater": lambda a, b: a > b,
            "less": lambda a, b: a < b,
            "equal": lambda a, b: a == b,
            "greater_equal": lambda a, b: a >= b,
            "less_equal": lambda a, b: a <= b,
            "not_equal": lambda a, b: a != b,
        }

        if op not in operators:
            raise CLUError(f"Unknown comparison operator '{op}'")

        return operators[op](left_val, right_val)