import pygame
from support import *
from ajustes import *

class StaticUI(pygame.sprite.Sprite):
	def __init__(self, groups):
		super().__init__(groups)

		self.image = pygame.image.load('graphics/gui/gui_top.png').convert_alpha()
		self.rect = self.image.get_rect(topleft = (0, 0))
		self.order = 1


class DinamicUI(pygame.sprite.Sprite):
	def __init__(self, groups, player, x, y, width, height, color, tipo, alpha = 255):
		super().__init__(groups)

		self.image = pygame.surface.Surface((width, height))
		self.image.fill(color)
		self.rect = self.image.get_rect(topleft = (x, y))
		self.player = player
		self.ratio = width/self.player.vida if color == 'red' else width/self.player.mana
		self.height = height
		self.color = color
		self.alpha = alpha
		self.tipo = tipo
		self.order = 5


	def update(self):
		if self.tipo == 'heal':
			vida = self.player.vida + self.player.heal_acum if self.player.vida >= 0 else 0
			vida = 100 if vida > 100 else vida

		elif self.tipo == 'vida':
			vida = self.player.vida if self.player.vida >= 0 else 0

		elif self.tipo == 'daño':
			vida = self.player.last_dmg if self.player.last_dmg < self.player.vida else self.player.vida
			vida = 0 if vida < 0 else vida

		elif self.tipo == 'mana':
			vida = self.player.mana if self.player.mana >= 0 else 0
			
		

		self.image = pygame.surface.Surface((int(self.ratio * vida), self.height)).convert_alpha()
		self.image.fill(self.color)
		self.image.set_alpha(self.alpha)

class Cooldown(pygame.sprite.Sprite):
	def __init__(self,groups, type, timer):
		super().__init__(groups)

		self.animations = import_folder('graphics/cooldown')
		self.image = self.animations[0]
		self.rect = self.image.get_rect(topleft = COOLDOWNS[type]['pos'])
		self.cd = COOLDOWNS[type]['cd']	
		self.timer = timer
		self.image_index = 0
		self.order = 1

	def update(self):

		current_time = pygame.time.get_ticks()
		self.image_index =  ((current_time - self.timer)/self.cd) * 4
		if self.image_index >= len(self.animations):
			self.kill()
			return

		self.image = self.animations[int(self.image_index)]

class Bloqueado(pygame.sprite.Sprite):
	def __init__(self,groups, type):
		super().__init__(groups)

		self.image = pygame.image.load('graphics/bloqueado/block.png')
		self.rect = self.image.get_rect(topleft = COOLDOWNS[type]['pos'])
		self.order = 1
