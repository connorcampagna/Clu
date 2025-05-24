
![Language](https://img.shields.io/badge/language-CLU-blueviolet)
![Status](https://img.shields.io/badge/status-Experimental-orange)
![License](https://img.shields.io/badge/license-CLUED-green)
![Made with](https://img.shields.io/badge/made%20with-Python-blue)

# CLU Language Documentation (v1.10)

---

### Overview

**CLU** is an English-like scripting language with a minimal syntax and an easy-to-read interpreter. Every variable **must** be declared with `var`, string literals are called **chars** (single-quoted), and you get:

- integer and floating-point math (`add`, `subtract`, `multiply`, `divide`)
- boolean logic (`True`, `False`, `and`, `or`, `not`)
- char concatenation with `+`
- comma-separated **list literals** with mixed types
- `if` / `otherwise` / `end` conditionals with complex boolean expressions
- `repeat … end` loops
- `foreach … in … end` iteration
- functions (`function name -> p1/p2` … `end`)
- `output` of variables, literals (ints, floats, chars, booleans, lists) or undeclared valid literals
- built-in functions for lists, types, and conversions
- `#` for comments

---

## Basic Concepts

| Feature                    | Syntax example                                                  |
|----------------------------|----------------------------------------------------------------|
| **Variable declaration**   | `var x is 5`<br>`var name is 'connor'`<br>`var pi is 3.14`<br>`var flag is True` |
| **Re-assignment**          | `var x is x add 1`                                              |
| **Output**                 | `output x`<br>`output 'hello'`<br>`output 1,2,3`<br>`output True` |
| **Integer addition**       | `var s is 2 add 3`                                              |
| **Float operations**       | `var area is pi multiply r multiply r`                          |
| **Boolean operations**     | `var result is a greater b and c less d`                       |
| **Char concatenation**     | `var t is 'a' + 'b'`                                           |
| **List literal**           | `var mixed is 2,4,'hi',8,True,3.14`                            |
| **List Indexing**          | `var a is nums[i]`                                              |
| **Conditionals**           | `if x greater 3 otherwise end`<br>`if flag and count less 10`   |
| **Loops**                  | `repeat i less 5`<br>`foreach item in list`                    |
| **Functions**              | `function sum_to_n -> n`                                        |
| **Comments**               | `# this is a comment`                                           |
| **Built-in Functions**     | `len of list`<br>`str of 42`<br>`bool of 0`                    |

---

## Example Programs

### 1) Variables & Output
```clu
var x is 5
var pi is 3.14
var flag is True
output x
output pi
output flag
output 42           # direct integer literal
output 3.14159      # direct float literal
output 'hi'         # direct char literal
output True         # direct boolean literal
output 1,2,3        # direct list literal

```
### 2) Chaining & Operations
```clu
# numeric chaining with `add`
var total is 1 add 2 add 3 add 4
output total        # → 10

# char concatenation with `+`
var part1 is 'Hello'
var part2 is ', '
var part3 is 'world'
var greeting is part1 + part2 + part3 + '!'
output greeting     # → Hello, world!

# floating point operations
var radius is 5.0
var area is 3.14159 multiply radius multiply radius
output area         # → 78.53975
```
### 3) Mixed Type Lists
```clu
var mixed is 2,3,'apple',7.5,True
output mixed        # → [2, 3, 'apple', 7.5, True]
output mixed[3]     # → 7.5 (indexing is 1-based)
```
### 4) Boolean Logic & Condtionals 
```clu
var x is 5
var is_valid is True

# Simple condition
if x greater 2
    output 'x > 2'
otherwise
    output 'x ≤ 2'
end

# Boolean variable condition
if is_valid
    output 'Valid!'
end

# Complex boolean expression
if x greater 2 and x less 10 and is_valid
    output 'x is between 2 and 10, and is valid'
end

# Boolean negation
if not is_valid
    output 'Not valid!'
end
```
### 5) Loops
```clu
# Simple counter loop
var i is 1
repeat i less_equal 5
    output i
    var i is i add 1
end
# prints 1 2 3 4 5

# Foreach loop with mixed list
var items is 'apple','banana',3,'orange',True
foreach item in items
    output 'Item: ' + str of item
end
```
### 6) Functions & Recursion 
```clu
function factorial -> n
    var res is 1
    var i is 1
    repeat i less_equal n
        var res is res multiply i
        var i is i add 1
    end
    output res
end

factorial 6         # → 720

```

### 7) Built In Functions 
```clu
# List operations
var numbers is 1,2,3,4,5
output sum of numbers       # → 15
output max of numbers       # → 5
output min of numbers       # → 1
output len of numbers       # → 5
output average of numbers   # → 3
output first of numbers     # → 1
output last of numbers      # → 5

# Type conversion
var num_str is str of 42    # → '42'
var num_int is int of '42'  # → 42
var num_float is float of '3.14'  # → 3.14
var flag is bool of 1       # → True

# Boolean functions
var values is True,False,True
output all of values        # → False
output any of values        # → True
output is_bool of True      # → True

# Utility functions
output type of 42           # → 'int'
output type of 'hello'      # → 'str'
output empty of ''          # → True
output contains of 'hello', 'e'  # → True

``` 
## Syntax Rules

- **`var NAME is EXPR`**: declare or re-declare a variable.
- **`var NAME is EXPR`**: re-assignment of an existing var, still must use var.
- **`'chars'`**: single-quoted string literals.
- **`INT`**: decimal integer literal.
- **`FLOAT`**: decimal floating-point literal (e.g., `3.14`).
- **`True`**, **`False`**: boolean literals.
- **`LIST`**: comma-separated items of any type (`1,2,'hi',4.5,True`).
- **`output X`**: prints a var, char, int, float, boolean, list, or valid literal.
- **`add`**, **`subtract`**, **`multiply`**, **`divide`**: numeric operations.
- **`+`**: char concatenation only.
- **`if VAR CMP VAR`** … **`otherwise`** … **`end`**: conditionals.
- **`if BOOL_EXPR`**: conditionals with boolean expressions.
- **`and`**, **`or`**, **`not`**: boolean operators.
- **`repeat VAR CMP VAL`** … **`end`**: loops.
- **`foreach VAR in LIST`** … **`end`**: iteration loops.
- **`function NAME -> p1/p2`** … **`end`**: define functions.
- **`NAME ARG1 ARG2`**: call a function.
- **`# …`**: comments to end of line.

---

## Comparison Operators

- **`greater`**: `>`
- **`less`**: `<`
- **`equal`**: `==`
- **`greater_equal`**: `>=`
- **`less_equal`**: `<=`
- **`not_equal`**: `!=`

---

## Built-in Functions

### List Operations
- **`sum`**: Sum of list elements
- **`max`**: Maximum value in a list
- **`min`**: Minimum value in a list
- **`len`**: Length of a list or string
- **`sorted`**: Sorted version of a list
- **`reversed`**: Reversed version of a list
- **`average`**: Average of list elements
- **`first`**: First element of a list
- **`last`**: Last element of a list
- **`empty`**: Check if a list or string is empty

### Type Conversion
- **`str`**: Convert to string
- **`int`**: Convert to integer
- **`float`**: Convert to float
- **`bool`**: Convert to boolean

### Boolean Functions
- **`all`**: Check if all elements in a list are True
- **`any`**: Check if any element in a list is True
- **`is_bool`**: Check if a value is a boolean

### Utility Functions
- **`type`**: Get the type name of a value
- **`contains`**: Check if an item is in a container

---

## Future Features (Planned)

- return values from functions
- modules / imports
- dictionaries / maps
- error handling (try/catch)
- file I/O

---

## Project Info

- **Author:** Connor Campagna
- **GitHub:** https://github.com/connorcampagna/Clu
- **License:** CLUED
- **Status:** Beta (v0.1)
