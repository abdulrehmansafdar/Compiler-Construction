
KEYWORDS = {
    'begin', 'end', 'var', 'integer', 'real', 'if', 'then', 'else', 'while', 'do', 'for', 'to', 'downto', 'function', 'procedure', 'program', 'const', 'type', 'array', 'of', 'record', 'repeat', 'until', 'case', 'with', 'goto', 'div', 'mod', 'and', 'or', 'not'
}
TOKEN_MAP = {
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'MULTIPLY',
    '/': 'DIVIDE',
    '(': 'LPAREN',
    ')': 'RPAREN',
    ';': 'SEMI',
    ',': 'COMMA',
    ':': 'COLON',
    '.': 'DOT',
    '=': 'EQUAL',
    '<': 'LT',
    '>': 'GT',
    '[': 'LBRACKET',
    ']': 'RBRACKET',
    '{': 'LBRACE',
    '}': 'RBRACE'
}
MULTI_OPS = {':=': 'ASSIGN', '<=': 'LE', '>=': 'GE', '<>': 'NE'}

# Character classes
CHAR_CLASSES = {
    'LETTER': 0,
    'DIGIT': 1,
    'QUOTE': 2,
    'COLON': 3,
    'LT': 4,
    'GT': 5,
    'OP': 6,
    'DELIM': 7,
    'SPACE': 8,
    'NEWLINE': 9,
    'LBRACE': 10,
    'LPAREN': 11,
    'OTHER': 12
}

# Transition table: state x char_class -> next_state
# States: 0=START, 1=ID, 2=NUM, 3=STRING, 4=COLON, 5=LT, 6=GT, 7=OP, 8=DELIM, 9=COMMENT, 10=LPAREN, 11=ERROR
transition_table = [
    # LETTER DIGIT QUOTE COLON LT GT OP DELIM SPACE NEWLINE LBRACE LPAREN OTHER
    [1,    2,    3,    4,    5,  6,  7,  8,    0,     0,     9,     10,   11], # State 0 (START)
    [1,    1,   -1,   -1,   -1, -1, -1, -1,  -1,    -1,    -1,    -1,   -1],  # State 1 (ID)
    [-1,   2,   -1,   -1,   -1, -1, -1, -1,  -1,    -1,    -1,    -1,   -1],  # State 2 (NUM)
    [3,    3,   3,    3,    3,  3,  3,  3,   3,     3,     3,     3,    -1], # State 3 (STRING)
    [-1,   -1,  -1,   -1,   -1, -1, -1, -1,  -1,    -1,    -1,    -1,   -1],  # State 4 (COLON)
    [-1,   -1,  -1,   -1,   -1, -1, -1, -1,  -1,    -1,    -1,    -1,   -1],  # State 5 (LT)
    [-1,   -1,  -1,   -1,   -1, -1, -1, -1,  -1,    -1,    -1,    -1,   -1],  # State 6 (GT)
    [-1,   -1,  -1,   -1,   -1, -1, -1, -1,  -1,    -1,    -1,    -1,   -1],  # State 7 (OP)
    [-1,   -1,  -1,   -1,   -1, -1, -1, -1,  -1,    -1,    -1,    -1,   -1],  # State 8 (DELIM)
    [9,    9,   9,    9,    9,  9,  9,  9,   9,     9,     9,     9,    -1],  # State 9 (COMMENT)
    [-1,   -1,  -1,   -1,   -1, -1, -1, -1,  -1,    -1,    -1,    -1,   -1],  # State 10 (LPAREN)
    [-1,   -1,  -1,   -1,   -1, -1, -1, -1,  -1,    -1,    -1,    -1,   -1],  # State 11 (ERROR)
]

accepting_states = {
    1: 'IDENTIFIER',
    2: 'INTEGER',
    3: 'STRING',
    4: 'COLON',
    5: 'LT',
    6: 'GT',
    7: 'OP',
    8: 'DELIM',
    9: 'COMMENT',
    10: 'LPAREN',
    11: 'LEXICAL_ERROR'
}

# Classify character

def classify_char(ch):
    if ch.isalpha(): return CHAR_CLASSES['LETTER']
    if ch.isdigit(): return CHAR_CLASSES['DIGIT']
    if ch == "'": return CHAR_CLASSES['QUOTE']
    if ch == ':': return CHAR_CLASSES['COLON']
    if ch == '<': return CHAR_CLASSES['LT']
    if ch == '>': return CHAR_CLASSES['GT']
    if ch in '+-*/': return CHAR_CLASSES['OP']
    if ch in TOKEN_MAP: return CHAR_CLASSES['DELIM']
    if ch == ' ': return CHAR_CLASSES['SPACE']
    if ch == '\n': return CHAR_CLASSES['NEWLINE']
    if ch == '{': return CHAR_CLASSES['LBRACE']
    if ch == '(': return CHAR_CLASSES['LPAREN']
    return CHAR_CLASSES['OTHER']

# Transition table-based tokenizer

def tokenize_transition_table(text):
    tokens = []
    i = 0
    line = 1
    while i < len(text):
        state = 0
        lexeme = ''
        start_line = line
        while i < len(text) and state != 11:
            ch = text[i]
            char_class = classify_char(ch)
            next_state = transition_table[state][char_class]
            if next_state == -1:
                break
            lexeme += ch
            state = next_state
            if ch == '\n':
                line += 1
            i += 1
        # Accepting state
        if state in accepting_states:
            token_type = accepting_states[state]
            value = '-'
            if token_type == 'IDENTIFIER':
                if lexeme.lower() in KEYWORDS:
                    token_type = 'KEYWORD'
            if token_type == 'INTEGER':
                value = lexeme
            if token_type == 'STRING':
                value = lexeme[1:-1]
            if token_type == 'COMMENT':
                value = '-'
            tokens.append((start_line, token_type, lexeme, value))
        else:
            tokens.append((start_line, 'LEXICAL_ERROR', lexeme, '-'))
        # Skip whitespace
        while i < len(text) and text[i].isspace():
            if text[i] == '\n':
                line += 1
            i += 1
    tokens.append((line, 'EOF', None, '-'))
    return tokens

if __name__ == "__main__":
    file_path = "test_pascal.txt"  # Replace with your Pascal source file
    with open(file_path, 'r') as f:
        text = f.read()
    tokens = tokenize_transition_table(text)
    print("Line | Token Type | Lexeme | Value")
    print("-----------------------------------------")
    for t in tokens:
        print(f"{t[0]:<4} | {t[1]:<15} | {str(t[2]):<10} | {t[3]}")
