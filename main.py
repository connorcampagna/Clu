# CLU Language Integration Script
# This script ties together the enhanced interpreter with the IDE
# Written By Connor Campagna @ 2025
# UOFG STUDENT

import sys
import os
from pathlib import Path


def setup_clu_environment():
    """Set up the CLU development environment"""
    print("Setting up CLU development environment...")

    # Create example CLU programs
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)

    # Basic example
    basic_example = """# Basic CLU Example - Variables and Output
var name is 'Connor'
var age is 21
var university is 'University of Glasgow'

output 'Hello, my name is ' + name
output 'I am ' + str of age + ' years old'
output 'I study at ' + university
"""

    # Lists and functions example
    lists_example = """# CLU Example - Lists and Functions
var numbers is 1,2,3,4,5,6,7,8,9,10
var fruits is 'apple','banana','cherry','date'

output 'Numbers: ' + str of numbers
output 'Sum of numbers: ' + str of sum of numbers
output 'Average: ' + str of average of numbers
output 'First fruit: ' + first of fruits
output 'Number of fruits: ' + str of len of fruits

function describe_list -> items
    output 'This list has ' + str of len of items + ' items'
    output 'First item: ' + str of first of items
    output 'Last item: ' + str of last of items
end

describe_list numbers
describe_list fruits
"""

    # Control flow example
    control_example = """# CLU Example - Control Flow
var x is 1

# Count to 5
repeat x less_equal 5
    output 'Count: ' + str of x
    var x is x add 1
end

# Check numbers
var test_numbers is 1,5,10,15,20

foreach num in test_numbers
    if num greater 10
        output str of num + ' is a big number'
    otherwise
        output str of num + ' is a small number'
    end
end

# Function with conditionals
function grade_score -> score
    if score greater_equal 90
        output 'Grade A - Excellent!'
    otherwise
        if score greater_equal 80
            output 'Grade B - Good work!'
        otherwise
            if score greater_equal 70
                output 'Grade C - Satisfactory'
            otherwise
                output 'Grade F - Needs improvement'
            end
        end
    end
end

var scores is 95,85,75,65
foreach score in scores
    output 'Score ' + str of score + ':'
    grade_score score
end
"""

    # Advanced features example
    advanced_example = """# CLU Example - Advanced Features
var mixed_data is 'hello',42,'world',100

output 'Processing mixed data:'
foreach item in mixed_data
    output 'Item: ' + str of item + ' (type: ' + type of item + ')'
end

# String and number conversion
var text_numbers is '10','20','30'
var converted is empty of converted

# Note: This would require list building functionality
output 'Text numbers: ' + str of text_numbers

# Working with different data types
var text is 'CLU Language'
var number is 2025
var decimal is 3.14159

output 'Text length: ' + str of len of text
output 'Number as text: ' + str of number
output 'Decimal as integer: ' + str of int of decimal

# Complex calculations
var base is 10
var exponent is 3
var result is base

repeat exponent greater 1
    var result is result multiply base
    var exponent is exponent subtract 1
end

output str of base + ' cubed is ' + str of result
"""

    # Write example files
    examples = {
        "01_basic.clu": basic_example,
        "02_lists_functions.clu": lists_example,
        "03_control_flow.clu": control_example,
        "04_advanced.clu": advanced_example
    }

    for filename, content in examples.items():
        example_path = examples_dir / filename
        with open(example_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"Created example: {filename}")

    # Create CLU language reference
    reference_content = """# CLU Language Reference

## Variables
```
var variable_name is value
var numbers is 1,2,3,4,5
var text is 'Hello World'
```

## Output
```
output 'Hello World'
output variable_name
output sum of numbers
```

## Functions
```
function function_name -> param1/param2
    # function body
end
```

## Control Flow

### Conditionals
```
if condition
    # code
otherwise
    # code
end
```

### Loops
```
repeat variable operator value
    # code
end

foreach item in list
    # code
end
```

## Operators
- Comparison: greater, less, equal, greater_equal, less_equal, not_equal
- Math: add, subtract, multiply, divide
- String: + (concatenation)

## Built-in Functions
- sum of list
- max of list
- min of list
- len of list/string
- sorted of list
- reversed of list
- average of list
- first of list
- last of list
- str of value (convert to string)
- int of value (convert to integer)
- float of value (convert to decimal)
- type of value (get type name)
- empty of list/string (check if empty)

## Examples
See the examples folder for comprehensive examples of CLU programs.
"""

    with open("CLU_Reference.md", 'w', encoding='utf-8') as f:
        f.write(reference_content)
    print("Created language reference: CLU_Reference.md")


