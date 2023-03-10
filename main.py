import pygame
from ajustes import *
from level import Level
from sys import exit



class Game:
	def __init__(self):
		#general
		pygame.init()
		self.screen = pygame.display.set_mode((ANCHO, ALTO))
		pygame.display.set_caption('Probando')
		self.clock = pygame.time.Clock()

		self.level = Level(self.screen, self.restart)

	def run(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					exit()
			self.screen.fill('#070707')
			self.level.run()
			pygame.display.update()
			self.clock.tick(FPS)

	def restart(self):
		self.level = Level(self.screen, self.restart)

if __name__ == '__main__':
	game = Game()
	game.run()