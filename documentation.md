# CLU Language Documentation

## Overview

**CLU** is a custom, minimalistic programming language designed for simple programs and learning interpreter construction.
It is inspired by English-like syntax, making it intuitive and easy to read.

---

## Basic Concepts

| Feature | Syntax |
|---------|--------|
| Variable Assignment | `x is 5` |
| Output | `output x` |
| Math Operations | `add`, `subtract`, `multiply`, `divide` |
| Conditionals | `if x greater 5`, `otherwise`, `end` |
| Loops | `repeat x less 10`, `end` |
| Functions | `function name -> param1/param2`, `end` |

---

## Example Programs

### Variables and Output

```clu
x is 5
output x
```

---

### Math

```clu
a is 10
b is 2
c is a add b
output c
```

---

### Conditions

```clu
x is 5

if x greater 2
    output x
otherwise
    output 0
end
```

---

### Loops

```clu
x is 0

repeat x less 5
    output x
    x is x add 1
end
```

✅ This will output:

```
0
1
2
3
4
```

---

### Functions

```clu
function counttofive -> start
    repeat start less 5
        output start
        start is start add 1
    end
end

counttofive 0
```

---

## Syntax Rules

- Use `is` to assign values.
- Loops must end with `end`.
- `repeat` supports conditions like `less`, `greater`, `equal`.
- Functions use `function name -> params` format.
- Function calls use simple space-separated arguments.
- `output` only prints variable values.

---

## Future Features (Planned)

- String support (e.g., `name is "Connor"`)
- Comment lines with `#`
- Return values from functions
- More advanced math and condition combinations

---

# Notes

- All variable names are case-sensitive.
- Variables must be assigned before they are used.
- Only integer math is supported currently.

---

# Project Info

- Author: Connor Campagna
- GitHub: [Clu Repository](https://github.com/connorcampagna/Clu)

---


