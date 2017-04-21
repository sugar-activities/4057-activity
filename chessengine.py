import popen2, os, sys
from piece import Move

class GnuChess:
	'''GNU Chess wrapper class.'''
	def __init__(self):
		'''Create a new instance of the GNU Chess wrapper, locate the 
		gnuchess executable, open a pipe to it and setup the comm.'''
		try:
			path = os.path.join(os.environ["SUGAR_BUNDLE_PATH"],"engines")
		except:
			path = os.path.join(".", "engines")

		OS = sys.platform
		if  OS == "linux2":
			engine_exec = "gnuchess-linux -ex"
		elif OS == "darwin":
			engine_exec = "gnuchess-osx -ex"
		elif OS == "win32":
			engine_exec = "gnuchess-win32.exe -ex"
		else:
			print "No gnuchess for %s, using system default" % (OS)
			engine_exec = ""

		if engine_exec != "":
			engine_path = os.path.join(path, engine_exec)
		else:
			print "Trying to find gnuchess in the PATH"
			engine_path = "gnuchess -ex"

		#Check whether the engine is executable:
		if not os.access(engine_path.split()[0], os.X_OK):
			print "Engine is not executable, try: chmod +x", engine_path.split()[0]
			raise IOError("Chess engine is not executable!")

		self.fin, self.fout = popen2.popen2(engine_path)

		#Check pipe:
		self.fout.write("\n")
		self.fout.flush()
		self.fin.readline()
		self.fin.readline()
		self.fin.readline()
		self.fout.write("depth 0\n")
		

	def move(self, move):
		'''Write a player's move to GNU Chess. Return the engine's move.'''
		move_str = self.move_to_gnuchess(move)

		print "Calling GNU Chess with move:", move_str
		self.fout.write(move_str + "\n")
		self.fout.flush()
		l = self.fin.readline()
		while l.find("My move is") == -1:
			if l.find("Illegal move") != -1:
				raise Exception("Illegal move")
			l = self.fin.readline()
		ans = l.split()[3]
		print ans
		if len(ans) == 4:
			return Move(self.gnuchess_to_coords(ans[:2]), \
				self.gnuchess_to_coords(ans[2:]))
		elif len(ans) == 5:
			return Crowning(self.gnuchess_to_coords(ans[:2]), \
				self.gnuchess_to_coords(ans[2:4]), \
				self.decode_piece(ans[4]))
		else:
			raise Exception("IA Error, unknown answer: " + ans)
		
	def close(self):
		self.fout.write("quit\n")
		self.fout.flush()
		self.fout.close()
		self.fin.close()
	

	def decode_piece(self, piece):
		p = piece.lower()
		if p == "q":
			return "queen"
		if p == "k":
			return "knight"
		if p == "b":
			return "bishop"
		if p == "r":
			return "rook"
		
		raise Exception("IA Error: Cannot determine Crowning type!")
	

	def move_to_gnuchess(self, move):
		move_str = self.coords_to_gnuchess(move.from_r, move.from_c) + \
			self.coords_to_gnuchess(move.to_r, move.to_c)
			
		if move.type == "Crowning":
			move_str += move.piece[0]
			
		return move_str

	def coords_to_gnuchess(self, i, j):
		letters = ["a", "b", "c", "d", "e", "f", "g", "h"]
		return letters[i] + str(8-j)

	def gnuchess_to_coords(self, move):
		letters = ["a", "b", "c", "d", "e", "f", "g", "h"]
		i = letters.index(move[0])
		j = int(8 - int(move[1]))
		return (i,j)
