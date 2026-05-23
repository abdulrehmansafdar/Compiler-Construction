# LL(1) Parser vs Recursive Descent Parser - Lab 09 Quick Review

## Overview

Both parsers in lab_09 parse the **same Pascal-like grammar** (program declarations, subprograms, statements). They achieve the same goal but work completely differently.

---

## 1. How They Differ (Key Differences)

| Aspect | LL(1) Parser | Recursive Descent Parser |
|--------|-------------|-------------------------|
| **Approach** | Table-driven (uses parsing table) | Function-driven (uses recursive functions) |
| **Parsing Table** | Pre-computed from FIRST/FOLLOW sets | No table needed |
| **Decision Making** | Look at stack top + current token → look up table | Look at current token → call appropriate function |
| **Grammar Requirements** | Must be left-factored, no left recursion | Same (left-factored, no left recursion) |
| **Implementation** | Algorithm 4.34 (dragon book) | Direct translation of grammar to code |

---

## 2. How They Work

### LL(1) Parser (ll1_parser.py)

```
STACK                              INPUT
$ program                          PROGRAM ID ... $

1. Look at stack top (program) and current token (PROGRAM)
2. Look up parsing table M[program, PROGRAM]
3. Table says: program -> PROGRAM ID SEMI ... (production)
4. Pop 'program', push RHS in reverse order
5. Repeat until stack matches input
```

**Step-by-step (Algorithm 4.34):**
1. Initialize stack with `$` and start symbol `program`
2. While stack not empty:
   - If top of stack = current token → pop, advance
   - Else if top is terminal but doesn't match → ERROR
   - Else if no rule in table M[top, token] → ERROR
   - Else pop top, push production RHS reversed

**Key Code (ll1_parser.py:89-150):**
```python
stack = ['$', 'program']  # Step 1
while stack:
    top = stack[-1]
    if top == input_token:           # Match
        stack.pop()
        pos += 1
    elif (top, input_token) in parse_table:  # Expand
        prod = parse_table[(top, input_token)]
        stack.pop()
        # Push RHS reversed
        for sym in prod.split()[::-1]:
            stack.append(sym)
    else:
        return False  # ERROR
```

### Recursive Descent Parser (recursive_descent_parser.py)

```
INPUT: PROGRAM ID ... $

1. Call program()
2. program() does:
   - match('PROGRAM')
   - match('ID')
   - if LPAREN: call identifier_list()
   - match('SEMI')
   - call declarations()
   - call subprogram_declarations()
   - call compound_statement()
3. Each function handles its own grammar rule
4. If all matches succeed → parse successful
```

**Step-by-step:**
1. Start with `parse()` which calls `program()`
2. Each non-terminal has its own function (e.g., `declarations()`, `statement()`)
3. Functions call `match(token_type)` to consume expected tokens
4. Functions call other functions for nested non-terminals

**Key Code (recursive_descent_parser.py:25-44):**
```python
def parse(self):
    self.program()  # Start parsing
    if self.errors:
        return False
    return True

def program(self):
    self.match('PROGRAM')
    self.match('ID')
    if self.current[0] == 'LPAREN':
        self.identifier_list()
        self.match('RPAREN')
    self.match('SEMI')
    self.declarations()
    ...
```

---

## 3. How Error Handling Works

### LL(1) Parser Error Handling

**Location:** `ll1_parser.py:116-125`

```python
# Two types of errors:
# 1. Terminal mismatch
if top in self.terminals and top != input_token:
    print(f"ERROR: Terminal mismatch - expected {top}, got {input_token}")
    return False

# 2. No rule in parsing table
elif (top, input_token) not in self.parse_table:
    print(f"ERROR: No rule M[{top}, {input_token}]")
    return False
```

**Error handling is PASSIVE** - parser stops at first error, no recovery.

### Recursive Descent Parser Error Handling

**Location:** `recursive_descent_parser.py:17-23`

```python
def match(self, token_type):
    if self.current[0] == token_type:
        self.advance()
        return True
    else:
        self.errors.append(f"Expected {token_type}, got {self.current[0]}")
        return False  # Records error but continues
```

**Error handling is ACTIVE** - collects all errors in `self.errors` list and reports at end:
```python
def parse(self):
    self.program()
    if self.errors:
        for e in self.errors:
            print(f"Error: {e}")
        return False
```

**Key difference:** RD can continue parsing after error (collects multiple errors), LL(1) stops immediately.

---

## 4. How They Parse From Your Code

### First, compute FIRST and FOLLOW sets (first_follow.py)

Both parsers need FIRST/FOLLOW to work:

```python
computer = FirstFollowComputer(grammar)
computer.compute()
# FIRST(program) = {PROGRAM}
# FOLLOW(program) = {$}
```

### LL(1) Parsing Flow

```
Grammar → FIRST/FOLLOW → Parsing Table → Parse Input
              ↓                ↓              ↓
        first_follow.py  ll1_parser.py   parse() method
```

**In ll1_parser.py:54-70:**
1. For each production, compute FIRST of RHS
2. Add production to table M[non-terminal, terminal]
3. For epsilon productions, use FOLLOW set

### Recursive Descent Parsing Flow

```
Grammar → Functions (one per non-terminal) → Parse Input
              ↓                               ↓
        recursive_descent_parser.py    parse() method
```

**In recursive_descent_parser.py:34-214:**
1. Each non-terminal → one function (program, declarations, statement, etc.)
2. Each function uses lookahead (self.current) to decide which production to use
3. Uses FIRST sets implicitly (checks if token is in expected set)

---

## Summary Table for Quick Recall

| Feature | LL(1) | Recursive Descent |
|---------|-------|-------------------|
| **Parsing method** | Table lookup | Function calls |
| **Data structure** | Stack + Table | Call stack (recursive) |
| **Grammar prep needed** | First/Follow + Table build | Just left-factor |
| **Error detection** | Immediate (stops) | Deferred (collects all) |
| **Code structure** | One parse() function | Many functions |
| **Lookahead** | Uses table | Uses if/elif checks |

---

## Quick Answer for Evaluation

**"What is the difference between LL(1) and Recursive Descent parser?"**

> LL(1) is a **table-driven** parser that uses a pre-computed parsing table to decide which production to use. It maintains an explicit stack and makes decisions by looking up M[non-terminal, current-token]. Recursive Descent is a **function-driven** parser where each non-terminal becomes a function, and decisions are made through if/elif checks on the current token. Both require left-factored grammars with no left recursion. LL(1) stops at first error, while Recursive Descent can collect multiple errors before stopping.