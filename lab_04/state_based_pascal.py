
# Keywords for Pascal
KEYWORDS = {
    'begin', 'end', 'var', 'integer', 'real', 'if', 'then', 'else', 'while', 'do', 'for', 'to', 'downto', 'function', 'procedure', 'program', 'const', 'type', 'array', 'of', 'record', 'repeat', 'until', 'case', 'with', 'goto', 'div', 'mod', 'and', 'or', 'not'
}

# Token map for Pascal
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

# Multi-character operators
MULTI_OPS = {':=': 'ASSIGN', '<=': 'LE', '>=': 'GE', '<>': 'NE'}

class BufferManager:
    def __init__(self, file_path, buffer_size=10):
        self.buffer_size = buffer_size
        self.file = open(file_path, 'r')
        self.buffers = [[], []]
        self.active = 0
        self.forward = 0
        self.lexeme_begin = 0
        self.eof = False
        self.file_ended = False
        self._fill_buffer(0)
        self._fill_buffer(1)

    def _fill_buffer(self, idx):
        if self.file_ended:
            self.buffers[idx] = ['E']
            return
        data = self.file.read(self.buffer_size)
        if len(data) < self.buffer_size:
            self.file_ended = True
        self.buffers[idx] = list(data) + ['E']

    def getNextChar(self):
        while True:
            if self.forward >= len(self.buffers[self.active]):
                self.active = 1 - self.active
                self._fill_buffer(self.active)
                self.forward = 0
            ch = self.buffers[self.active][self.forward]
            self.forward += 1
            if ch == 'E':
                if len(self.buffers[self.active]) == 1:
                    self.eof = True
                    return None
                continue
            return ch

    def ungetChar(self):
        if self.forward > 0:
            self.forward -= 1
        else:
            self.active = 1 - self.active
            self.forward = len(self.buffers[self.active]) - 2

    def close(self):
        self.file.close()

# State-based tokenizer for Pascal

def tokenize_file(file_path):
    tokens = []
    bm = BufferManager(file_path)
    ch = bm.getNextChar()
    line = 1
    while True:
        if ch is None:
            break
        # Handle comments: { ... } or (* ... *)
        if ch == '{':
            comment = ch
            ch = bm.getNextChar()
            while ch is not None and ch != '}':
                if ch == '\n':
                    line += 1
                comment += ch
                ch = bm.getNextChar()
            comment += '}'
            tokens.append((line, 'COMMENT', comment, '-'))
            ch = bm.getNextChar()
            continue
        if ch == '(':  # Check for (* ... *)
            next_ch = bm.getNextChar()
            if next_ch == '*':
                comment = '(*'
                ch = bm.getNextChar()
                while ch is not None:
                    if ch == '*':
                        peek = bm.getNextChar()
                        if peek == ')':
                            comment += '*)'
                            ch = bm.getNextChar()
                            tokens.append((line, 'COMMENT', comment, '-'))
                            break
                        else:
                            comment += '*' + peek
                            ch = bm.getNextChar()
                            continue
                    if ch == '\n':
                        line += 1
                    comment += ch
                    ch = bm.getNextChar()
                continue
            else:
                bm.ungetChar()
        # String literal: '...'
        if ch == "'":
            string_val = ''
            ch = bm.getNextChar()
            while ch is not None and ch != "'":
                if ch == '\n':
                    line += 1
                string_val += ch
                ch = bm.getNextChar()
            tokens.append((line, 'STRING', string_val, string_val))
            ch = bm.getNextChar()
            continue
        # Ignore whitespace
        if ch.isspace():
            if ch == '\n':
                line += 1
            ch = bm.getNextChar()
            continue
        # Multi-character operators
        if ch in {':', '<', '>'}:
            peek = bm.getNextChar()
            op = ch + (peek if peek else '')
            if op in MULTI_OPS:
                tokens.append((line, MULTI_OPS[op], op, '-'))
                ch = bm.getNextChar()
                continue
            else:
                bm.ungetChar()
        # Number (integer or float)
        if ch.isdigit():
            num = ch
            ch = bm.getNextChar()
            while ch is not None and (ch.isdigit() or ch == '.'):
                num += ch
                ch = bm.getNextChar()
            if '.' in num:
                tokens.append((line, 'FLOAT', num, num))
            else:
                tokens.append((line, 'INTEGER', num, num))
            continue
        # Identifier or keyword
        if ch.isalpha():
            name = ch
            ch = bm.getNextChar()
            while ch is not None and (ch.isalnum() or ch == '_'):
                name += ch
                ch = bm.getNextChar()
            if name.lower() in KEYWORDS:
                tokens.append((line, 'KEYWORD', name, '-'))
            else:
                tokens.append((line, 'IDENTIFIER', name, '-'))
            continue
        # Single-character token
        if ch in TOKEN_MAP:
            tokens.append((line, TOKEN_MAP[ch], ch, '-'))
            ch = bm.getNextChar()
            continue
        # End of statement
        if ch == '\n':
            line += 1
            ch = bm.getNextChar()
            continue
        # Invalid character
        tokens.append((line, 'LEXICAL_ERROR', ch, '-'))
        ch = bm.getNextChar()
    tokens.append((line, 'EOF', None, '-'))
    bm.close()
    return tokens

if __name__ == "__main__":
    file_path = "test_pascal.txt"  # Replace with your Pascal source file
    tokens = tokenize_file(file_path)
    print("Line | Token Type | Lexeme | Value")
    print("-----------------------------------------")
    for t in tokens:
        print(f"{t[0]:<4} | {t[1]:<10} | {str(t[2]):<10} | {t[3]}")
