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

import pygame, sys, os
from piece import *
from messenger import *
from chessengine import *

MODE_P_VS_CPU = 0
MODE_P_VS_P = 1

class BoardController:

	def __init__(self, board, mode = MODE_P_VS_P, game_code = "0", logpath = "."):
		'''Create a new board controller.'''
		self.board = board
		self.selected_cell = None
		self.board.current_turn = "black" #will be flipped
		self.board.change_turn() #set turn to white and show a message
		self.game_state = "playing"

		#Move logging:
		self.move_log = open(os.path.join(logpath, game_code + ".log"), "w")

		#IA related
		self.ia = None
		self.mode = mode
		if mode == MODE_P_VS_CPU:
			try:
				self.ia = GnuChess()
			except Exception,ex:
				print "Cannot start gnuchess:", ex.message, \
					"defaulting to player vs. player mode"
				self.mode = MODE_P_VS_P

		self.last_p_move = None #no last known player move

		#Animation related
		self.rendering_animation = False

	def shutdown(self, message = None):
		if self.mode == MODE_P_VS_CPU and self.ia:
			self.ia.close()
		if message:
			self.move_log.write(message + "\n")
		self.move_log.close()
	
	#TODO: Add castling and en-passant pawns indications.
	def init_board_text(self, text):
		'''Initialize board to a serialized position'''
		column, row = 0, 0
		kind_by_char = {'P': "pawn", 'N': "knight", 'B': "bishop", 
						  'R': "rook", 'Q': "queen", 'K': "king"}
		for char in text:
			player = char.isupper() and "white" or "black"
			kind = kind_by_char.get(char.upper())
			
			if kind:
				self.board.put_piece_at(Piece(kind, player), column, row)
			if column == 7:
				column, row = -1, row + 1
			column = column + 1
	
	def init_board(self):
		'''Initialize board to starting chess configuration'''
		#self.init_board_text("RNBQKBNR" + "P" * 8 + "." * 32 + "p" * 8 + "rnbqkbnr")
		self.init_board_text("rnbqkbnr" + "p" * 8 + "." * 32 + "P" * 8 + "RNBQKBNR")
	
	def update(self, delta_t):
		'''Perform updates on the board such as animations, 
		calling the IA, etc.'''
		#TODO: Animate piece movements

		#Call IA:
		if self.ia and self.board.current_turn == "black" and self.game_state != "checkmate":
			if self.last_p_move:
				print "Calling IA:"
				#try:
				ans = self.ia.move(self.last_p_move)
				cpu_from_cell = self.board[ans.from_r][ans.from_c]
				self.move_log.write(str(self.board.current_turn) + ": " + \
					str(ans.from_r) + "," + str(ans.from_c) +\
					" to " + str(ans.to_r) + "," + str(ans.to_c) + "\n")
				
				#if not self.board.move_piece_in_cell_to(cpu_from_cell, ans.to_r, ans.to_c):
				if not self.board.cpu_move_piece(ans):
					print "IA made an illegal move:",\
						ans.from_r, ans.from_c, "to",\
						ans.to_r, ans.to_c
					raise Exception("IA out of sync!")
				self.board.change_turn()

	#def on_cell_clicked(self, clicked_cell):
	#	if clicked_cell is None:
	#		return
	#	
	#	if clicked_cell.piece is not None:
	#		if clicked_cell != self.selected_cell:
	#			print "Changed selected piece"
	#			self.selected_cell = clicked_cell
	#		else:
	#			print "Unselected piece"
	#			self.selected_cell = None
	#	else:
	#		if self.selected_cell is not None:
	#			print "Move piece to..."
	#			moved = self.board.move_piece_in_cell_to( \
	#			self.selected_cell, clicked_cell.i, \
	#			clicked_cell.j)
	#			
	#			if moved:
	#				print "Piece moved correctly"
	#				self.selected_cell = None
	#			else:
	#				print "Could not move the piece there"
	#			
	#		else:
	#			print "Nothing to do"
	
	def on_cell_clicked(self, clicked_cell):
		'''Handle mouse events from the user. This method gets called
		by the event control code when the user clicks on a cell.'''
		
		if self.rendering_animation or clicked_cell is None:
			return
		
		# Select a piece?
		if clicked_cell.piece is not None and self.selected_cell is None:
			if clicked_cell != self.selected_cell:
				self.selected_cell = clicked_cell
			else:
				self.selected_cell = None
		else:
			# Move piece or deselect
			if self.selected_cell is not None:
				if self.selected_cell.piece.is_turn(self.board.current_turn) and \
				    (self.selected_cell.i != clicked_cell.i  or \
				        self.selected_cell.j != clicked_cell.j):
					self.move_piece(clicked_cell)
				else:
					self.selected_cell = None
			else:
				pass

	def move_piece(self, clicked_cell):
		'''Move the currently selected piece to a new cell. 
		The currently selected piece is at self.selected_cell.'''
		
		if self.game_state == "checkmate":
			return

		was_pawn = self.selected_cell.piece.type == "pawn"

		# Try to move the piece on the board:
		to_i, to_j = clicked_cell.i, clicked_cell.j
		moved = self.board.move_piece_in_cell_to(self.selected_cell, to_i, to_j)
		if moved:
			self.move_log.write(str(self.board.current_turn) + ": " + \
				str(self.selected_cell.i) + "," + str(self.selected_cell.j) +\
				" to " + str(to_i) + "," + str(to_j) + "\n")

			# save move for IA:
			if self.ia:
				from_i = self.selected_cell.i
				from_j = self.selected_cell.j
				#check for crowning:
				if self.board.current_turn == "black" and to_j == 7 and was_pawn:
					self.last_p_move = Crowning((from_i, from_j), (to_i, to_j), \
								self.board[to_i][to_j].piece.type)
				elif self.board.current_turn == "white" and to_j == 0 and was_pawn:
					self.last_p_move = Crowning((from_i),(from_j), (to_i, to_j),\
								self.board[to_i][to_j].piece.type)
				else:
					# just regular move
					self.last_p_move = Move((from_i, from_j),(to_i, to_j))
				
			self.board.change_turn()
			self.selected_cell = None
		else:
			if clicked_cell.piece and \
				self.selected_cell.piece.owner == clicked_cell.piece.owner:
					self.selected_cell = clicked_cell
