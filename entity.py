import pygame
from math import sin
from ajustes import TILESIZE

class Entity(pygame.sprite.Sprite):
	def __init__(self, groups):
		super().__init__(groups)

		self.direction = pygame.math.Vector2()
		self.gravedad = 0
		self.en_piso = True


	def move(self, speed):
		self.hitbox.x += self.direction.x * speed
		self.collision('horizontal', self.obstacle_sprites)
		if not self.dashing:
			self.collision('horizontal', self.atacables)
		self.hitbox.y += self.direction.y * speed + self.gravedad
		self.en_piso = self.collision('vertical', self.obstacle_sprites)
		if not self.dashing:
			self.en_piso += self.collision('vertical', self.atacables)
		self.rect.midbottom = self.hitbox.midbottom

		if not self.en_piso:
			self.gravedad += 3
		

	def collision(self, direccion, obstacles):
		if direccion == 'horizontal':
			for sprite in obstacles:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.x > 0:#moving right
						self.hitbox.right = sprite.hitbox.left
					elif self.direction.x < 0: #moving left
						self.hitbox.left = sprite.hitbox.right


		elif direccion == 'vertical':
			for sprite in obstacles:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.gravedad < 0:#moving up
						self.hitbox.top = sprite.hitbox.bottom
						self.gravedad = 0
					else:
						self.hitbox.bottom = sprite.hitbox.top
						self.gravedad = 0
						return True
		return False


	def wave_value(self):
		value = sin(pygame.time.get_ticks())
		if value >= 0:
			return 255
		return 0