def create_launcher_script():
    """Create a launcher script for the CLU IDE"""
    launcher_content = """#!/usr/bin/env python3
# CLU IDE Launcher
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_clu_ide import CluIde
    from PySide6.QtWidgets import QApplication

    if __name__ == "__main__":
        app = QApplication(sys.argv)
        app.setStyle("Fusion")

        window = CluIde()
        window.show()

        sys.exit(app.exec())

except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure PySide6 is installed: pip install PySide6")
    sys.exit(1)
"""

    with open("launch_clu_ide.py", 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    print("Created launcher script: launch_clu_ide.py")


def create_command_line_runner():
    """Create a command-line runner for CLU files"""
    runner_content = """#!/usr/bin/env python3
# CLU Command Line Runner
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Run CLU programs from command line')
    parser.add_argument('file', help='CLU file to execute')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug mode')

    args = parser.parse_args()

    # Check if file exists
    clu_file = Path(args.file)
    if not clu_file.exists():
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)

    # Read the CLU file
    try:
        with open(clu_file, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Import and run the enhanced interpreter
    try:
        from enhanced_interpreter import Parser, Interpreter, CLUError

        if args.verbose:
            print(f"Running CLU file: {clu_file}")
            print("-" * 40)

        # Parse and execute
        lines = code.split('\\n')
        parser = Parser()
        program = parser.parse(lines)

        interpreter = Interpreter()
        interpreter.load_program(program)

        if args.debug:
            print("Debug: Program parsed successfully")
            print(f"Debug: Found {len(program.functions)} functions")
            print(f"Debug: Found {len(program.instructions)} main instructions")
            print("-" * 40)

        interpreter.run()

        if args.verbose:
            print("-" * 40)
            print("Execution completed successfully")

    except CLUError as e:
        print(f"CLU Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Runtime Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
"""

    with open("run_clu.py", 'w', encoding='utf-8') as f:
        f.write(runner_content)
    print("Created command-line runner: run_clu.py")


def create_project_readme():
    """Create a comprehensive README for the project"""
    readme_content = """# CLU Programming Language

CLU is an educational programming language designed for learning programming concepts with natural, English-like syntax.

## Features

- **Natural Syntax**: Write code that reads like English
- **Educational Focus**: Perfect for teaching programming concepts
- **Type Safety**: Built-in type checking and conversion
- **Interactive IDE**: Full-featured development environment
- **Comprehensive**: Variables, functions, loops, conditionals, and more

## Installation

1. Install Python 3.8 or higher
2. Install PySide6 for the IDE:
   ```bash
   pip install PySide6
   ```

## Usage

### Using the IDE
```bash
python launch_clu_ide.py
```

### Command Line
```bash
python run_clu.py example.clu
```

### Debug Mode
```bash
python run_clu.py -d -v example.clu
```

## Language Syntax

### Variables
```clu
var name is 'Connor'
var age is 21
var numbers is 1,2,3,4,5
```

### Output
```clu
output 'Hello World'
output name
output sum of numbers
```

### Functions
```clu
function greet -> name
    output 'Hello ' + name
end

greet 'Connor'
```

### Control Flow
```clu
if age greater 18
    output 'Adult'
otherwise
    output 'Minor'
end

repeat x less 10
    output x
    var x is x add 1
end

foreach item in list
    output item
end
```

## Examples

Check the `examples/` directory for comprehensive CLU programs demonstrating various features.

## Built-in Functions

- **Math**: sum, max, min, average
- **Lists**: len, sorted, reversed, first, last
- **Types**: str, int, float, type
- **Utilities**: empty, contains

## IDE Features

- Syntax highlighting
- Line numbers
- Variable inspection
- Integrated interpreter
- Dark/Light themes
- File management
- Error reporting with line numbers

## Project Structure

```
clu-language/
├── enhanced_interpreter.py    # Core interpreter
├── enhanced_clu_ide.py       # IDE interface
├── launch_clu_ide.py         # IDE launcher
├── run_clu.py                # Command-line runner
├── examples/                 # Example programs
├── CLU_Reference.md          # Language reference
└── README.md                 # This file
```

## Contributing

This project was created as an educational tool. Feel free to suggest improvements or report bugs.

## Author

Connor Campagna  
University of Glasgow Student  
2025

## License

Educational use. Created for learning purposes.
"""

    with open("README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("Created project README: README.md")


def main():
    """Main setup function"""
    print("=" * 50)
    print("CLU Language Development Environment Setup")
    print("=" * 50)

    setup_clu_environment()
    print()

    create_launcher_script()
    print()

    create_command_line_runner()
    print()

    create_project_readme()
    print()

    print("=" * 50)
    print("Setup Complete!")
    print("=" * 50)
    print()
    print("Next steps:")
    print("1. Install PySide6: pip install PySide6")
    print("2. Launch IDE: python launch_clu_ide.py")
    print("3. Try examples: python run_clu.py examples/01_basic.clu")
    print("4. Read the reference: CLU_Reference.md")
    print()
    print("Have fun programming in CLU!")


if __name__ == "__main__":
    main()