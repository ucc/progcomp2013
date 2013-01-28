#!/usr/bin/python

import sys
from images import *

def main(argv):
	pygame.init()
	try:
		target = str(argv[1])
	except:
		target = os.path.join(os.path.curdir, "..","data","images")

	try:
		grid_size = int(argv[2])
	except:
		grid_size = 64
		

	if not os.path.exists(target):
		os.mkdir(target)

	create_images([grid_size, grid_size], font_name=os.path.join(os.path.curdir, "..", "data", "DejaVuSans.ttf"))

	for colour in piece_char.keys():
		for piece in piece_char[colour].keys():
			pygame.image.save(images[colour][piece], os.path.join(target,str(colour)+"_"+str(piece)+".png"))
			pygame.image.save(small_images[colour][piece], os.path.join(target,str(colour)+"_"+str(piece)+"_small.png"))

	pygame.quit()
	return 0

if __name__ == "__main__":
	sys.exit(main(sys.argv))
