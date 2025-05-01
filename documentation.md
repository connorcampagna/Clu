# CLU Language Documentation (v0.01)

---

### Overview

**CLU** is a tiny, English-like scripting language with a minimal syntax and an easy-to-read interpreter. Every variable **must** be declared with `var`, string literals are now called **chars** (single-quoted), and you get:

- integer math (`add`, `subtract`, `multiply`, `divide`)  
- char concatenation with `+`  
- comma-separated **list literals**  
- `if` / `otherwise` / `end` conditionals  
- `repeat … end` loops  
- functions (`function name -> p1/p2` … `end`)  
- `output` of variables, literals (ints, chars, lists) or undeclared valid literals  
- `#` for comments  

---

## Basic Concepts

| Feature                  | Syntax example                                      |
| ------------------------ | --------------------------------------------------- |
| **Variable declaration** | `var x is 5`<br>`var name is 'connor'`              |
| **Re-assignment**        | `x is x add 1`                                      |
| **Output**               | `output x`<br>`output 'hello'`<br>`output 1,2,3`   |
| **Integer addition**     | `var s is 2 add 3`                                  |
| **Char concatenation**   | `var t is 'a' + 'b'`                                |
| **List literal**         | `var nums is 2,4,6,8`                               |
| **Conditionals**         | 
if x greater 3
    output 'big'
otherwise
    output 'small'
end
``` |
| **Loops**                | ```clu
var i is 0
repeat i less 5
    output i
    var i is i add 1
end
``` |
| **Functions**            | ```clu
function sum_to_n -> n
    …  
end
sum_to_n 10
``` |
| **Comments**             | `# this is a comment`                               |

---

## Example Programs
```
### 1) Variables & Output
```clu
var x is 5
output x
output 42           # direct integer literal
output 'hi'         # direct char literal
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
```

### 3) Lists
```clu
var primes is 2,3,5,7,11
output primes       # → [2, 3, 5, 7, 11]
```

### 4) Conditionals
```clu
var x is 5

if x greater 2
    output 'x > 2'
otherwise
    output 'x ≤ 2'
end
```

### 5) Loops
```clu
var i is 1
repeat i less_equal 5
    output i
    var i is i add 1
end
# prints 1 2 3 4 5
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

### 7) Euclid’s GCD (recursive)
```clu
function gcd -> a/b
    if b equal 0
        output a
    otherwise
        var rem is a subtract (a divide b) multiply b
        gcd b rem
    end
end

gcd 270 192         # → 6
```

---

## Syntax Rules

- **`var NAME is EXPR`**: declare or re-declare a variable.  
- **`NAME is EXPR`**: re-assignment of an existing var.  
- **`'chars'`**: single-quoted string literals.  
- **`INT`**: decimal integer literal.  
- **`LIST`**: comma-separated ints (`1,2,3`).  
- **`output X`**: prints a var, char, int, list, or valid literal.  
- **`add`**, **`subtract`**, **`multiply`**, **`divide`**: integer ops.  
- **`+`**: char concatenation only.  
- **`if VAR CMP VAR`** … **`otherwise`** … **`end`**: conditionals.  
- **`repeat VAR CMP VAL`** … **`end`**: loops.  
- **`function NAME -> p1/p2`** … **`end`**: define functions.  
- **`NAME ARG1 ARG2`**: call a function.  
- **`# …`**: comments to end of line.  

---

## Future Features (Planned)

- return values from functions  
- built-in list indexing / length / append  
- modules / imports  
- richer datatypes (floats, booleans)  
- improved error messages & stack traces  

---

## Project Info

- **Author:** Connor Campagna  
- **GitHub:** https://github.com/connorcampagna/Clu  
- **License:** MIT  
- **Status:** Experimental (v0.01)  


