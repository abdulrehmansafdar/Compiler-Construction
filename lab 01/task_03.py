token_map = {
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'MULTIPLY',
    '/': 'DIVIDE',
    '(': 'LPAREN',
    ')': 'RPAREN',
    '=': 'ASSIGN'
}

# Tokenizer
def tokenize(expr):
    tokens = []
    i = 0
    while i < len(expr):
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        if ch.isdigit():
            num = ch
            i += 1
            while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                num += expr[i]
                i += 1
            tokens.append(("NUMBER", num))
            continue
        if ch.isalpha():
            name = ch
            i += 1
            while i < len(expr) and expr[i].isalnum():
                name += expr[i]
                i += 1
            tokens.append(("IDENTIFIER", name))
            continue
        if ch in token_map:
            tokens.append((token_map[ch], ch))
            i += 1
            continue
        raise Exception(f"Invalid character: {ch}")
    tokens.append(("EOF", None))
    return tokens

# Parser and Evaluator
class Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables

    def current(self):
        return self.tokens[self.pos]

    def eat(self, token_type=None):
        tok = self.current()
        if token_type and tok[0] != token_type:
            raise Exception(f"Expected {token_type}, got {tok[0]}")
        self.pos += 1
        return tok

    def parse(self):
        # Assignment or expression
        if self.current()[0] == "IDENTIFIER" and self.tokens[self.pos+1][0] == "ASSIGN":
            var_name = self.eat("IDENTIFIER")[1]
            self.eat("ASSIGN")
            expr = self.expr()
            return ("ASSIGN", var_name, expr)
        else:
            return self.expr()

    def expr(self):
        node = self.term()
        while self.current()[0] in ("PLUS", "MINUS"):
            op = self.eat()[0]
            right = self.term()
            node = (op, node, right)
        return node

    def term(self):
        node = self.factor()
        while self.current()[0] in ("MULTIPLY", "DIVIDE"):
            op = self.eat()[0]
            right = self.factor()
            node = (op, node, right)
        return node

    def factor(self):
        tok = self.current()
        if tok[0] == "NUMBER":
            self.eat("NUMBER")
            return ("NUMBER", float(tok[1]))
        elif tok[0] == "IDENTIFIER":
            self.eat("IDENTIFIER")
            return ("IDENTIFIER", tok[1])
        elif tok[0] == "LPAREN":
            self.eat("LPAREN")
            node = self.expr()
            self.eat("RPAREN")
            return node
        else:
            raise Exception(f"Unexpected token: {tok}")

def eval_ast(node, variables):
    if node[0] == "NUMBER":
        return node[1]
    if node[0] == "IDENTIFIER":
        if node[1] in variables:
            return variables[node[1]]
        else:
            raise Exception(f"Variable {node[1]} not defined")
    if node[0] == "ASSIGN":
        value = eval_ast(node[2], variables)
        variables[node[1]] = value
        print(f"Variable {node[1]} assigned value {value}")
        return value
    if node[0] == "PLUS":
        return eval_ast(node[1], variables) + eval_ast(node[2], variables)
    if node[0] == "MINUS":
        return eval_ast(node[1], variables) - eval_ast(node[2], variables)
    if node[0] == "MULTIPLY":
        return eval_ast(node[1], variables) * eval_ast(node[2], variables)
    if node[0] == "DIVIDE":
        return eval_ast(node[1], variables) / eval_ast(node[2], variables)
    raise Exception(f"Unknown AST node: {node}")

if __name__ == "__main__":
    test_cases = [
        "3 + 4 * 2",
        "(3 + 4) * 2",
        "x = 10",
        "y = 5",
        "x + y * 2",
        "((3 + 5) * 2) - 4 / 2"
    ]
    variables = {}
    for expr in test_cases:
        print(f"\nExpression: {expr}")
        tokens = tokenize(expr)
        print("Tokens:", end=" ")
        print([f"{t[0]}:{t[1]}" if t[0] in ("NUMBER", "IDENTIFIER") else t[0] for t in tokens if t[0] != "EOF"])
        parser = Parser(tokens, variables)
        ast = parser.parse()
        # Optional: print AST
        # print("AST:", ast)
        if ast[0] == "ASSIGN":
            eval_ast(ast, variables)
        else:
            result = eval_ast(ast, variables)
            print(f"Result: {int(result) if result == int(result) else result}")