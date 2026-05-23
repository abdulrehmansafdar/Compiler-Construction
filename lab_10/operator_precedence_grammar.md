# Operator Precedence Grammar for a Subset of Pascal

All production rules below satisfy the two constraints of Operator Precedence Grammar:
1. **No ε-productions** (no null/empty right-hand side)
2. **No two adjacent non-terminals** on any right-hand side

---

## Program Structure

```
program  →  program id ( identifier_list ) ; program_block
```

## Program Block (replaces declarations + subprograms + compound body)

```
program_block  →  var identifier_list : type ; program_block
               |  function id : standard_type ; program_block
               |  function id ( parameter_list ) : standard_type ; program_block
               |  procedure id ; program_block
               |  procedure id ( parameter_list ) ; program_block
               |  begin statement_list end
               |  begin end
```

## Identifier List

```
identifier_list  →  id
                 |  identifier_list , id
```

## Type

```
type  →  standard_type
      |  array [ num .. num ] of standard_type
```

## Standard Type

```
standard_type  →  integer
               |  real
```

## Parameter List

```
parameter_list  →  identifier_list : type
                |  parameter_list ; identifier_list : type
```

## Compound Statement

```
compound_statement  →  begin statement_list end
                    |  begin end
```

## Statement List

```
statement_list  →  statement
                |  statement_list ; statement
```

## Statement

```
statement  →  variable assignop expression
           |  procedure_statement
           |  compound_statement
           |  if expression then statement else statement
           |  while expression do statement
```

## Procedure Statement

```
procedure_statement  →  id
                     |  id ( expression_list )
```

## Variable

```
variable  →  id
          |  id [ expression ]
```

## Expression List

```
expression_list  →  expression
                 |  expression_list , expression
```

## Expression

```
expression  →  simple_expression
            |  simple_expression relop simple_expression
```

## Simple Expression

```
simple_expression  →  term
                   |  simple_expression addop term
                   |  + term
                   |  - term
```

## Term

```
term  →  factor
      |  term mulop factor
```

## Factor

```
factor  →  id
        |  id ( expression_list )
        |  num
        |  ( expression )
        |  not factor
```

---

## Summary of Changes from Original CFG

| Change | Original | Modified |
|--------|----------|----------|
| Removed ε-productions | `declarations → ε`, `subprogram_declarations → ε`, `arguments → ε`, `optional_statements → ε` | Inlined / handled via alternative productions |
| Removed adjacent NTs: `sign term` | `simple_expression → sign term` | `simple_expression → + term \| - term` (uses terminals directly) |
| Removed adjacent NTs: `declarations subprogram_declarations compound_statement` | `program → ... ; declarations subprogram_declarations compound_statement` | `program → ... ; program_block` (single NT replaces the three) |
| Removed adjacent NTs in subprogram chain | `subprogram_declarations → subprogram_declarations subprogram_declaration ;`, `subprogram_declaration → subprogram_head declarations compound_statement` | Absorbed into `program_block` with terminals (`function`, `procedure`, etc.) separating every pair of NTs |
