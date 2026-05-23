# FIRST and FOLLOW sets computation for Pascal subset

class FirstFollowComputer:
    def __init__(self, grammar):
        self.grammar = grammar
        self.first = {}
        self.follow = {}
        self.terminals = set()
        self.non_terminals = set()
        
    def compute(self):
        self._init_symbols()
        self._compute_first()
        self._compute_follow()
        return self.first, self.follow
    
    def _init_symbols(self):
        for lhs in self.grammar:
            self.non_terminals.add(lhs)
            for prod in self.grammar[lhs]:
                for symbol in prod.split():
                    if symbol not in self.grammar and symbol != 'epsilon':
                        self.terminals.add(symbol)
        
        for nt in self.non_terminals:
            self.first[nt] = set()
            self.follow[nt] = set()
        for t in self.terminals:
            self.first[t] = {t}
    
    def _compute_first(self):
        changed = True
        while changed:
            changed = False
            for lhs in self.grammar:
                for prod in self.grammar[lhs]:
                    symbols = prod.split()
                    first_prod = self._first_of_sequence(symbols)
                    if not first_prod.issubset(self.first[lhs]):
                        self.first[lhs] |= first_prod
                        changed = True
    
    def _first_of_sequence(self, symbols):
        result = set()
        for sym in symbols:
            if sym == 'epsilon':
                result.add('epsilon')
                break
            result |= self.first.get(sym, {sym}) - {'epsilon'}
            if 'epsilon' not in self.first.get(sym, set()):
                break
        return result
    
    def _compute_follow(self):
        self.follow[list(self.non_terminals)[0]].add('$')
        
        changed = True
        while changed:
            changed = False
            for lhs in self.grammar:
                for prod in self.grammar[lhs]:
                    symbols = prod.split()
                    for i, sym in enumerate(symbols):
                        if sym in self.non_terminals:
                            if i + 1 < len(symbols):
                                beta = symbols[i + 1:]
                                first_beta = self._first_of_sequence(beta)
                                new_follows = first_beta - {'epsilon'}
                                if not new_follows.issubset(self.follow[sym]):
                                    self.follow[sym] |= new_follows
                                    changed = True
                                if 'epsilon' in first_beta:
                                    if not self.follow[lhs].issubset(self.follow[sym]):
                                        self.follow[sym] |= self.follow[lhs]
                                        changed = True
                            else:
                                if not self.follow[lhs].issubset(self.follow[sym]):
                                    self.follow[sym] |= self.follow[lhs]
                                    changed = True
    
    def print_sets(self):
        print("=== FIRST Sets ===")
        for nt in sorted(self.non_terminals):
            print(f"FIRST({nt}) = {self.first[nt]}")
        
        print("\n=== FOLLOW Sets ===")
        for nt in sorted(self.non_terminals):
            print(f"FOLLOW({nt}) = {self.follow[nt]}")


if __name__ == "__main__":
    grammar = {
        'program': ['PROGRAM ID LPAREN identifier_list RPAREN SEMI declarations subprogram_declarations compound_statement',
                   'PROGRAM ID SEMI declarations subprogram_declarations compound_statement'],
        'identifier_list': ['ID', 'identifier_list COMMA ID'],
        'declarations': ['VAR identifier_list COLON type SEMI declarations', 'epsilon'],
        'type': ['standard_type', 'ARRAY LBRACKET NUMBER DOTDOT NUMBER RBRACKET OF standard_type'],
        'standard_type': ['INTEGER', 'REAL'],
        'subprogram_declarations': ['subprogram_declaration SEMI subprogram_declarations', 'epsilon'],
        'subprogram_declaration': ['subprogram_head declarations compound_statement'],
        'subprogram_head': ['FUNCTION ID arguments COLON standard_type SEMI', 'PROCEDURE ID arguments SEMI'],
        'arguments': ['LPAREN parameter_list RPAREN', 'epsilon'],
        'parameter_list': ['identifier_list COLON type', 'parameter_list SEMI identifier_list COLON type'],
        'compound_statement': ['BEGIN optional_statements END'],
        'optional_statements': ['statement_list', 'epsilon'],
        'statement_list': ['statement', 'statement_list SEMI statement'],
        'statement': ['variable ASSIGNOP expression', 'compound_statement', 'IF expression THEN statement ELSE statement', 'WHILE expression DO statement'],
        'variable': ['ID', 'ID LBRACKET expression RBRACKET'],
        'expression': ['simple_expression', 'simple_expression RELOP simple_expression'],
        'simple_expression': ['term', 'simple_expression ADDOP term'],
        'term': ['factor', 'term MULOP factor'],
        'factor': ['ID', 'NUMBER', 'LPAREN expression RPAREN', 'NOT factor'],
    }
    
    computer = FirstFollowComputer(grammar)
    computer.compute()
    computer.print_sets()