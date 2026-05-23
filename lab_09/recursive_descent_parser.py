# Recursive Descent Parser using FIRST and FOLLOW sets

from pathlib import Path
import sys

LAB_ROOT = Path(__file__).resolve().parents[1]
if str(LAB_ROOT) not in sys.path:
    sys.path.insert(0, str(LAB_ROOT))

from lab_11.symbol_table import SymbolTableManager

class FirstFollowParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current = self.tokens[self.pos] if self.pos < len(self.tokens) else ('EOF', None)
        self.errors = []
        self.symtab = SymbolTableManager()
        self.pending_decl_entries = []
        self.current_decl_type = None
        self.scope_initialized = False
    
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]
        else:
            self.current = ('EOF', None)
    
    def match(self, token_type):
        if self.current[0] == token_type:
            self.advance()
            return True
        else:
            self.errors.append(f"Expected {token_type}, got {self.current[0]}")
            return False

    def current_line(self):
        if isinstance(self.current, tuple) and len(self.current) >= 4 and isinstance(self.current[0], int):
            return self.current[0]
        return 0

    def current_lexeme(self):
        if isinstance(self.current, tuple):
            if len(self.current) >= 3 and isinstance(self.current[0], int):
                return self.current[2]
            if len(self.current) >= 2:
                return self.current[1]
        return None

    def _token_name(self, token):
        if isinstance(token, tuple):
            if len(token) >= 3 and isinstance(token[0], int):
                return token[1]
            return token[0]
        return token

    def _token_line(self, token):
        if isinstance(token, tuple) and len(token) >= 4 and isinstance(token[0], int):
            return token[0]
        return 0

    def _token_lexeme(self, token):
        if isinstance(token, tuple):
            if len(token) >= 3 and isinstance(token[0], int):
                return token[2]
            if len(token) >= 2:
                return token[1]
        return None

    def _ensure_global_scope(self):
        if not self.scope_initialized:
            self.symtab.begin_scope()
            self.scope_initialized = True

    def _type_name_from_current(self):
        if self.current[0] == 'INTEGER':
            return 'integer'
        if self.current[0] == 'REAL':
            return 'real'
        if self.current[0] == 'ARRAY':
            return 'array'
        return str(self.current[0]).lower()

    def _declare_name(self, name, kind, type_name, line):
        inserted = self.symtab.insert(name, kind, type_name, line)
        if inserted is None:
            self.errors.append(f"ERROR line {line}: duplicate declaration '{name}'")

    def _use_name(self, name, line):
        if name is None:
            return
        found = self.symtab.lookup(name)
        if found is None:
            self.errors.append(f"ERROR line {line}: undeclared variable '{name}'")

    def _flush_pending_declarations(self, type_name):
        for name, line in self.pending_decl_entries:
            self._declare_name(name, 'variable', type_name, line)
        self.pending_decl_entries = []

    def _close_scopes(self, target_level=0):
        while self.symtab.current_scope is not None and self.symtab.current_scope.scope_level >= target_level:
            self.symtab.end_scope()
    
    def parse(self):
        self._ensure_global_scope()
        self.program()
        self._close_scopes(0)
        if self.errors:
            for e in self.errors:
                print(f"Error: {e}")
            return False
        print("Parse successful!")
        return True
    
    def program(self):
        self.match('PROGRAM')
        program_name = self.current_lexeme()
        program_line = self.current_line()
        self.match('ID')
        if program_name:
            self._declare_name(program_name, 'program', 'void', program_line)
        if self.current[0] == 'LPAREN':
            self.match('LPAREN')
            self.identifier_list()
            self.match('RPAREN')
        self.match('SEMI')
        self.declarations()
        self.subprogram_declarations()
        self.compound_statement()
    
    def identifier_list(self):
        if self.current[0] == 'ID':
            self.pending_decl_entries.append((self.current_lexeme(), self.current_line()))
            self.match('ID')
        while self.current[0] == 'COMMA':
            self.match('COMMA')
            if self.current[0] == 'ID':
                self.pending_decl_entries.append((self.current_lexeme(), self.current_line()))
                self.match('ID')
    
    def declarations(self):
        while self.current[0] == 'VAR':
            self.match('VAR')
            self.pending_decl_entries = []
            self.identifier_list()
            self.match('COLON')
            declared_type = self._type_name_from_current()
            self.type_rule()
            self.match('SEMI')
            self._flush_pending_declarations(declared_type)
    
    def type_rule(self):
        if self.current[0] == 'ARRAY':
            self.match('ARRAY')
            self.match('LBRACKET')
            self.match('NUMBER')
            self.match('DOTDOT')
            self.match('NUMBER')
            self.match('RBRACKET')
            self.match('OF')
            self.standard_type()
        else:
            self.standard_type()
    
    def standard_type(self):
        if self.current[0] in ('INTEGER', 'REAL'):
            self.match(self.current[0])
        else:
            self.errors.append(f"Expected type, got {self.current[0]}")
    
    def subprogram_declarations(self):
        while self.current[0] in ('FUNCTION', 'PROCEDURE'):
            self.subprogram_declaration()
            self.match('SEMI')
    
    def subprogram_declaration(self):
        self.subprogram_head()
        self.declarations()
        self.compound_statement(create_scope=False)
        if self.symtab.current_scope is not None and self.symtab.current_scope.scope_level > 0:
            self.symtab.end_scope()
    
    def subprogram_head(self):
        if self.current[0] == 'FUNCTION':
            header_line = self.current_line()
            self.match('FUNCTION')
            func_name = self.current_lexeme()
            self.match('ID')
            if func_name:
                self._declare_name(func_name, 'function', 'unknown', header_line)
            self.symtab.begin_scope()
            self.arguments()
            self.match('COLON')
            return_type = self._type_name_from_current()
            self.standard_type()
            if func_name:
                self.symtab.update_in_parent_scope(func_name, type_name=return_type)
            self.match('SEMI')
        elif self.current[0] == 'PROCEDURE':
            header_line = self.current_line()
            self.match('PROCEDURE')
            proc_name = self.current_lexeme()
            self.match('ID')
            if proc_name:
                self._declare_name(proc_name, 'procedure', 'void', header_line)
            self.symtab.begin_scope()
            self.arguments()
            self.match('SEMI')
    
    def arguments(self):
        if self.current[0] == 'LPAREN':
            self.match('LPAREN')
            self.parameter_list()
            self.match('RPAREN')
    
    def parameter_list(self):
        self.pending_decl_names = []
        self.identifier_list()
        self.match('COLON')
        param_type = self._type_name_from_current()
        self.type_rule()
        param_line = self.current_line()
        self._flush_pending_declarations(param_type, param_line)
        while self.current[0] == 'SEMI':
            self.match('SEMI')
            self.pending_decl_names = []
            self.identifier_list()
            self.match('COLON')
            param_type = self._type_name_from_current()
            self.type_rule()
            param_line = self.current_line()
            self._flush_pending_declarations(param_type, param_line)
    
    def compound_statement(self, create_scope=True):
        opened_scope = False
        if create_scope:
            self.symtab.begin_scope()
            opened_scope = True
        self.match('BEGIN')
        self.optional_statements()
        self.match('END')
        if opened_scope and self.symtab.current_scope is not None and self.symtab.current_scope.scope_level > 0:
            self.symtab.end_scope()
    
    def optional_statements(self):
        if self.current[0] in ('ID', 'BEGIN', 'IF', 'WHILE'):
            self.statement_list()
    
    def statement_list(self):
        self.statement()
        while self.current[0] == 'SEMI':
            self.match('SEMI')
            self.statement()
    
    def statement(self):
        if self.current[0] == 'IF':
            self.match('IF')
            self.expression()
            self.match('THEN')
            self.statement()
            if self.current[0] == 'ELSE':
                self.match('ELSE')
                self.statement()
        elif self.current[0] == 'WHILE':
            self.match('WHILE')
            self.expression()
            self.match('DO')
            self.statement()
        elif self.current[0] == 'BEGIN':
            self.compound_statement()
        elif self.current[0] == 'ID':
            name = self.current_lexeme()
            line = self.current_line()
            self._use_name(name, line)
            self.match('ID')
            if self.current[0] == 'ASSIGNOP':
                self.match('ASSIGNOP')
                self.expression()
            elif self.current[0] == 'LPAREN':
                self.match('LPAREN')
                self.expression_list()
                self.match('RPAREN')
            elif self.current[0] == 'LBRACKET':
                self.match('LBRACKET')
                self.expression()
                self.match('RBRACKET')
                self.match('ASSIGNOP')
                self.expression()
    
    def expression_list(self):
        self.expression()
        while self.current[0] == 'COMMA':
            self.match('COMMA')
            self.expression()
    
    def expression(self):
        self.simple_expression()
        if self.current[0] == 'RELOP':
            self.match('RELOP')
            self.simple_expression()
    
    def simple_expression(self):
        if self.current[0] in ('PLUS', 'MINUS'):
            self.match(self.current[0])
        self.term()
        while self.current[0] == 'ADDOP':
            self.match('ADDOP')
            self.term()
    
    def term(self):
        self.factor()
        while self.current[0] == 'MULOP':
            self.match('MULOP')
            self.factor()
    
    def factor(self):
        if self.current[0] == 'ID':
            name = self.current_lexeme()
            line = self.current_line()
            self._use_name(name, line)
            self.match('ID')
            if self.current[0] == 'LPAREN':
                self.match('LPAREN')
                self.expression_list()
                self.match('RPAREN')
            elif self.current[0] == 'LBRACKET':
                self.match('LBRACKET')
                self.expression()
                self.match('RBRACKET')
        elif self.current[0] == 'NUMBER':
            self.match('NUMBER')
        elif self.current[0] == 'LPAREN':
            self.match('LPAREN')
            self.expression()
            self.match('RPAREN')
        elif self.current[0] == 'NOT':
            self.match('NOT')
            self.factor()
        else:
            self.errors.append(f"Unexpected token: {self.current[0]}")


if __name__ == "__main__":
    import sys
    import ast
    
    if len(sys.argv) > 1 and sys.argv[1] == "complex":
        fname = "lab_09/sample_tokens_complex.txt"
    elif len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        fname = "lab_09/sample_tokens.txt"
    
    tokens = []
    with open(fname) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            tokens.append(ast.literal_eval(line))
    
    parser = FirstFollowParser(tokens)
    parser.parse()
    print(f"Input accepted: {'Yes' if not parser.errors else 'No'}")