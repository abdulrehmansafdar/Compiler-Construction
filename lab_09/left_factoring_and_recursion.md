
# Left Factoring and Left Recursion Removal for Pascal Subset CFG

**Name:** Abdul Rehman  
**Roll Number:** 2023-CS-20

This document shows how to apply left factoring and remove left recursion from the subset Pascal grammar (see `subset_pascal_cfg.md`).

---

## 1. Formula Reference

### Left Recursion Removal
Given:
```
A → Aα | β
```
Transform to:
```
A  → βA'
A' → αA' | ε
```

### Left Factoring
Given:
```
A → αβ1 | αβ2
```
Transform to:
```
A  → αA'
A' → β1 | β2
```

---

## 2. Example Applications to Pascal CFG

### (A) Remove Left Recursion

#### Example: `identifier_list`
Original:
```
identifier_list → id
                | identifier_list , id
```
This is **left recursive** (identifier_list on the left of |).

**Remove left recursion:**
```
identifier_list → id identifier_list'
identifier_list' → , id identifier_list' | ε
```

#### Example: `declarations`
Original:
```
declarations → declarations var identifier_list : type ;
             | ε
```
**Remove left recursion:**
```
declarations → ε declarations'
declarations' → var identifier_list : type ; declarations' | ε
```

### (B) Left Factoring

#### Example: `statement`
Original:
```
statement → variable assignop expression
          | procedure_statement
          | compound_statement
          | if expression then statement else statement
          | while expression do statement
```
Suppose two productions start with the same prefix (e.g., `if expression then statement`).

If you had:
```
S → if E then S else S
  | if E then S
```
Left factor:
```
S → if E then S S'
S' → else S | ε
```

#### Example: `simple_expression`
Original:
```
simple_expression → term
                 | sign term
                 | simple_expression addop term
```
The third production is left recursive. Remove left recursion:
```
simple_expression → sign term simple_expression'
                 | term simple_expression'
simple_expression' → addop term simple_expression' | ε
```

---

## 3. Summary Table

| Non-terminal         | Original Rule(s)                                   | After Transformation                |
|---------------------|----------------------------------------------------|-------------------------------------|
| identifier_list     | id <br> identifier_list , id                       | id identifier_list' <br> identifier_list' → , id identifier_list' \| ε |
| declarations        | declarations var identifier_list : type ; <br> ε   | ε declarations' <br> declarations' → var identifier_list : type ; declarations' \| ε |
| simple_expression   | term <br> sign term <br> simple_expression addop term | sign term simple_expression' <br> term simple_expression' <br> simple_expression' → addop term simple_expression' \| ε |
| statement           | ... (see above)                                    | ... (see above)                     |

---


---


## 4. All Rules: Left Recursion Removal and Left Factoring (Complete)

Below, every rule from the Pascal subset CFG is listed. Left recursion and left factoring are applied wherever possible.

### program
Original:
```
program → program id ( identifier_list ) ; declarations subprogram_declarations compound_statement
```
No left recursion or factoring needed.

### identifier_list
Original:
```
identifier_list → id
               | identifier_list , id
```
Transformed:
```
identifier_list → id identifier_list'
identifier_list' → , id identifier_list' | ε
```

### declarations
Original:
```
declarations → declarations var identifier_list : type ;
             | ε
```
Transformed:
```
declarations → declarations'
declarations' → var identifier_list : type ; declarations' | ε
```

### type
Original:
```
type → standard_type
     | array [ num .. num ] of standard_type
```
No left recursion or factoring needed.

### standard_type
Original:
```
standard_type → integer
              | real
```
No left recursion or factoring needed.

### subprogram_declarations
Original:
```
subprogram_declarations → subprogram_declarations subprogram_declaration ;
                        | ε
```
Transformed:
```
subprogram_declarations → subprogram_declarations'
subprogram_declarations' → subprogram_declaration ; subprogram_declarations' | ε
```

### subprogram_declaration
Original:
```
subprogram_declaration → subprogram_head declarations compound_statement
```
No left recursion or factoring needed.

### subprogram_head
Original:
```
subprogram_head → function id arguments : standard_type ;
                | procedure id arguments ;
```
Left factoring (common prefix `id arguments`):
```
subprogram_head → function id arguments subprogram_head'
               | procedure id arguments ;
subprogram_head' → : standard_type ;
```
Or, since only the suffix differs, you may keep as is for recursive descent.

### arguments
Original:
```
arguments → ( parameter_list )
          | ε
```
No left recursion or factoring needed.

### parameter_list
Original:
```
parameter_list → identifier_list : type
               | parameter_list ; identifier_list : type
```
Transformed:
```
parameter_list → identifier_list : type parameter_list'
parameter_list' → ; identifier_list : type parameter_list' | ε
```

### compound_statement
Original:
```
compound_statement → begin optional_statements end
```
No left recursion or factoring needed.

### optional_statements
Original:
```
optional_statements → statement_list
                    | ε
```
No left recursion or factoring needed.

### statement_list
Original:
```
statement_list → statement
               | statement_list ; statement
```
Transformed:
```
statement_list → statement statement_list'
statement_list' → ; statement statement_list' | ε
```

### statement
Original:
```
statement → variable assignop expression
          | procedure_statement
          | compound_statement
          | if expression then statement else statement
          | while expression do statement
```
Left factoring for `if`:
```
statement → if expression then statement statement'
          | while expression do statement
          | variable assignop expression
          | procedure_statement
          | compound_statement
statement' → else statement | ε
```

### variable
Original:
```
variable → id
         | id [ expression ]
```
Left factoring (common prefix `id`):
```
variable → id variable'
variable' → [ expression ] | ε
```

### procedure_statement
Original:
```
procedure_statement → id
                    | id ( expression_list )
```
Left factoring (common prefix `id`):
```
procedure_statement → id procedure_statement'
procedure_statement' → ( expression_list ) | ε
```

### expression_list
Original:
```
expression_list → expression
                | expression_list , expression
```
Transformed:
```
expression_list → expression expression_list'
expression_list' → , expression expression_list' | ε
```

### expression
Original:
```
expression → simple_expression
           | simple_expression relop simple_expression
```
Left factoring (common prefix `simple_expression`):
```
expression → simple_expression expression'
expression' → relop simple_expression | ε
```

### simple_expression
Original:
```
simple_expression → term
                 | sign term
                 | simple_expression addop term
```
Transformed:
```
simple_expression → sign term simple_expression'
                 | term simple_expression'
simple_expression' → addop term simple_expression' | ε
```

### term
Original:
```
term → factor
     | term mulop factor
```
Transformed:
```
term → factor term'
term' → mulop factor term' | ε
```

### factor
Original:
```
factor → id
       | id ( expression_list )
       | num
       | ( expression )
       | not factor
```
Left factoring (common prefix `id`):
```
factor → id factor'
       | num
       | ( expression )
       | not factor
factor' → ( expression_list ) | ε
```

### sign
Original:
```
sign → +
     | -
```
No left recursion or factoring needed.

---

All rules from the subset Pascal CFG are now included and transformed where necessary for recursive descent parsing.

---

*Prepared for lab_09: left factoring and left recursion removal for Pascal CFG.*

*Prepared for lab_09: left factoring and left recursion removal for Pascal CFG.*
