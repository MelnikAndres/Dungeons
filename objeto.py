import pygame
from ajustes import *
from math import sin

class Objeto(pygame.sprite.Sprite):
	def __init__(self, groups, x, y, type, pick, player):
		super().__init__(groups)

		self.image = pygame.transform.scale2x(pygame.image.load(f'graphics/objetos/{type}.png')).convert_alpha()
		self.rect = self.image.get_rect(bottomleft = (x, y))
		self.hitbox = self.rect
		self.type = type
		self.order = 4

		self.vida = OBJETOS[type]['vida']

		self.invulnerable = False
		self.timer = 0

		self.visibles = [groups[0]]
		self.player = player
		self.pick = pick
		self.check_pick()

	def check_pick(self):
		if self.pick == 'heal':
			self.player.heal = False
		elif self.pick == 'thunder':
			self.player.thunder = False
		elif self.pick == 'skull':
			self.player.skull = False
		elif self.pick == 'dash':
			self.player.dash = False


	def wave_value(self):
		value = sin(pygame.time.get_ticks())
		if value >= 0:
			return 255
		return 0

	def check_daño(self):
		if self.invulnerable:
			if not self.timer:
				self.timer = pygame.time.get_ticks()
			self.image.set_alpha(self.wave_value())

	def check_vida(self):
		if self.vida <= 0:
			self.kill()
			Pickup(self.visibles, self.rect.left + 32, self.rect.bottom - 32, self.pick, self.player)


	def cooldown(self):
		current_time = pygame.time.get_ticks()

		if current_time - self.timer > 1000:
			self.timer = 0
			self.invulnerable = False
			self.image.set_alpha(255)


	def update(self):
		self.check_daño()
		self.check_vida()
		self.cooldown()

class Pickup(pygame.sprite.Sprite):
	def __init__(self, groups, x , y, type, player):
		super().__init__(groups)
		self.order = 4
		self.image = pygame.image.load(f'graphics/pickups/{type}.png').convert_alpha()
		self.rect = self.image.get_rect(center = (x, y))
		self.hitbox = self.rect
		self.pick = type
		self.player = player

	def update(self):
		if self.hitbox.colliderect(self.player.hitbox):
			if self.pick == 'heal':
				self.player.heal = True
			elif self.pick == 'thunder':
				self.player.thunder = True
			elif self.pick == 'skull':
				self.player.skull = True
			elif self.pick == 'dash':
				self.player.dash = True
			self.kill()