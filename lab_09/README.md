# Lab 09 - Parser Implementation

Files in this lab:
1. `first_follow.py` - Computes FIRST and FOLLOW sets for the grammar
2. `recursive_descent_parser.py` - Recursive descent parser
3. `sample_tokens.txt` - Simple test tokens
4. `sample_tokens_complex.txt` - Complex test tokens

## How to Run

### FIRST and FOLLOW Sets
```bash
python lab_09/first_follow.py
```
Output: Computes and prints FIRST and FOLLOW sets for all non-terminals.

### Recursive Descent Parser
Simple test:
```bash
python lab_09/recursive_descent_parser.py
```

Complex test:
```bash
python lab_09/recursive_descent_parser.py complex
```

### Sample Input Files

`sample_tokens.txt` - Minimal Pascal program:
```
('PROGRAM', 'program')
('ID', 'main')
('SEMI', ';')
('BEGIN', 'begin')
('END', 'end')
```

`sample_tokens_complex.txt` - Full Pascal program with declarations, assignments, if-else, while, and function calls.