import pygame

class Tile(pygame.sprite.Sprite):
	def __init__(self, x, y, groups, sprite_type, surface = pygame.surface.Surface((32, 32))):
		super().__init__(groups)
		self.init_pos = (x, y)
		self.sprite_type = sprite_type
		self.image = pygame.transform.scale2x(surface).convert_alpha()
		self.rect = self.image.get_rect(bottomleft = (x, y))
		self.hitbox = self.rect
		self.direction = pygame.math.Vector2()
		if sprite_type == 'fondo' or sprite_type == 'invisible':
			self.order = 20
		elif sprite_type == 'plataforma':
			self.order = 6
		elif sprite_type == 'dark':
			self.order = 0