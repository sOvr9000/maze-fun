import numpy as np

def maze_params(ba):
	ls = ba[2]*256+ba[3]+2
	h,w = ba[0]+1,ba[1]+1
	return {'size': (h,w), 'solution_length': ls, 'total_bytes': 4+ceil((h*(w-1)+w*(h-1))*0.125+(ls-2)*0.25)}

class Maze:
	def __init__(self, size=(15,15)):
		if type(size) is int:
			self.size = (size, size)
		else:
			self.size = size
		self.width = self.size[1]
		self.height = self.size[0]
		self.path = np.zeros((self.height, self.width, 2), dtype=bool)
	def generate(self):
		# Using Wilson's algorithm
		self.path[:,:,:] = False # reset
		self.trace_back = {(0,0): (None,0)}
		closed_cells = [(0,0)]
		for i in range(self.height):
			for j in range(self.width):
				if (i,j) in closed_cells:
					continue
				cur_cell = (i,j)
				cur_path = [cur_cell]
				d = -1
				while True:
					ds = [0, 1, 2, 3]
					_i, _j = cur_cell
					if _i == 0:
						ds.remove(3)
					elif _i+1 == self.height:
						ds.remove(1)
					if _j == 0:
						ds.remove(2)
					elif _j+1 == self.width:
						ds.remove(0)
					if d != -1:
						ds.remove((d+2)%4)
					d = ds[np.random.randint(len(ds))]
					if d == 0:
						cur_cell = (_i, _j+1)
					elif d == 1:
						cur_cell = (_i+1, _j)
					elif d == 2:
						cur_cell = (_i, _j-1)
					elif d == 3:
						cur_cell = (_i-1, _j)
					if cur_cell in cur_path:
						cur_path = cur_path[:cur_path.index(cur_cell)+1]
					else:
						cur_path.append(cur_cell)
						if cur_cell in closed_cells:
							for z in range(len(cur_path)-2,-1,-1):
								self.set_path_to(*cur_path[z], *cur_path[z+1], True)
								closed_cells.append(cur_path[z])
								self.trace_back[cur_path[z]] = (cur_path[z+1], self.trace_back[cur_path[z+1]][1]+1)
							break
		c = (self.height-1, self.width-1)
		self.solution = [c]
		while c != (0,0):
			c = self.trace_back[c][0]
			self.solution.append(c)
		self.solution.reverse()
	def set_path(self, i, j, k, v):
		if k == 0:
			if j+1 < self.width:
				self.path[i,j,0] = v
		elif k == 1:
			if i+1 < self.height:
				self.path[i,j,1] = v
		elif k == 2:
			if j > 0:
				self.path[i,j-1,0] = v
		elif k == 3:
			if i > 0:
				self.path[i-1,j,1] = v
	def set_path_to(self, i0, j0, i1, j1, v):
		self.set_path(i0, j0, 0 if j1 == j0+1 else 1 if i1 == i0+1 else 2 if j0 == j1+1 else 3, v)
	def __repr__(self, show_solution=True):
		FILLED = '\u25a0'
		EMPTY = ' '#'\u25a1'
		s = [[FILLED if i == 0 or j == 0 or i == self.height*2 or j == self.width*2 or (i%2 == 0 and j%2 == 0) else EMPTY for j in range(self.width*2+1)] for i in range(self.height*2+1)]
		for i in range(self.height):
			for j in range(self.width):
				if not self.path[i,j,0]:
					s[2*i+1][2*(j+1)] = FILLED
				if not self.path[i,j,1]:
					s[2*(i+1)][2*j+1] = FILLED
		if show_solution:
			SOLUTION = '\u2022'#'\u25a1'
			s[1][1] = SOLUTION
			lc = self.solution[0]
			for c in self.solution[1:]:
				s[2*c[0]+1][2*c[1]+1] = SOLUTION
				if c[0] == lc[0]+1:
					s[2*(lc[0]+1)][2*lc[1]+1] = SOLUTION
				elif lc[0] == c[0]+1:
					s[2*(c[0]+1)][2*c[1]+1] = SOLUTION
				elif c[1] == lc[1]+1:
					s[2*lc[0]+1][2*(lc[1]+1)] = SOLUTION
				elif lc[1] == c[1]+1:
					s[2*c[0]+1][2*(c[1]+1)] = SOLUTION
				lc = c
		return f'Maze {self.height}x{self.width} | Solution length: {len(self.solution)}\n' + '\n'.join(' '.join(_s) for _s in s)
	def to_bytearray(self):
		assert self.width <= 256 and self.height <= 256, f'The maze is too large to be encoded as a byte array.  Size = ({self.height}, {self.width}), but it must be no larger than (256, 256) in either dimension.'
		assert self.width > 0 and self.height > 0, f'Error with maze dimensions.  Size = ({self.height}, {self.width})'
		lba = (self.width * (self.height - 1) + self.height * (self.width - 1)) * 0.125 + (len(self.solution)-2) * 0.25
		Lba = ceil(lba)
		bits = np.zeros((Lba,8),dtype=bool)
		U = 0
		V = 0
		for i in range(self.height):
			for j in range(self.width-1):
				bits[U,V] = self.path[i,j,0]
				V += 1
				if V == 8:
					U += 1
					V = 0
		for i in range(self.height-1):
			for j in range(self.width):
				bits[U,V] = self.path[i,j,1]
				V += 1
				if V == 8:
					U += 1
					V = 0
		lc = self.solution[0]
		for c in self.solution[1:-1]:
			if c[0] == lc[0]+1:
				bits[U,V] = False
				V += 1
				if V == 8:
					U += 1
					V = 0
				bits[U,V] = True
			elif lc[0] == c[0]+1:
				bits[U,V] = True
				V += 1
				if V == 8:
					U += 1
					V = 0
				bits[U,V] = True
			elif c[1] == lc[1]+1:
				bits[U,V] = False
				V += 1
				if V == 8:
					U += 1
					V = 0
				bits[U,V] = False
			elif lc[1] == c[1]+1:
				bits[U,V] = True
				V += 1
				if V == 8:
					U += 1
					V = 0
				bits[U,V] = False
			V += 1
			if V == 8:
				U += 1
				V = 0
			lc = c
		ba = np.dot(bits, [128,64,32,16,8,4,2,1])
		ba = bytearray([self.height-1, self.width-1, (len(self.solution)-2)//256, (len(self.solution)-2)%256] + ba.tolist())
		return ba
	@classmethod
	def from_bytearray(cls, ba):
		p = maze_params(ba)
		m = Maze(size = p['size'])
		m.solution = [(0,0)]
		ls = p['solution_length']
		bits = [
			bit
			for b in ba[4:]
			for bit in (
				b&0b10000000!=0,
				b&0b01000000!=0,
				b&0b00100000!=0,
				b&0b00010000!=0,
				b&0b00001000!=0,
				b&0b00000100!=0,
				b&0b00000010!=0,
				b&0b00000001!=0,
			)
		]
		K = 0
		for i in range(m.height):
			for j in range(m.width-1):
				m.path[i,j,0] = bits[K]
				K += 1
		for i in range(m.height-1):
			for j in range(m.width):
				m.path[i,j,1] = bits[K]
				K += 1
		for _ in range(ls-2):
			d = bits[K]*2+bits[K+1]
			i,j = m.solution[-1]
			if d == 0:
				m.solution.append((i,j+1))
			elif d == 1:
				m.solution.append((i+1,j))
			elif d == 2:
				m.solution.append((i,j-1))
			elif d == 3:
				m.solution.append((i-1,j))
			K += 2
		m.solution.append((m.height-1,m.width-1))
		return m
	def save(self, file):
		if '.' not in file:
			file += '.maze'
		f = open(file, 'wb')
		f.write(self.to_bytearray())
		f.close()
