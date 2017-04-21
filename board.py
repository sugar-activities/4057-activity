#
#    Ceibal Chess - A chess activity for Sugar.
#    Copyright (C) 2008 Alejandro Segovia <asegovi@gmail.com>
#
#   This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
import os, time
from cell import *
from resourcemanager import image_manager

# Board class
class Board:

	def __init__(self, width, height):
		self.w, self.h = width, height
		self.board = []
		self.king_white_move = False
		self.king_black_move = False

		#Castling specific:
		self.white_king_moved = False
		self.white_tower_right_moved = False
		self.white_tower_left_moved = False

		self.black_king_moved = False
		self.black_tower_right_moved = False
		self.black_tower_left_moved = False

		self.current_turn = "white"
		
		#Special parameter hypothetical is used 
		#to flag whether moves are being calculated for a hypothetical
		#board (such as checking if the king is checked after moving to 
		#some cell). This prevents an inifite recursion when checking
		#a king's possible moves.
		self.hypothetical = False
		
		self.moves_cache_dirty = True
		self.all_moves = {"white" : [], "black" : []} 
		
		self.white_en_passant = None
		self.black_en_passant = None
		
		self.background = None
		for i in range(0, 8):
			self.board.append([])
			for j in range(0, 8):
				if i % 2 != j % 2:
					color = (0, 0, 0)
				else:
					color = (255, 255, 255)
				self.board[i].append(Cell(i, j, width/8, color))
		self.castling_allowed = ["white", "black"]
	
	def clone(self):
		'''Create a shallow copy of this board. Cloned boards are
		hypothetical by default.'''
		clone = Board(self.w, self.h)
		
		clone.king_white_move = self.king_white_move
		clone.king_black_move = self.king_black_move
		
		clone.white_king_moved = self.white_king_moved
		clone.white_tower_right_moved = self.white_tower_right_moved
		clone.white_tower_left_moved = self.white_tower_left_moved 

		clone.black_king_moved = self.black_king_moved
		clone.black_tower_right_moved = self.black_tower_right_moved
		clone.black_tower_left_moved = self.black_tower_left_moved 
		
		clone.current_turn = self.current_turn
		clone.hypothetical = True
		
		clone.white_en_passant = self.white_en_passant
		clone.black_en_passant = self.black_en_passant
		
		for i in range(0,8):
			for j in range(0,8):
				piece = self[i][j].piece
				if not piece:
					continue
				clone[i][j].piece = Piece(piece.type, piece.owner)
				
		clone.castling_allowed = self.castling_allowed
		
		return clone
	
	def reset(self):
		'''Reset all game-specific flags'''
		self.king_white_move = False
		self.king_black_move = False

		#Castling specific:
		self.white_king_moved = False
		self.white_tower_right_moved = False
		self.white_tower_left_moved = False

		self.black_king_moved = False
		self.black_tower_right_moved = False
		self.black_tower_left_moved = False

		self.current_turn = "white"
		
		self.hypothetical = False

		self.castling_allowed = ["white", "black"]
		

	def __getitem__(self, i):
		'''Override operator [] to be able to reference cells
		directly via board[col][row]'''
		return self.board[i]

	def render_background(self, surface):
		'''Render the checkboard background'''
		if self.background is None:
			#Create alternating background
			self.background = pygame.Surface((self.w, self.h))
			for i in range(0, 8):
				for j in range(0, 8):
					self.board[i][j].render_background(self.background)

			#Load texture and blit it
			texture = image_manager.get_image("wood.png")
			texture = pygame.transform.scale(texture, (self.w, self.h))
			self.background.blit(texture, texture.get_rect())

		surface.blit(self.background, self.background.get_rect())
	
	def render_foreground(self, surface):
		'''Render cell contents. Call render_foreground on each cell.'''
		for i in range(0, 8):
			for j in range(0, 8):
				self.board[i][j].render_foreground(surface)
	
	def pick(self, x, y):
		'''Try to pick piece in the cell below the x,y screen position.
		If the cell does not contain a piece, return None.'''
		for i in range(0, 8):
			for j in range(0, 8):
				if self.board[i][j].contains(x, y):
					self.board[i][j].pick()
					return self.board[i][j]
		return None
	
	def get_piece_at(self, i, j):
		'''Get the piece at a given position. Returns None if there is 
		no piece at cell (i,j).'''
		if i < 0 or i > 7 or j < 0 or j > 7:
			raise Exception("Indices out of board: " + i + " " + j)
			
		return self.board[i][j].piece
	
	
	def put_piece_at(self, piece, i, j):
		if i < 0 or i > 7 or j < 0 or j > 7:
			raise Exception("Indices out of board: " + i + " " + j)
		
		self.board[i][j].piece = piece
		self.moves_cache_dirty = True
		
	#def move_piece_in_cell_to(self, cell, dest_i, dest_j):
	#	'''
	#	Try to move a piece from where it is to dest_i, dest_j.
	#	Returns True if the piece could be moved, False otherwise.
	#	'''
	#	if (dest_i, dest_j) in cell.piece.get_moves(cell.i, cell.j, self) \
	#	and self.board[dest_i][dest_j].piece is None:
	#		self.board[dest_i][dest_j].piece = cell.piece
	#		self.board[cell.i][cell.j].piece = None
	#		return True
	#	return False
	
	def cpu_move_piece(self, move):
		'''Perform a CPU's move. This is basically a hack and will not be
		needed once the code moves to command-based movements.'''
		
		result = self.move_piece_in_cell_to(self[move.from_r][move.from_c],
						move.to_r, move.to_c)
		
		if result and move.type == "Crowning":
			self[move.to_r][move.to_c].piece.type = move.piece
		
		return result
	
	def move_piece_in_cell_to(self, cell, dest_i, dest_j):
		'''Try to move the piece in cell from where it is to 
		(dest_i, dest_j).Returns True if the piece could be moved, 
		False otherwise.'''
		
		#Sanity checks:
		if not cell.piece:
			return False

		if dest_i < 0 or dest_i > 7 or dest_j < 0 or dest_j > 7:
			return False

		#print "moving piece in cell", cell.i, cell.j, "to:", dest_i, dest_j

		valid_moves = cell.piece.get_moves(cell.i, cell.j, self)
		if not (dest_i, dest_j) in valid_moves:
			return False
		
		#Castling
		if cell.piece.type == "king":
			if self.can_perform_castling(cell.piece.owner, dest_i):
				self.perform_castling(cell, dest_i, dest_j)
				self.moves_cache_dirty = True
				self.clear_opponent_en_passant(self[dest_i][dest_j].piece.owner)
				return True
			else:
				if dest_j == cell.j-2 or dest_j == cell.j+2:
					raise Exception("Castling Failed "+  \
					"(dest_j = %d but can_perform_castling returned false)", (dest_j))

		#Destination empty or with an enemy
		if self[dest_i][dest_j].piece is None or \
			self[dest_i][dest_j].piece.owner != cell.piece.owner:
		
			if cell.piece.type == "king":
				self.flag_king_movement(cell.piece.owner)
			elif cell.piece.type == "rook":
				self.flag_rook_movement(cell)

			#Promotion
			if cell.piece.type == "pawn" and \
				(dest_j == 0 or dest_j == 7 or \
				pygame.key.get_mods() & pygame.KMOD_SHIFT):
				
				cell.piece.type = "queen"
			
			#En passant
			if cell.piece.type == "pawn":
				#are we /moving/ en passant?
				if cell.piece.owner == "white" and cell.j == 6 and dest_j == 4:
					self.white_en_passant = dest_i
				elif cell.piece.owner == "black" and cell.j == 1 and dest_j == 3:
					self.black_en_passant = dest_i

				#are we /attacking/ en passant?
				if dest_i != cell.i and not self[dest_i][dest_j].piece:
					if cell.piece.owner == "white":
						self[dest_i][dest_j+1].piece = None
					else:
						self[dest_i][dest_j-1].piece = None
			
		        #Move the piece
			self.board[dest_i][dest_j].piece = cell.piece
			self.board[cell.i][cell.j].piece = None
			self.moves_cache_dirty = True
			self.clear_opponent_en_passant(self[dest_i][dest_j].piece.owner)
			return True
	
		print "Should never reach this point"
		return False
	
	def render_moves_for_piece_in_cell(self, surface, cell):
		'''Highlight possible moves for the piece in the given cell'''
		if cell.piece is None:
			raise Exception("cell does not contain a piece!")
		
		#select hightlight colors:
		if cell.piece.owner == self.current_turn:
			color = (0, 255, 0)
			color2 = (0, 180, 0)
		else:
			color = (255, 0, 0)
			color2 = (180, 0, 0)

		#print "[render_moves_for_piece_in_cell] Calling get_moves for", cell.piece.type
		#t_ini = time.time()
		dests = cell.piece.get_moves(cell.i, cell.j, self)
		#print "get_moves ran in", time.time() - t_ini, "seconds" 

		for dest in dests:
			self.board[dest[0]][dest[1]].\
				render_as_highlight(surface, color)
		cell.render_as_highlight(surface, color2)
	
	def change_turn(self):
		'''Make the change of turn.'''

		if self.current_turn == "white":
			self.current_turn = "black"
		else:
			self.current_turn = "white"
		
		return self.current_turn
		
	def clear_opponent_en_passant(self, owner):
		if owner == "white" and self.black_en_passant:
			self.black_en_passant = None
		elif owner == "black" and self.white_en_passant:
			self.white_en_passant = None

	def flag_king_movement(self, owner):
		'''Flag that the given owner's king has moved. It will no longer
		be able to perform castling.'''
		if owner == "white":
			self.white_king_moved = True
		else:
			self.black_king_moved = True
	
	def flag_rook_movement(self, cell):
		if cell.piece.owner == "white":
			if cell.i == 0 and cell.j == 7 and not self.white_tower_left_moved:
				self.white_tower_left_moved = True
			elif cell.i == 7 and cell.j == 7 and not self.white_tower_right_moved:
				self.white_tower_right_moved = True
		else:
			if cell.i == 0 and cell.j == 0 and not self.black_tower_left_moved:
				self.black_tower_left_moved = True
			elif cell.i == 7 and cell.j == 0 and not self.black_tower_right_moved:
				self.black_tower_right_moved = True
			
	def can_perform_castling(self, owner, dest_i):
		'''Determine whether the owner (black or white) can perform
		castling with the right or left rook, depending on dest_i'''

		if owner == "white" and self.white_king_moved:
			return False
		
		if owner == "black" and self.black_king_moved:
			return False
		
		if owner == "white" and dest_i == 6 and self.white_tower_right_moved:
			return False

		if owner == "white" and dest_i == 2 and self.white_tower_left_moved:
			return False

		if owner == "black" and dest_i == 6 and self.black_tower_right_moved:
			return False

		if owner == "white" and dest_i == 2 and self.black_tower_left_moved:
			return False

		if dest_i != 2 and dest_i != 6:
			return False

		return True

	def perform_castling(self, cell, dest_i, dest_j):
		'''Perform Castling between the king and a rook'''
		owner = cell.piece.owner
		if dest_i == cell.i + 2:
			#move king:
			self.board[dest_i][dest_j].piece = cell.piece
			cell.piece = None
			#move rook:
			self.board[dest_i-1][dest_j].piece = self.board[dest_i+1][dest_j].piece
			self.board[dest_i+1][dest_j].piece = None

		elif dest_i == cell.i - 2:
			#move king:
			self.board[dest_i][dest_j].piece = cell.piece
			cell.piece = None
			#move rook:
			self.board[dest_i+1][dest_j].piece = self.board[dest_i-2][dest_j].piece
			self.board[dest_i-2][dest_j].piece = None

		if owner == "white":
			self.white_king_moved = True
		else:
			self.black_king_moved = True
		return True

	def king_is_checked(self,owner):
		'''Check whether the king of the given owner is under attack'''
		#Find the king and all attackers
		king_pos = self.get_king_position(owner)
		enemy_moves = self.get_all_oponent_moves(owner)

		threats = filter(lambda x:x == king_pos, enemy_moves)
		if len(threats) > 0:			
			return True
		return False

