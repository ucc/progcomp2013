import random

# I know using non-abreviated strings is inefficient, but this is python, who cares?
# Oh, yeah, this stores the number of pieces of each type in a normal chess game
piece_types = {"pawn" : 8, "bishop" : 2, "knight" : 2, "rook" : 2, "queen" : 1, "king" : 1, "unknown" : 0}

# Class to represent a quantum chess piece
class Piece():
	def __init__(self, colour, x, y, types):
		self.colour = colour # Colour (string) either "white" or "black"
		self.x = x # x coordinate (0 - 8), none of this fancy 'a', 'b' shit here
		self.y = y # y coordinate (0 - 8)
		self.types = types # List of possible types the piece can be (should just be two)
		self.current_type = "unknown" # Current type
		self.choice = -1 # Index of the current type in self.types (-1 = unknown type)
		
		
		self.last_state = None
		
		self.move_pattern = None
		self.coverage = None

		

	def init_from_copy(self, c):
		self.colour = c.colour
		self.x = c.x
		self.y = c.y
		self.types = c.types[:]
		self.current_type = c.current_type
		self.choice = c.choice
		
		self.last_state = None
		self.move_pattern = None

	

	# Make a string for the piece (used for debug)
	def __str__(self):
		return str(self.colour) + " " + str(self.current_type) + " " + str(self.types) + " at " + str(self.x) + ","+str(self.y)  

	# Draw the piece in a pygame surface
	def draw(self, window, grid_sz = [80,80], style="quantum"):

		# First draw the image corresponding to self.current_type
		img = images[self.colour][self.current_type]
		rect = img.get_rect()
		if style == "classical":
			offset = [-rect.width/2, -rect.height/2]
		else:
			offset = [-rect.width/2,-3*rect.height/4] 
		window.blit(img, (self.x * grid_sz[0] + grid_sz[0]/2 + offset[0], self.y * grid_sz[1] + grid_sz[1]/2 + offset[1]))
		
		
		if style == "classical":
			return

		# Draw the two possible types underneath the current_type image
		for i in range(len(self.types)):
			if always_reveal_states == True or self.types[i][0] != '?':
				img = small_images[self.colour][self.types[i]]
			else:
				img = small_images[self.colour]["unknown"] # If the type hasn't been revealed, show a placeholder

			
			rect = img.get_rect()
			offset = [-rect.width/2,-rect.height/2] 
			
			if i == 0:
				target = (self.x * grid_sz[0] + grid_sz[0]/5 + offset[0], self.y * grid_sz[1] + 3*grid_sz[1]/4 + offset[1])				
			else:
				target = (self.x * grid_sz[0] + 4*grid_sz[0]/5 + offset[0], self.y * grid_sz[1] + 3*grid_sz[1]/4 + offset[1])				
				
			window.blit(img, target) # Blit shit
	
	# Collapses the wave function!		
	def select(self):
		if self.current_type == "unknown":
			self.choice = random.randint(0,1)
			if self.types[self.choice][0] == '?':
				self.types[self.choice] = self.types[self.choice][1:]
			self.current_type = self.types[self.choice]
		return self.choice

	# Uncollapses (?) the wave function!
	def deselect(self):
		#print "Deselect called"
		if (self.x + self.y) % 2 != 0:
			if (self.types[0] != self.types[1]) or (self.types[0][0] == '?' or self.types[1][0] == '?'):
				self.current_type = "unknown"
				self.choice = -1
			else:
				self.choice = 0 # Both the two types are the same

	# The sad moment when you realise that you do not understand anything about a subject you studied for 4 years...
