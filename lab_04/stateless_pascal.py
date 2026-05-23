
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

# Stateless tokenizer for Pascal

def skip_whitespace(text, i):
    while i < len(text) and text[i].isspace():
        i += 1
    return i

def scan_comment(text, i, line):
    if text[i] == '{':
        start = i
        i += 1
        while i < len(text) and text[i] != '}':
            if text[i] == '\n':
                line += 1
            i += 1
        i += 1  # skip '}'
        return ('COMMENT', text[start:i], '-'), i, line
    elif text[i] == '(' and i+1 < len(text) and text[i+1] == '*':
        start = i
        i += 2
        while i < len(text):
            if text[i] == '*' and i+1 < len(text) and text[i+1] == ')':
                i += 2
                return ('COMMENT', text[start:i], '-'), i, line
            if text[i] == '\n':
                line += 1
            i += 1
    return None, i, line

def scan_string(text, i, line):
    if text[i] == "'":
        start = i
        i += 1
        while i < len(text) and text[i] != "'":
            if text[i] == '\n':
                line += 1
            i += 1
        i += 1  # skip closing quote
        return ('STRING', text[start+1:i-1], text[start+1:i-1]), i, line
    return None, i, line

def scan_number(text, i):
    start = i
    while i < len(text) and text[i].isdigit():
        i += 1
    if i < len(text) and text[i] == '.':
        i += 1
        while i < len(text) and text[i].isdigit():
            i += 1
        return ('FLOAT', text[start:i], text[start:i]), i
    return ('INTEGER', text[start:i], text[start:i]), i

def scan_identifier(text, i):
    start = i
    while i < len(text) and (text[i].isalnum() or text[i] == '_'):
        i += 1
    name = text[start:i]
    if name.lower() in KEYWORDS:
        return ('KEYWORD', name, '-'), i
    return ('IDENTIFIER', name, '-'), i

def scan_operator(text, i):
    if i+1 < len(text):
        op = text[i:i+2]
        if op in MULTI_OPS:
            return (MULTI_OPS[op], op, '-'), i+2
    if text[i] in TOKEN_MAP:
        return (TOKEN_MAP[text[i]], text[i], '-'), i+1
    return None, i+1

def tokenize_stateless(text):
    tokens = []
    i = 0
    line = 1
    while i < len(text):
        i = skip_whitespace(text, i)
        if i >= len(text):
            break
        if text[i] == '\n':
            line += 1
            i += 1
            continue
        # Comments
        tok, ni, line = scan_comment(text, i, line)
        if tok:
            tokens.append((line, tok[0], tok[1], tok[2]))
            i = ni
            continue
        # Strings
        tok, ni, line = scan_string(text, i, line)
        if tok:
            tokens.append((line, tok[0], tok[1], tok[2]))
            i = ni
            continue
        # Numbers
        if text[i].isdigit():
            tok, ni = scan_number(text, i)
            tokens.append((line, tok[0], tok[1], tok[2]))
            i = ni
            continue
        # Identifiers/Keywords
        if text[i].isalpha():
            tok, ni = scan_identifier(text, i)
            tokens.append((line, tok[0], tok[1], tok[2]))
            i = ni
            continue
        # Operators/Delimiters
        tok, ni = scan_operator(text, i)
        if tok:
            tokens.append((line, tok[0], tok[1], tok[2]))
            i = ni
            continue
        # Lexical error
        tokens.append((line, 'LEXICAL_ERROR', text[i], '-'))
        i += 1
    tokens.append((line, 'EOF', None, '-'))
    return tokens

if __name__ == "__main__":
    file_path = "test_pascal.txt"  # Replace with your Pascal source file
    with open(file_path, 'r') as f:
        text = f.read()
    tokens = tokenize_stateless(text)
    print("Line | Token Type | Lexeme | Value")
    print("-----------------------------------------")
    for t in tokens:
        print(f"{t[0]:<4} | {t[1]:<10} | {str(t[2]):<10} | {t[3]}")
