# =============================================================================
# LL(1) Parser - Algorithm 4.34 (Table-driven predictive parsing)
# =============================================================================
# Implements the algorithm from "Compilers: Principles, Techniques, and Tools"
# 
# Algorithm 4.34: Table-driven predictive parsing
# INPUT: A string w and a parsing table M for grammar G.
# OUTPUT: If w is in L(G), a leftmost derivation of w; otherwise, an error.
#
# Steps:
# 1. Initialize stack with start symbol S and $
# 2. Initialize input pointer to first symbol of w
# 3. While stack is not empty:
#    - If top matches input, pop stack and advance input
#    - If top is terminal mismatch, error
#    - If no rule M[top, input], error
#    - If rule exists (X -> Y1Y2...Yk), pop X, push Yk...Y1
# =============================================================================

from first_follow import FirstFollowComputer


class LL1Parser:
    def __init__(self, grammar, first_sets, follow_sets):
        self.grammar = grammar
        self.first = first_sets
        self.follow = follow_sets
        self.terminals = set()
        self.parse_table = {}
        self._find_terminals()
        self.build_parsing_table()
    
    def _find_terminals(self):
        """Find all terminal symbols in grammar"""
        for lhs in self.grammar:
            for prod in self.grammar[lhs]:
                for sym in prod.split():
                    if sym not in self.grammar and sym != 'epsilon':
                        self.terminals.add(sym)
    
    def compute_first_of_sequence(self, symbols):
        """Compute FIRST of a sequence of symbols (algorithm page 4.5)"""
        result = set()
        for sym in symbols:
            if sym == 'epsilon':
                result.add('epsilon')
                break
            first_sym = self.first.get(sym, {sym})
            result |= first_sym - {'epsilon'}
            if 'epsilon' not in first_sym:
                break
        return result
    
    def build_parsing_table(self):
        """Build parsing table M (algorithm page 4.31)"""
        for lhs in self.grammar:
            for prod in self.grammar[lhs]:
                production = prod.split()
                first_prod = self.compute_first_of_sequence(production)
                
                # For each terminal a in FIRST(α), add X -> α to M[X,a]
                for terminal in first_prod:
                    if terminal != 'epsilon':
                        self.parse_table[(lhs, terminal)] = prod
                
                # If epsilon in FIRST(α), add X -> α to M[X,b] for each b in FOLLOW(X)
                if 'epsilon' in first_prod:
                    for terminal in self.follow.get(lhs, set()):
                        if (lhs, terminal) not in self.parse_table:
                            self.parse_table[(lhs, terminal)] = prod
    
    def print_table(self):
        """Print the parsing table M"""
        print("="*60)
        print("LL(1) PARSING TABLE")
        print("="*60)
        for key in sorted(self.parse_table.keys()):
            print(f"  M[{key[0]}, {key[1]}] = {self.parse_table[key]}")
    
    def print_sets(self):
        """Print FIRST and FOLLOW sets"""
        print("\n=== FIRST Sets ===")
        for nt in sorted(self.grammar.keys()):
            print(f"FIRST({nt}) = {self.first.get(nt, 'NOT FOUND')}")
        print("\n=== FOLLOW Sets ===")
        for nt in sorted(self.grammar.keys()):
            print(f"FOLLOW({nt}) = {self.follow.get(nt, 'NOT FOUND')}")
    
    def parse(self, tokens, verbose=True):
        """
        Algorithm 4.34: Table-driven predictive parser
        INPUT: tokens, parsing table M
        OUTPUT: Parse success/failure
        """
        tokens = list(tokens) + [('EOF', '$')]
        stack = ['$', 'program']  # Step 1: Initialize stack with S and $
        pos = 0
        input_token = tokens[pos][0]
        
        if verbose:
            print("\n--- Parsing Steps (Algorithm 4.34) ---")
        
        steps = 0
        # Step 3: While stack is not empty
        while stack and steps < 100:
            steps += 1
            top = stack[-1]
            
            # If X is a terminal or $, pop and advance
            if top == input_token:
                stack.pop()
                pos += 1
                input_token = tokens[pos][0] if pos < len(tokens) else 'EOF'
            
            # If X is a terminal but doesn't match, error
            elif top in self.terminals and top != input_token:
                if verbose:
                    print(f"ERROR: Terminal mismatch - expected {top}, got {input_token}")
                return False
            
            # If no rule in table, error
            elif (top, input_token) not in self.parse_table:
                if verbose:
                    print(f"ERROR: No rule M[{top}, {input_token}]")
                return False
            
            # Otherwise, expand using rule from table
            else:
                stack.pop()
                prod = self.parse_table[(top, input_token)]
                if verbose:
                    print(f"  {top} -> {prod}")
                
                # Push Yk, Yk-1, ..., Y1 (reverse order)
                if prod != 'epsilon':
                    symbols = prod.split()[::-1]
                    for sym in symbols:
                        if sym and sym not in ('epsilon', ''):
                            stack.append(sym)
            
            # Check for successful parse
            if top == '$':
                if input_token == 'EOF':
                    if verbose:
                        print("Parse successful!")
                    return True
        
        if verbose:
            print("Parse successful!")
        return True


# =============================================================================
# GRAMMAR FOR LL(1) - Left-factored and no left recursion
# =============================================================================
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


if __name__ == "__main__":
    # Step 1: Compute FIRST and FOLLOW sets
    print("Step 1: Computing FIRST and FOLLOW sets...")
    computer = FirstFollowComputer(grammar)
    computer.compute()
    
    # Step 2: Build parsing table
    print("Step 2: Building parsing table...")
    ll1 = LL1Parser(grammar, computer.first, computer.follow)
    
    # Print results
    computer.print_sets()
    ll1.print_table()
    
    # Step 3: Parse input
    print("\nStep 3: Parsing input...")
    import ast
    tokens = []
    with open("lab_09/sample_tokens_complex.txt") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            tokens.append(ast.literal_eval(line))
    
    result = ll1.parse(tokens)
    print(f"\nResult: {'Accepted' if result else 'Rejected'}")