#!/usr/bin/env python
#
#    Ceibal Chess - A chess activity for Sugar.
#    Copyright (C) 2008, 2009 Alejandro Segovia <asegovi@gmail.com>
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

import sys, pygame, time, traceback
from board import *
from piece import *
from boardcontroller import *
#from messenger import *
from menu import *
from ui import *
from resourcemanager import image_manager

def clear(surface):
	surface.fill((0, 0, 0))
		
def update():
	pygame.display.flip()

def main(requested_w, requested_h):
	pygame.init()

	#Messages
	game_messages = {}
	game_messages["checkmate"] = Message("Checkmate!", 10, 40, (255, 0, 0))
	game_messages["check"] = Message("Check", 10, 40, (128, 0, 0))
	game_messages["none"] = Message("", 10, 40)


	#XO: 1200x900
	scr_w = requested_w
	scr_h = requested_h
	if len(sys.argv) == 3:
		scr_w = int(sys.argv[1])
		scr_h = int(sys.argv[2])
	
	size = width, height = scr_h - 70, scr_h - 70

	#Screen config
	screen = pygame.display.set_mode((scr_w, scr_h))
	pygame.display.set_caption("Ceibal-Chess")

	surface = pygame.Surface(size)
	bg_img = image_manager.get_image("bg.png")
	bg_img = pygame.transform.scale(bg_img, (scr_w, scr_h))
	print scr_w, scr_h

	#Center chessboard in screen
	screen_rect = screen.get_rect()
	sface_rect = surface.get_rect()
	delta_x = (screen_rect.w - sface_rect.w) / 2
	delta_y = (screen_rect.h - sface_rect.h) / 2

	clock = pygame.time.Clock()

	board = Board(width, height)

	menu_opts = ["New CPU Game", "Player vs. Player", \
			"Practice Mode", "Credits", "Quit Ceibal-Chess"]
	menu = Menu(scr_h, scr_h, menu_opts)
	menu.visible = True

	#LOG related:
	#Unique identifier for this game (used for logs)
	game_code = str(int(time.time()))

	try:
		logpath = os.path.join(os.environ["HOME"], ".cchess")
	except:
		logpath = ".cchess"
		
	if not os.path.isdir(logpath):
		os.mkdir(logpath)
	
	#Controller
	controller = BoardController(board, MODE_P_VS_P, game_code, logpath)
	controller.init_board()

	#FPS
	#messenger.messages["FPS"] = Message("FPS: (calculating)", 10, 10)
	fps = 0
	last_time = time.time()

	#Create UI Elements:
	turn_display = StatePanel(scr_w - scr_w/6, scr_h/40, 120, 120)

	#Post an ACTIVEEVENT to render the first time
	pygame.event.post(pygame.event.Event(pygame.ACTIVEEVENT))

	while 1:
		fps += 1
		new_time = time.time()
		if new_time - last_time > 5:
			#print "FPS:", fps/5.0
			#messenger.messages["FPS"] = Message("FPS: " + str(fps/5.0), 10, 10)
			last_time = new_time
			fps = 0
		
		#clock.tick(30)
		
		try:
			if not menu.visible:
				controller.update(0)

			#Event handling
			event = pygame.event.wait()
			#discard mousemotion event (too expensive)
			while event.type == pygame.MOUSEMOTION:
				event = pygame.event.wait()

			if event.type == pygame.QUIT:
				controller.shutdown()
				sys.exit(0)

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					menu.toggle_visible()
				#else:
				#	controller.shutdown()
				#	sys.exit(0)

			if event.type == pygame.MOUSEBUTTONDOWN:
				x, y = pygame.mouse.get_pos()

				if not menu.visible:
					clicked_cell = board.pick(x-delta_x, y-delta_y)
					controller.on_cell_clicked(clicked_cell)
				else:
					option = menu.on_click(x-delta_x, y-delta_y)
					if option:
						if option == menu_opts[4]:
							controller.shutdown()
							sys.exit(0)
						elif option in menu_opts[0:2]:
							game_mode = MODE_P_VS_CPU
							if option == menu_opts[1]:
								game_mode = MODE_P_VS_P
							board = Board(width, height)
							controller.shutdown("Started new game")
							controller = BoardController(board, game_mode, game_code, logpath)
							controller.init_board()
							menu.visible = False
							turn_display.set_state("move_white")
			if not menu.visible:
				print "Checking if king is checkmated:"
				t_ini = time.time()
				checkmated = board.king_is_checkmated(board.current_turn)
				print "Check if checkmate for %s took %.5f secs" % \
					(board.current_turn, time.time() - t_ini)

				if checkmated:
					#print "Checkmate for", board.current_turn
					#messenger.messages["check"] = game_messages["checkmate"]
					controller.game_state = "checkmate"
					turn_display.set_state("checkmate_" + board.current_turn)

				elif board.king_is_checked(board.current_turn):
					#messenger.messages["check"] = game_messages["check"]
					turn_display.set_state("check_" + board.current_turn)
				else:
					#messenger.messages["check"] = game_messages["none"]
					turn_display.set_state("move_" + board.current_turn)

		except Exception, ex:
			print "Caught exception, dumping and cleaning up..."
			#Dump to stdout
			print ex.message
			traceback.print_exc(file=sys.stdout)
			
			#Dump move log and close IA
			controller.shutdown(ex.message)	

			#Dump trace to file
			trace_file = open(os.path.join(logpath, game_code + ".trace"), "w")
			traceback.print_exc(file=trace_file)
			trace_file.close()
			
			#Dump screen to image file
			pygame.image.save(screen, os.path.join(logpath, game_code + ".png"))
			
			print "Ceibal-Chess is done crashing... Game code was: " + game_code
			print "Have a nice day :)"
			sys.exit(-1)

		#time visual update:
		t_ini = time.time()

		clear(screen)	
		clear(surface)
		
		screen.blit(bg_img, bg_img.get_rect())
		
		board.render_background(surface)
		
		if controller.selected_cell is not None:
			board.render_moves_for_piece_in_cell(surface, controller.selected_cell)
			controller.selected_cell.render_foreground(surface)
		
		board.render_foreground(surface)

		menu.render(surface)

		screen.blit(surface, sface_rect.move(delta_x, delta_y))
		
		if not menu.visible:
			turn_display.render(screen)
		
		messenger.render_messages(screen)
		
		update()
		
		print "Visual refresh took %.5f secs" % (time.time() - t_ini)

if __name__ == "__main__":
	main(1000, 700)



