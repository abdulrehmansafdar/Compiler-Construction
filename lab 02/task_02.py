import threading

BUFFER_SIZE = 10
NUM_BUFFERS = 2

class DoubleBuffer:
	def __init__(self, file_path, buffer_size=BUFFER_SIZE):
		self.file = open(file_path, 'r')
		self.buffer_size = buffer_size
		self.buffers = [[], []]
		self.active = 0  # buffer being read by consumer
		self.fill = 0    # buffer being filled by producer
		self.forward = 0 # position in active buffer
		self.eof = False
		self.lock = threading.Lock()
		self.empty = [threading.Semaphore(1), threading.Semaphore(1)]  # initially both empty
		self.full = [threading.Semaphore(0), threading.Semaphore(0)]   # initially both not full
		self.file_ended = False
	def producer_fill(self, idx):
		self.empty[idx].acquire()
		with self.lock:
			if self.file_ended:
				self.buffers[idx] = ['E']
			else:
				data = self.file.read(self.buffer_size)
				if len(data) < self.buffer_size:
					self.file_ended = True
				self.buffers[idx] = list(data) + ['E']
		self.full[idx].release()

	def consumer_get(self):
		# Returns next char, or None at EOF
		while True:
			self.full[self.active].acquire()
			with self.lock:
				buf = self.buffers[self.active]
				if self.forward >= len(buf):
					# Should not happen, but reset
					self.forward = 0
				ch = buf[self.forward]
				self.forward += 1
				if ch == 'E':
					if len(buf) == 1:
						self.eof = True
						self.empty[self.active].release()
						return None
					else:
						# End of buffer, switch
						self.empty[self.active].release()
						self.active = 1 - self.active
						self.forward = 0
						continue
				# Not sentinel, return char
				self.full[self.active].release()  # allow further reads
				return ch
	def close(self):
		self.file.close()

# Token map (same as before)
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

def producer_thread(buffer_mgr):
	idx = 0
	while True:
		buffer_mgr.producer_fill(idx)
		# If file ended, stop producing
		with buffer_mgr.lock:
			if buffer_mgr.file_ended:
				break
		idx = 1 - idx

def consumer_thread(buffer_mgr, tokens_out):
	ch = buffer_mgr.consumer_get()
	while ch is not None:
		# String literal
		if ch == '"':
			string_val = ''
			ch = buffer_mgr.consumer_get()
			while ch is not None and ch != '"':
				string_val += ch
				ch = buffer_mgr.consumer_get()
			if ch == '"':
				tokens_out.append(("STRING", string_val))
				ch = buffer_mgr.consumer_get()
				continue
			elif ch is None:
				raise Exception("Unterminated string literal at EOF")
		if ch.isspace():
			ch = buffer_mgr.consumer_get()
			continue
		if ch.isdigit():
			num = ch
			ch = buffer_mgr.consumer_get()
			while ch is not None and (ch.isdigit() or ch == '.'):
				num += ch
				ch = buffer_mgr.consumer_get()
			tokens_out.append(("NUMBER", num))
			continue

		if ch.isalpha():
			name = ch
			ch = buffer_mgr.consumer_get()
			while ch is not None and ch.isalnum():
				name += ch
				ch = buffer_mgr.consumer_get()
			tokens_out.append(("IDENTIFIER", name))
			continue

		if ch in token_map:
			tokens_out.append((token_map[ch], ch))
			ch = buffer_mgr.consumer_get()
			continue
		raise Exception(f"Invalid character: {ch}")
	tokens_out.append(("EOF", None))
	buffer_mgr.close()

import time

if __name__ == "__main__":
	# Use the same test_program.txt as before
	file_path = "test_program.txt"
	buffer_mgr = DoubleBuffer(file_path)
	tokens = []
	start_time = time.time()
	prod = threading.Thread(target=producer_thread, args=(buffer_mgr,))
	cons = threading.Thread(target=consumer_thread, args=(buffer_mgr, tokens))
	prod.start()
	cons.start()
	prod.join()
	cons.join()
	end_time = time.time()
	print("\nTokens produced by multi-threaded reader:")
	for token in tokens:
		print(token)
	print(f"\nTime taken (task_02): {end_time - start_time:.6f} seconds")
