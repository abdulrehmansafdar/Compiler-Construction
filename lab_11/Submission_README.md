# Lab 11 - Symbol Table Manager (Pascal CFG)

This folder contains the Lab 11 implementation for a symbol table manager based on a Pascal subset grammar. The goal is to move from pure syntax checking (previous labs) to semantic checks related to declarations, scope, and name use.

The implementation is designed to support your lab evaluation (viva) by clearly showing:
- how identifiers are stored,
- how scope is handled,
- how duplicate and undeclared errors are detected,
- and where parser integration should occur.

---

## 1. Lab Objectives and How This Work Addresses Them

### Objective 1: Explain the role of symbol table in compiler
The symbol table stores metadata for every identifier (name, kind, type, scope, declaration line). It is needed after lexical/syntax phases for semantic checks (duplicate declarations, undeclared uses) and later code generation support.

### Objective 2: Choose suitable data structure
This lab uses a hash table with separate chaining. It gives average-case O(1) insert and lookup, which is practical for compilers.

### Objective 3: Implement insert, lookup, delete
Implemented in `symbol_table.py`:
- `insert(name, kind, type_name, line)`
- `lookup(name)`
- `lookup_current(name)`
- `delete(name)` (current scope only)

### Objective 4: Handle nested scopes
Implemented using stack-like linked scopes:
- `begin_scope()` creates a new scope with parent pointer.
- `end_scope()` prints and pops current scope.

### Objective 5: Detect duplicate and undeclared names
- Duplicate declaration: `lookup_current` before `insert`.
- Undeclared use: `lookup` across current scope to global scope.

### Objective 6: Connect with parser
A semantic driver exists (`pascal_semantic_simulator.py`) showing parser-like semantic actions, and the recursive-descent parser from Lab 09 has been wired with symbol-table hooks for declarations, uses, and scope handling.

### Objective 7: Print symbol table for debugging
`end_scope()` prints a formatted table for the popped scope.

---

## 2. Implemented Files

- `symbol_table.py`
	- Core hash-based symbol table manager.
	- Contains data structures and all major operations.

- `task1_driver.py`
	- Dedicated in-lab Task 1 verification script.
	- Runs 10 inserts, 5 lookups (including misses), 3 deletes.

- `pascal_semantic_simulator.py`
	- A small Pascal-like semantic event runner.
	- Demonstrates declarations, uses, nested blocks, duplicate and undeclared checks.

- `test_cases/valid_nested.pas`
- `test_cases/duplicate_decl.pas`
- `test_cases/undeclared_use.pas`
- `test_cases/shadowing_valid.pas`
	- Test inputs for semantic behavior.

---

## 3. Data Structure Design

### 3.1 Symbol Entry
Each identifier is represented by `SymbolEntry` with:
- `entry_id`
- `name`
- `kind` (variable/function/parameter/program/array)
- `type_name` (integer/real/etc.)
- `scope_level`
- `line`
- `next` (for linked list chaining in same hash bucket)

### 3.2 Single Scope Table
Each scope is `ScopeTable`:
- `slots[211]`: fixed-size bucket array
- `parent`: pointer to enclosing scope
- `scope_level`
- `entries_in_order`: preserves insert order for cleaner debug output

### 3.3 Scope Manager
`SymbolTableManager` keeps:
- `current_scope`
- `next_entry_id`

This naturally forms a stack of scopes through parent links.

---

## 4. Algorithm and Complexity

### Hash Function
djb2:
- Start with `h = 5381`
- For each char: `h = h * 33 + ord(char)`
- Index: `h % 211`

### Operation Complexity (average)
- `insert`: O(1)
- `lookup_current`: O(1)
- `lookup` across nested scopes: O(number_of_scopes) average bucket traversal
- `delete` (current scope): O(1) average

Worst-case can degrade if many collisions, but prime table size and djb2 help distribution.

---

## 5. How Each Required Operation Works

### `begin_scope()`
Creates a new empty scope.
- Level is 0 if first scope, else `parent.level + 1`.
- New scope becomes `current_scope`.

### `end_scope()`
- Prints current scope in tabular form.
- Moves `current_scope` to `parent`.

### `insert(name, kind, type_name, line)`
1. Ensure a scope exists.
2. Check `lookup_current(name)`.
3. If found: return `None` (duplicate declaration in same scope).
4. Else create entry and push at bucket head (separate chaining).

### `lookup_current(name)`
Searches only in current scope bucket chain.

### `lookup(name)`
Searches current scope first, then parent, and so on until global scope.

### `delete(name)`
Deletes only from current scope chain (as required for scope-local behavior).

---

## 6. Mapping to Pascal CFG (What to Explain in Viva)

For grammar in Pascal subset:

- `program -> program id ...`
	- Insert program name in global scope.

- `declarations -> var identifier_list : type ; ...`
	- For each identifier in `identifier_list`, call `insert`.
	- If `insert` fails, report duplicate declaration in current scope.

