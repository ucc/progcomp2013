import pygame
import os

# Dictionary that stores the unicode character representations of the different pieces
# Chess was clearly the reason why unicode was invented
# For some reason none of the pygame chess implementations I found used them!
piece_char = {"white" : {"king" : u'\u2654',
			 "queen" : u'\u2655',
			 "rook" : u'\u2656',
			 "bishop" : u'\u2657',
			 "knight" : u'\u2658',
			 "pawn" : u'\u2659',
			 "unknown" : '?'},
		"black" : {"king" : u'\u265A',
			 "queen" : u'\u265B',
			 "rook" : u'\u265C',
			 "bishop" : u'\u265D',
			 "knight" : u'\u265E',
			 "pawn" : u'\u265F',
			 "unknown" : '?'}}

images = {"white" : {}, "black" : {}}
small_images = {"white" : {}, "black" : {}}

def create_images(grid_sz, font_name=os.path.join(os.path.curdir, "data", "DejaVuSans.ttf")):

	# Get the font sizes
	l_size = 5*(grid_sz[0] / 8)
	s_size = 3*(grid_sz[0] / 8)

	for c in piece_char.keys():
		
		if c == "black":
			for p in piece_char[c].keys():
				images[c].update({p : pygame.font.Font(font_name, l_size).render(piece_char[c][p], True,(0,0,0))})
				small_images[c].update({p : pygame.font.Font(font_name, s_size).render(piece_char[c][p],True,(0,0,0))})		
		elif c == "white":
			for p in piece_char[c].keys():
				images[c].update({p : pygame.font.Font(font_name, l_size+1).render(piece_char["black"][p], True,(255,255,255))})
				images[c][p].blit(pygame.font.Font(font_name, l_size).render(piece_char[c][p], True,(0,0,0)),(0,0))
				small_images[c].update({p : pygame.font.Font(font_name, s_size+1).render(piece_char["black"][p],True,(255,255,255))})
				small_images[c][p].blit(pygame.font.Font(font_name, s_size).render(piece_char[c][p],True,(0,0,0)),(0,0))
	

def load_images(image_dir=os.path.join(os.path.curdir, "data", "images")):
	if not os.path.exists(image_dir):
		raise Exception("Couldn't load images from " + image_dir + " (path doesn't exist)")
	for c in piece_char.keys():
		for p in piece_char[c].keys():
			images[c].update({p : pygame.image.load(os.path.join(image_dir, c + "_" + p + ".png"))})
			small_images[c].update({p : pygame.image.load(os.path.join(image_dir, c + "_" + p + "_small.png"))})
