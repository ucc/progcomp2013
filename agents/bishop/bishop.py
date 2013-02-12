#!/usr/bin/python -u

from qchess import *

graphics_enabled = True

"""
	This is a wrapper to AgentBishop, which can now be found directly in qchess as one of the internal agents
	As well as wrapping, it will also show AgentBishop's thought processes in graphics, which is kind of cool

	So basically, using `./qchess.py @internal:AgentBishop` is better, unless you want to see the graphics
"""

	
# Horrible messy graphics class that draws what the agent is doing, kind of useful for testing
class AgentBishop_Graphics(GraphicsThread):
	def __init__(self, board, title):
		GraphicsThread.__init__(self, board, title, grid_sz = [64,64])
		self.choice = None
		self.moves = None

	def run(self):
		square_img = pygame.Surface((self.grid_sz[0], self.grid_sz[1]),pygame.SRCALPHA) # A square image
		while not self.stopped():
		
			self.board.display_grid(window = self.window, grid_sz = self.grid_sz)	

			# Draw choice of the AI
			if agent.choice != None:
				mp = [self.grid_sz[i] * [agent.choice.x, agent.choice.y][i] for i in range(2)]
				square_img.fill(pygame.Color(0,255,0,64))
				self.window.blit(square_img, mp)

			# Draw calculated choices for the piece clicked on
			if self.choice != None:
				mp = [self.grid_sz[i] * [self.choice.x, self.choice.y][i] for i in range(2)]
				square_img.fill(pygame.Color(0,0,255,128))
				self.window.blit(square_img, mp)

			# Draw the choices the AI calculated from the selection of the chosen piece
			if agent.choice != None and agent.choice.selected_moves != None:
				for m in agent.choice.selected_moves:
					mp = [m[0][i] * self.grid_sz[i] for i in range(2)]
					square_img.fill(pygame.Color(128,128,255,128))
					self.window.blit(square_img, mp)
					font = pygame.font.Font(None, 14)
					text = font.render("{0:.2f}".format(round(m[1],2)), 1, pygame.Color(255,0,0))
					mp[0] = mp[0] + self.grid_sz[0] - text.get_width()
					mp[1] = mp[1] + self.grid_sz[1] - text.get_height()
					self.window.blit(text, mp)


			# Draw the choice the AI's chosen piece could have actually made
			if agent.choice != None and agent.choice.last_moves != None:
				for m in agent.choice.last_moves:
					mp = [m[0][i] * self.grid_sz[i] for i in range(2)]
					square_img.fill(pygame.Color(255,0,0,128))
					self.window.blit(square_img, mp)
					font = pygame.font.Font(None, 14)
					text = font.render("{0:.2f}".format(round(m[1],2)), 1, pygame.Color(0,0,255))
					mp[0] = mp[0] + self.grid_sz[0] - text.get_width()
					self.window.blit(text, mp)

			


			if self.moves != None:
				for m in self.moves:
					mp = [m[0][i] * self.grid_sz[i] for i in range(2)]
					square_img.fill(pygame.Color(255,0,255,128))
					self.window.blit(square_img, mp)
					font = pygame.font.Font(None, 14)
					text = font.render("{0:.2f}".format(round(m[1],2)), 1, pygame.Color(0,0,0))
					self.window.blit(text, mp)
			
			
	
			self.board.display_pieces(window = self.window, grid_sz = self.grid_sz)

			pygame.display.flip()
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.stop()
					break
				elif event.type == pygame.MOUSEBUTTONDOWN:
					m = [event.pos[i] / self.grid_sz[i] for i in range(len(event.pos))]
					p = agent.board.grid[m[0]][m[1]]
					if p == None:
						continue
					self.choice = p
					self.last_moves = self.choice.last_moves
					self.selected_moves = self.choice.selected_moves
					if event.button == 3 or self.choice.last_moves == None:
						self.moves = agent.prioritise_moves(self.choice)
					else:
						self.moves = self.choice.last_moves
					
				elif event.type == pygame.MOUSEBUTTONUP:
					if self.choice == None:
						continue
					self.choice.last_moves = self.last_moves
					self.choice.selected_moves = self.selected_moves
					self.choice = None
					self.moves = None
					
		pygame.display.quit()				

if __name__ == "__main__":
	
	if sys.argv[1] == "--no-graphics":
		graphics_enabled = False

	colour = sys.stdin.readline().strip("\r\n")
	agent = AgentBishop(sys.argv[0], colour)

	if graphics_enabled:
		graphics = AgentBishop_Graphics(agent.board, "Agent Bishop ("+agent.colour+") DEBUG")
		graphics.start()
	run_agent(agent)
	
	if graphics_enabled:
		graphics.stop()
		graphics.join()