- `subprogram_head -> function id ... | procedure id ...`
	- Insert subprogram name in enclosing scope.
	- Enter new scope for parameters and local declarations.

- `parameter_list -> identifier_list : type ...`
	- Insert each parameter as kind `parameter`.

- `compound_statement -> begin ... end`
	- Begin scope at block start, end scope at block end.

- `statement / factor` uses of `id`
	- Call `lookup(id)`.
	- If missing in all scopes, report undeclared variable.

Shadowing behavior:
- Inner declaration of same name is allowed.
- Lookup returns nearest declaration from current scope outward.

---

## 7. Task-wise Status

### Task 1 (In-lab) - Done
- Hash table (size 211) with separate chaining.
- `insert`, `lookup`, `delete`, print implemented.
- Verified by `task1_driver.py` with required operation counts.

### Task 2 (In-lab) - Done
- Nested scope manager with begin/end scope.
- Outward lookup across scope chain.
- Scope dump on pop.
- Nested and shadowing behavior verified in tests.

### Task 3 (Homework) - Partially done
- Semantic checks implemented in simulator.
- Recursive-descent parser integration is implemented in `lab_09/recursive_descent_parser.py`.

### Task 4 (Homework) - Done
- Pretty tabular scope print implemented.

### Task 5 (Homework) - In progress
- Test files created.
- Formal 1-2 page report file still to be written.

---

## 8. Integrating with Recursive Descent Parser (Recommended Path)

Your lab manual expects parser integration from earlier recursive descent work. The current codebase uses the Lab 09 recursive-descent parser as the real integration target because Lab 04 contains lexers, not a parser.

### 8.1 Parser setup
At parser start:
1. Create `SymbolTableManager` instance.
2. Call `begin_scope()` for global scope.

### 8.2 Declaration hooks
In recursive descent function that parses declarations (for `var identifier_list : type ;`):
1. Parse identifier list and resolved type.
2. For each identifier, call `insert`.
3. If `insert` returns `None`, emit duplicate declaration error with line.

### 8.3 Usage hooks
In expression/assignment parsing where identifiers are used:
1. On each identifier use, call `lookup`.
2. If result is `None`, emit undeclared variable error with line.

### 8.4 Scope hooks
At function/procedure body or nested `begin ... end` block:
1. On entry: `begin_scope()`
2. On exit: `end_scope()`

### 8.5 End of parse
Close all remaining scopes with `end_scope()` to print final dumps.

### 8.6 What is already wired in this workspace
- Program name insertion at the start of parsing.
- `var` declarations insert identifiers into the current scope.
- Function/procedure heads create a nested scope for parameters and local declarations.
- Identifier uses in assignments, expressions, and procedure/function calls trigger `lookup`.
- `begin ... end` blocks create and close nested scopes.

---

## 9. How to Run

From workspace root:

```bash
# Task 1 explicit checks
python lab_11/task1_driver.py

# Semantic behavior checks
python lab_11/pascal_semantic_simulator.py lab_11/test_cases/valid_nested.pas
python lab_11/pascal_semantic_simulator.py lab_11/test_cases/duplicate_decl.pas
python lab_11/pascal_semantic_simulator.py lab_11/test_cases/undeclared_use.pas
python lab_11/pascal_semantic_simulator.py lab_11/test_cases/shadowing_valid.pas
```

---

## 10. Expected Demonstration Points for Evaluation

1. Why hash table + chaining is chosen over list/tree.
2. Why table size is prime (211).
3. Difference between `lookup_current` and `lookup`.
4. How duplicate declaration is detected.
5. How undeclared use is detected.
6. How shadowing works correctly.
7. Why scope table is printed at `end_scope`.
8. How this plugs into recursive descent parser functions.

---

## 11. Known Limitations and Next Steps

Current limitations:
- Semantic driver is simplified and not a full parser.
- Not all Pascal constructs are semantically typed.
- Token stream adapter from Lab 3 lexer format to parser format is not finalized.

Recommended next steps:
1. Directly integrate hooks into your recursive descent parser file.
2. Save outputs for each test in an `output/` folder.
3. Write the 1-2 page report (`expected vs actual`, limitations, bug notes).

---

## 12. Quick Viva Script (Short Answers)

- Q: Why do we need a symbol table?
	A: To store identifier metadata for semantic checks like duplicate declarations, undeclared uses, and scope/type-related processing.

- Q: Why hash table?
	A: Average O(1) insertion/lookup, efficient for frequent identifier operations during compilation.

- Q: How do you detect duplicate declaration?
	A: Use `lookup_current` before insert. If found, report duplicate in the same scope.

- Q: How do you detect undeclared variable?
	A: On identifier use, call outward `lookup`. If no match up to global scope, report undeclared error.

- Q: How is shadowing handled?
	A: Inner scope insert is allowed; lookup searches from current scope first, so nearest declaration is returned.

- Q: Where do begin/end scope happen in parser?
	A: At function/procedure body entry-exit and nested `begin...end` block entry-exit.
