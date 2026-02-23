
class BufferManager:
	def __init__(self, file_path, buffer_size=10):
		self.buffer_size = buffer_size
		self.file = open(file_path, 'r')
		self.buffers = [[], []]  # Two buffers
		self.active = 0  # 0 or 1: which buffer is active
		self.forward = 0  # Current position in active buffer
		self.lexeme_begin = 0  # Start of current lexeme (absolute position)
		self.eof = False
		self.total_read = 0  # Total characters read from file
		self.file_ended = False
		self._fill_buffer(0)
		self._fill_buffer(1)

	def _fill_buffer(self, idx):
		if self.file_ended:
			self.buffers[idx] = ['E']  # Only sentinel if file ended
			print(f"[Buffer {idx+1} filled: EOF sentinel only]")
			return
		data = self.file.read(self.buffer_size)
		if len(data) < self.buffer_size:
			self.file_ended = True
		self.buffers[idx] = list(data) + ['E']  # Add sentinel
		print(f"[Buffer {idx+1} filled: {''.join(self.buffers[idx][:-1])}]")

	def getNextChar(self):
		while True:
			# If at end of buffer, switch to other buffer
			if self.forward >= len(self.buffers[self.active]):
				# Switch buffer
				print(f"[Buffer switch at position {self.forward}]")
				self.active = 1 - self.active
				self._fill_buffer(self.active)
				self.forward = 0
			ch = self.buffers[self.active][self.forward]
			print(f"[Buffer {self.active+1} active] Position {self.forward}: '{ch}'")
			self.forward += 1
			if ch == 'E':
				# If buffer only contains sentinel, real EOF
				if len(self.buffers[self.active]) == 1:
					self.eof = True
					return None  # True EOF
				# Otherwise, switch buffer and continue
				continue
			return ch

	def ungetChar(self):
		# Move back one character
		if self.forward > 0:
			self.forward -= 1
		else:
			# If at start, move to previous buffer
			self.active = 1 - self.active
			self.forward = len(self.buffers[self.active]) - 2  # Before sentinel

	def getLexeme(self):
		buf = self.buffers[self.active]
		start = self.lexeme_begin
		end = self.forward
		return ''.join(buf[start:end])

	def resetLexemeBegin(self):
		self.lexeme_begin = self.forward

	def close(self):
		self.file.close()


# Token map from lab 01
token_map = {
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'MULTIPLY',
    '/': 'DIVIDE',
    '(': 'LPAREN',
    ')': 'RPAREN',
    '<': 'LT',
    '>': 'GT',
    ';': 'SEMI',
    '{': 'LBRACE',
    '}': 'RBRACE'
}

# Tokenizer using BufferManager
def tokenize_file(file_path):
	tokens = []
	bm = BufferManager(file_path)
	ch = bm.getNextChar()
	while True:
		if ch is None:
			break
		# String literal
		if ch == '"':
			string_val = ''
			ch = bm.getNextChar()
			while ch is not None and ch != '"':
				string_val += ch
				ch = bm.getNextChar()
			if ch == '"':
				tokens.append(("STRING", string_val))
				bm.resetLexemeBegin()
				ch = bm.getNextChar()
				continue
			elif ch is None:
				# EOF reached while inside string
				raise Exception("Unterminated string literal at EOF")

		# Ignore spaces
		if ch.isspace():
			ch = bm.getNextChar()
			bm.resetLexemeBegin()
			continue

		# Number
		if ch.isdigit():
			num = ch
			ch = bm.getNextChar()
			while ch is not None and (ch.isdigit() or ch == '.'):
				num += ch
				ch = bm.getNextChar()
			tokens.append(("NUMBER", num))
			bm.resetLexemeBegin()
			continue

		# Identifier
		if ch.isalpha():
			name = ch
			ch = bm.getNextChar()
			while ch is not None and ch.isalnum():
				name += ch
				ch = bm.getNextChar()
			tokens.append(("IDENTIFIER", name))
			bm.resetLexemeBegin()
			continue

		# Single-character token
		if ch in token_map:
			tokens.append((token_map[ch], ch))
			ch = bm.getNextChar()
			bm.resetLexemeBegin()
			continue

		# Invalid character
		raise Exception(f"Invalid character: {ch}")

	tokens.append(("EOF", None))
	bm.close()
	return tokens


import time

if __name__ == "__main__":
	size = 5000
	test_code = '''int main() {\n    cout << "Hello World";\n    return 0;\n}\n''' * size
	with open("test_program.txt", "w") as f:
		f.write(test_code)

	print("Tokenizing test_program.txt using double buffering:")
	start_time = time.time()
	tokens = tokenize_file("test_program.txt")
	end_time = time.time()
	for token in tokens:
		print(token)
	print(f"\nTime taken (task_01): {end_time - start_time:.6f} seconds for {size} repetitions")