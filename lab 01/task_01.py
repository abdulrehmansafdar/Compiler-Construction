token_map = {
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'MULTIPLY',
    '/': 'DIVIDE',
    '(': 'LPAREN',
    ')': 'RPAREN'
}

def tokenize(expr):
    tokens = []
    i = 0

    while i < len(expr):
        ch = expr[i]

        # Ignore spaces
        if ch.isspace():
            i += 1
            continue

        # Number
        if ch.isdigit():
            num = ch
            i += 1
            while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                num += expr[i]
                i += 1
            tokens.append(("NUMBER", num))
            continue

        # Identifier
        if ch.isalpha():
            name = ch
            i += 1
            while i < len(expr) and expr[i].isalnum():
                name += expr[i]
                i += 1
            tokens.append(("IDENTIFIER", name))
            continue

        # Single-character token
        if ch in token_map:
            tokens.append((token_map[ch], ch))
            i += 1
            continue

        # Invalid character
        raise Exception(f"Invalid character: {ch}")

    tokens.append(("EOF", None))
    return tokens

if __name__ == "__main__":
    test_cases = [
        "3 + 4 * 2",
        "(3 + 4) * 2",
        "x + 3",
        "x + y * 2",
        "((3 + 5) * 2) - 4 / 2",
        "a * (b + c) - d / e"
    ]

    for expr in test_cases:
        print(f"\nExpression: {expr}")
        tokens = tokenize(expr)
        print("Tokens:")
        for token in tokens:
            print(token)