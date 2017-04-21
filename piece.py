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

import pygame, os
from resourcemanager import image_manager

# Move classes
class Move:
	'''Represents a regular piece movement in chess.'''
	def __init__(self, pair_from, pair_to):
		self.type = "Move"
		self.from_r = pair_from[0]
		self.from_c = pair_from[1]
		self.to_r = pair_to[0]
		self.to_c = pair_to[1]

class Castling:
	'''Represents a Castling move in chess. Unused.'''
	def __init__(self, rook_c, rook_r, king_c, king_r):
		self.type = "Castling"
		self.rook_c = rook_c # Column and row of castling rook and king
		self.rook_r = rook_r
		self.king_c = king_c
		self.king_r = king_r

class Crowning:
	'''Represents a Pawn Crowning move in chess.'''
	def __init__(self, (from_c, from_r), (to_c, to_r), piece):
		self.type = "Crowning"
		self.from_c = from_c
		self.from_r = from_r
		self.to_c = to_c
		self.to_r = to_r
		self.piece = piece

WHITE_RANK = 7
BLACK_RANK = 0

class Piece:
	
	def __init__(self, type, owner):
		self.type = type
		self.picked = False
		self.owner = owner
		if (type == "pawn"):
			self.en_passant = False
		self.has_moved = False

		
	def render(self, surface, x, y, cell_size):
		'''
		Render this piece. x,y are the top left corner of the 
		container cell; cell_size is its size
		'''
		img = image_manager.get_image(self.type + self.owner + ".png")

		w,h = img.get_width(), img.get_height()
		tx = x + (cell_size - w) / 2
		ty = y + (cell_size - h) / 2
		
		surface.blit(img, pygame.Rect(tx, ty, w, h))
		
	def on_pick(self):
		return

		
	def get_moves(self, column, row, board, attack=False):
		'''Get all possible cell destinations depending on i, j and 
		the piece type. Special parameter attack is used flag when not
		to calculate certain moves because we are interested in getting
		attack moves. An example of this is the king Castling which 
		cannot be considered an attack move.'''
		
		if not board.hypothetical:
			print "Calculating moves for", self.type
		
		dests = []
		
		dests.append((column, row))

		if self.type == "knight":
			dests.append((column+1, row+2))
			dests.append((column+1, row-2))
			dests.append((column-1, row-2))
			dests.append((column-1, row+2))
			dests.append((column+2, row+1))
			dests.append((column+2, row-1))
			dests.append((column-2, row-1))
			dests.append((column-2, row+1))
			
		if self.type == "rook" or self.type == "queen":
			for dc,dr in ([(0,d) for d in [-1,1]] + [(d,0) for d in [-1,1]]):
				c = column + dc
				r = row + dr
				blocked = None
				while r >= 0 and r < 8 and c >= 0 and c < 8 and not blocked:
					blocked = board.board[c][r].piece
					if not blocked or self.owner != board.board[c][r].piece.owner \
						or (self.type == "rook" and board.board[c][r].piece.type == "king"):
						dests.append((c,r))
						c = c + dc
						r = r + dr
						
				
		if self.type == "bishop" or self.type == "queen":
			for dc,dr in [(dc,dr) for dc in [-1,1] for dr in [-1,1]]:
				c = column + dc
				r = row + dr
				blocked = None
				while r >= 0 and r < 8 and c >= 0 and c < 8 and not blocked:
					blocked = board.board[c][r].piece
					if not blocked or self.owner != board.board[c][r].piece.owner :
						dests.append((c,r))
						c = c + dc
						r = r + dr
				
		if self.type == "king":
			dests = [(column + dc, row + dr) for dc in [-1,0,1] for dr in [-1,0,1] if dc != 0 or dr != 0]
			
			if not attack:
				threats = board.get_all_oponent_moves(self.owner)
				
				#Castling
				if not board.king_is_checked(self.owner):
				
					if self.owner == "white":
						if not board.white_king_moved:
							if not board.white_tower_right_moved and \
							not board.board[column+1][row].piece and \
							not board.board[column+2][row].piece and \
							(column+2, row) not in threats and\
							(column+1, row) not in threats:
								dests.append((column+2, row))
							
							if not board.white_tower_left_moved and \
							not board.board[column-1][row].piece and \
							not board.board[column-2][row].piece and \
							not board.board[column-3][row].piece and \
							(column-2, row) not in threats and \
							(column-1, row) not in threats:
								dests.append((column-2, row))
					else:
						if not board.black_king_moved:
							if not board.black_tower_right_moved and \
							not board.board[column+1][row].piece and \
							not board.board[column+2][row].piece and \
							(column+2,row) not in threats and\
							(column+1,row) not in threats:
								dests.append((column+2, row))
							if not board.black_tower_left_moved and \
							not board.board[column-1][row].piece and \
							not board.board[column-2][row].piece and \
							not board.board[column-3][row].piece and \
							(column-2, row) not in threats and\
							(column-1, row) not in threats:
								dests.append((column-2, row))

				#Remove threatened destinations:
				#all_dests = len(dests)
				dests = filter(lambda x:(x[0],x[1]) not in threats, dests)			
				#print "Removed", all_dests - len(dests), "inmediate threats for king"
		
		if self.type == "pawn":
			dr = self.owner == "white" and -1 or 1
			#rank = self.owner != "white" and BLACK_RANK or WHITE_RANK
			if self.owner == "white":
				rank = WHITE_RANK
			else:
				rank = BLACK_RANK

			#Bound checking:
			if 0 <= row + dr < 8:
				if not board[column][row + dr].piece and not attack:
					dests.append((column, row + dr))
				
				#Double step:
				if row== rank + dr and not board[column][row + 2*dr].piece\
					and not board[column][row + 1*dr].piece and not attack:
					dests.append((column, row + 2 * dr))
				
				#Attack move:
				if attack:
					dests.append((column - 1, row + dr))
					dests.append((column + 1, row + dr))
				else:
					if column > 0 and (board.board[column - 1][row + dr].piece):
						if board.board[column - 1][row + dr].piece.owner != self.owner:
							dests.append((column - 1, row + dr))
					if column < 7 and (board.board[column + 1][row + dr].piece):
						if board.board[column + 1][row + dr].piece.owner != self.owner:
							dests.append((column + 1, row + dr))
							
				#Attack en passant:
				if self.owner == "white" and board.black_en_passant and row == 3:
					dests.append((board.black_en_passant, 2))
					
				elif self.owner == "black" and board.white_en_passant and row == 4:
					dests.append((board.white_en_passant, 5))
		
		
		#Remove out-of-bounds destinations
		dests = filter(lambda x: x[0] >= 0 and x[0] < 8 and x[1] >= 0 and x[1] < 8, dests)

		#Remove moving to the cell we are in
		dests = filter(lambda x: x != (column, row), dests)

		#Remove occupied destinations:
		dests = filter(lambda x:board[x[0]][x[1]].piece is None or \
				board[x[0]][x[1]].piece.owner != self.owner, dests)

		#Simulate movement and remove destinations that leave the king checked:
		if not board.hypothetical:
			#if self.type == "king":
			#	all_dests = len(dests)

			invalid = []
			for i,j in dests:
				next = board.clone()
				moved = next.move_piece_in_cell_to(next[column][row], i, j)
				if not moved or next.king_is_checked(self.owner):
					invalid.append((i,j))
			dests = filter(lambda x:x not in invalid, dests)

			#if self.type == "king":
			#	print "Removed", all_dests - len(dests), "secondary threats for king" 

		return dests
	
	def is_turn(self, lastowner):
		if self.owner == lastowner:
			return True
		else:
			return False
		
		
		
		