#	def king_is_checkmated(self,owner):
#		'''Determine whether a given king is check mated'''
#		ki, kj = self.get_king_position(owner)
#		enemy_moves = self.get_all_oponent_moves(owner)
#		king_moves = self.board[ki][kj].piece.get_moves(ki, kj, self)
#		king_threatened = (ki, kj) in enemy_moves

#		if not king_threatened:
#			return False

#		for king_move in king_moves:
#			if king_move not in enemy_moves and not self.board[king_move[0]][king_move[1]].piece:
#				print "Possible escape:", king_move
#				return False

		#King is threatened and there is no escape: try to kill attacker(s):
#		my_moves = self.get_all_oponent_moves(owner == "white" and "black" or "white")

#		attackers = []
#		for i in range(0, 8):
#			for j in range(0, 8):
#				if self.board[i][j].piece and self.board[i][j].piece.owner != owner:
#					moves = self.board[i][j].piece.get_moves(i,j, self)
#					if (ki, kj) in moves:
#						attackers.append((i,j))

#		for i,j in attackers:
#			if (i, j) not in my_moves or (i, j) in enemy_moves:
#				print "Some attacker cannot be killed"
#				return True #Some attacker cannot be killed

		#All attackers could be killed by my moves
#		print "All (", len(attackers), ") attackers can be killed"

	def king_is_checkmated(self,owner):
		'''Determine whether a given king is checkmated.'''

		# If I cant make a move then it's a checkmate. Easy, huh? ;)
		my_moves = self.get_all_oponent_moves(owner == "white" and "black" or "white")

		if my_moves:
		    return False
		else:
		   print "Some Attacker cannot be killed"
		   return True
		     

	def get_king_position(self,owner):
		'''Find the owner's (white or black) king's position'''
		for i in range(0, 8):
			for j in range(0, 8):
				if self.board[i][j].piece:
					piece = self.board[i][j].piece
					if piece.type == "king" and piece.owner == owner:
						return (i,j)
		raise Exception("Error:", owner, "king not found!!")

	def get_all_oponent_moves(self, owner):
		'''Get all owner's enemies moves'''
		
		if owner == "white":
			enemy = "black"
		else:
			enemy = "white"

		if not self.moves_cache_dirty:
			print "Moves cache hit!"
			return self.all_moves[enemy]

		print "move cache missed"
		t_ini = time.time()

		#rebuild move cache:
		self.all_moves["white"] = []
		self.all_moves["black"] = []
		for i in range(0, 8):
			for j in range(0, 8):
				if self.board[i][j].piece:
					piece = self.board[i][j].piece
					self.all_moves[piece.owner].extend(piece.get_moves(i, j, self, True))

		self.moves_cache_dirty = False
		print "Move cache rebuilt in %.5f secs" % (time.time() - t_ini)
		return self.all_moves[enemy]
		#
		#all_moves = []
		#for i in range(0, 8):
		#	for j in range(0, 8):
		#		if self.board[i][j].piece:
		#			piece = self.board[i][j].piece
		#			if piece.owner != owner:
		#				all_moves.extend(piece.get_moves(i, j, self, True))

		#Cache moves:
		#if enemy == "black":
		#	self.black_moves_dirty = False
		#else:
		#	self.white_moves_dirty = False
		#self.all_moves[enemy] = all_moves
		
		#return all_moves
