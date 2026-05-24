# Lab 11 Submission README

## What is included

- `symbol_table.py` - hash-based symbol table with nested scopes
- `recursive_descent_parser.py` - parser integration from Lab 09
- `pascal_semantic_simulator.py` - semantic test driver
- `task1_driver.py` - Task 1 operation-count driver
- `test_cases/` - sample valid and invalid inputs

## Build / Run

Open terminal in `D:\UET\6th_semester\CC Lab` and run:

```bash
python lab_11\task1_driver.py
python lab_11\pascal_semantic_simulator.py lab_11\test_cases\valid_nested.pas
python lab_11\pascal_semantic_simulator.py lab_11\test_cases\duplicate_decl.pas
python lab_11\pascal_semantic_simulator.py lab_11\test_cases\undeclared_use.pas
python lab_11\pascal_semantic_simulator.py lab_11\test_cases\shadowing_valid.pas
python lab_09\recursive_descent_parser.py
python lab_09\recursive_descent_parser.py complex
```

If you are already inside `lab_11`, use:

python task1_driver.py
python pascal_semantic_simulator.py test_cases\valid_nested.pas
python recursive_descent_parser.py

```

```
