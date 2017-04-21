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

import pygame
from piece import *

class Cell:

	def __init__(self, i, j, size, color, piece = None):
		self.color = color
		self.piece = piece
		self.size = size
		self.i = i
		self.j = j
	
	def render_background(self, surface):
		size = self.size
		tx = self.i * size
		ty = self.j * size
		
		surface.fill(self.color, pygame.Rect(tx, ty, size, size))
	
	def render_foreground(self, surface):
		if self.piece is not None:
			size = self.size
			tx = self.i * size
			ty = self.j * size
			self.piece.render(surface, tx, ty, size)
		
	def render_as_highlight(self, surface, color = (0, 255, 0)):
		size = self.size
		tx = self.i * size
		ty = self.j * size
		
		#surface.fill((0, 0, 0), pygame.Rect(tx, ty, size, size))
		surface.fill(color, pygame.Rect(tx+5, ty+5, size-10, size-10))
		
	#def render(self, surface):
	#	size = self.size
	#	tx = self.i * size
	#	ty = self.j * size
	#	
	#	#print tx, ty, tx + size, ty + size
	#	
	#	surface.fill(self.color, pygame.Rect(tx, ty, size, size))
	#	if self.piece is not None:
	#		self.piece.render(surface, tx, ty, size)
			
	def contains(self, x, y):
		tx = self.i * self.size
		ty = self.j * self.size
		
		if x > tx and x < tx + self.size and \
			y > ty and y < ty + self.size:
				return True
				
	def pick(self):
		if self.piece:
			self.piece.on_pick()
			
