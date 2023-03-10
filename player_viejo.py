import pygame
from ajustes import *
from entity import Entity
from support import import_folder

class Player(Entity):
	def __init__(self, x, y, groups, obstacle_sprites, atacables):
		super().__init__(groups)
		
		#general
		self.import_player_assets()

		self.image_index = 0
		self.image = self.animations['idle_right'][self.image_index]

		self.rect = self.image.get_rect(bottomleft = (x, y)) 
		self.hitbox = self.rect.inflate(-40, -20)

		#stats
		self.speed = PLAYER['speed']
		self.vida = PLAYER['vida']
		self.daño = PLAYER['ataque']

		#status
		self.flip = 'right'
		self.accion = 'idle_'
		self.bussy = False
		self.saltando = False
		self.crouching = False
		self.atacando = False
		self.invulnerable = False
		self.dañado_timer = 0

		#exception
		self.jumpattack_index = 0

		#sprite group
		self.obstacle_sprites = obstacle_sprites
		self.atacables = atacables
		self.ataque = None

	def import_player_assets(self):
		player_path = 'graphics/warrior/'
		self.animations = {'idle_right': [], 'run_right': [], 'jump_right': [], 
							'attack_right': [], 'crouch_right': [], 'hurt_right': [], 
							'jumpattack_right': [], 'crouchattack_right': [],
							'crouchreverse_right': []}

		animations_left = {'idle_left': [], 'run_left': [], 'jump_left': [], 
							'attack_left': [], 'crouch_left': [], 'hurt_left': [], 
							'jumpattack_left': [], 'crouchattack_left': [],
							'crouchreverse_left': []}

		for animation in self.animations:
			full_path = player_path + animation
			self.animations[animation] = import_folder(full_path, scale = True)

			for animation_flip in self.animations[animation]:
				animation = animation.split('_')[0] + '_left'
				animations_left[animation].append(pygame.transform.flip(animation_flip, True, False))

		self.animations.update(animations_left)

	def input(self):
		if self.bussy:
			self.direction.x = 0
			return

		keys = pygame.key.get_pressed()


		if keys[pygame.K_UP]:
			if not self.atacando:
				self.accion = 'jump_'
			if not self.saltando:
				self.gravedad = -20
				self.image_index = 0
				self.saltando = True
			elif self.gravedad > -30:
				self.gravedad -= 1

		if keys[pygame.K_RIGHT]:
			self.flip = 'right'
			self.direction.x = 1

		elif keys[pygame.K_LEFT]:
			self.flip = 'left'
			self.direction.x = - 1

		else:
			self.direction.x = 0

		if keys[pygame.K_DOWN] and not self.saltando:
			self.direction.x = 0
			self.accion = 'crouch_'
			self.direction.x = 0
			self.crouching = True

		elif self.crouching:
			self.crouching = False
			self.accion = 'idle_'

		if keys[pygame.K_e] and not self.atacando:
			
			self.bussy = True
			self.atacando = True
			if self.crouching:
				self.image_index = 0
				self.accion = 'crouchattack_'
			elif self.saltando:
				self.accion = 'jumpattack_'
				self.bussy = False
				self.jumpattack_index = 0
			else:
				self.image_index = 0
				self.accion = 'attack_'
				self.image_index = 0

	def animate(self):

		if self.invulnerable and self.bussy:
			if self.accion != 'hurt_':
				self.accion = 'hurt_'
				self.image_index = 0

			self.animation(0.15, loop = False)

			if self.image_index == len(self.animations[f'{self.accion}{self.flip}']) - 1:
				self.bussy = False
				self.input()


		elif self.accion == 'jump_':

			self.animation(0.12, loop = False)

		elif self.accion == 'attack_':
			self.animation(0.3, end_action = True)

			if 1.1 < self.image_index < 1.3 :
				self.crear_ataque('suelo')

			elif int(self.image_index) > 2 and self.ataque:
				self.ataque.kill()


		elif self.accion == 'crouchattack_':
			self.animation(0.3, end_action = True)

			if 1.1 < self.image_index < 1.3 :
				self.crear_ataque('crouch')

			elif int(self.image_index) > 2 and self.ataque:
				self.ataque.kill()

		elif self.accion == 'jumpattack_':
			self.jumpattack_animation()

			if 1.1 < self.jumpattack_index < 1.3 :
				self.crear_ataque('aire')

			elif self.ataque:
				self.ataque.kill()

		elif self.accion == 'crouchreverse_':

			self.animation(0.25, end_action = True)

		elif self.accion == 'crouch_':

			self.animation(0.15)

		elif self.direction.x !=0:

			if self.accion != 'run_':
				self.accion = 'run_'
				self.image_index = 0

			self.animation(self.speed/40)
		else:


			if self.accion != 'idle_':
				self.accion = 'idle_'
				self.image_index = 0

			self.debug_barato()

			self.animation(0.15)

	def animation(self, velocidad, loop = True, end_action = False):
		self.image_index += velocidad
		if self.image_index >= len(self.animations[f'{self.accion}{self.flip}']): 

			if loop:
				self.image_index = 0
			else:
				self.image_index = len(self.animations[f'{self.accion}{self.flip}']) - 1

			if end_action:
				self.accion = 'idle_'
				self.bussy = False
				self.input()

		self.image = self.animations[f'{self.accion}{self.flip}'][int(self.image_index)]

		self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
		self.hitbox.center = self.rect.center

	def jumpattack_animation(self):
		self.image_index += 0.12
		self.jumpattack_index += 0.3
		if self.jumpattack_index >= len(self.animations[f'{self.accion}{self.flip}']): 
			self.accion = 'jump_'
			self.image = self.animations[f'{self.accion}{self.flip}'][int(self.image_index)]
		else:
			self.image = self.animations[f'{self.accion}{self.flip}'][int(self.jumpattack_index)]

		self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
		self.hitbox.center = self.rect.center

	def check_status(self):
		self.check_salto()
		self.check_attack()
		self.check_pos()
		self.check_dañado()
		self.check_cooldowns()
		
		
	def check_salto(self):
		if self.gravedad < 0:
			return

		if self.gravedad > 6:
			self.saltando = True

		elif self.saltando and self.en_piso:
			self.saltando = False

		if self.gravedad > 21 and self.accion != 'jump_':
			self.accion = 'jump_'
			self.image_index = 2.5
			self.saltando = True
			return
		
		if (self.accion == 'jump_' or self.accion == 'jumpattack_') and self.en_piso:
			if self.image_index < 3:
				self.accion = 'idle_'
				self.image_index = 0
				self.saltando = False
			else:
				self.accion = 'crouchreverse_'
				self.image_index = 0
				self.saltando = False
				self.bussy = True

	def check_pos(self):
		if self.hitbox.top > 1396:
			self.hitbox.bottom = 0

	def check_attack(self):
		if self.atacando and self.accion not in ('attack_', 'jumpattack_', 'crouchattack_', 'jump_'):
			self.atacando = False
		if self.atacando and not self.saltando and self.accion == 'jump_':
			self.atacando = False

	def check_dañado(self):

		if self.invulnerable:
			alpha = self.wave_value()
			self.image.set_alpha(alpha)
			if not self.dañado_timer:
				self.bussy = True
				self.dañado_timer = pygame.time.get_ticks()

	def check_cooldowns(self):
		current_time = pygame.time.get_ticks()

		if current_time - self.dañado_timer > 1000:
			self.invulnerable = False
			self.image.set_alpha(255)
			self.dañado_timer = 0

	def crear_ataque(self, tipo):

		if not self.ataque:
			self.ataque = Allyattack(tipo, self.rect.centerx, self.rect.centery)

		if self.flip == 'left':
			self.ataque.image = self.ataque.img_left
		else:
			self.ataque.image = self.ataque.img_right

		self.ataque.rect.center = self.rect.center

		for sprite in self.atacables:
			if sprite.hitbox.colliderect(self.rect):
				if pygame.sprite.collide_mask(self.ataque, sprite):
					sprite.vida -= self.daño
					sprite.invulnerable = True
					self.ataque.kill()

	def debug_barato(self):
		if self.bussy and self.accion == 'idle_':
			self.bussy = False

	def update(self):
		self.collision('horizontal', self.atacables)
		self.check_status()
		self.input()
		self.move(self.speed)
		
		self.animate()


class Allyattack(pygame.sprite.Sprite):
	def __init__(self, type, x, y):
		super().__init__()

		
		self.img_right = pygame.transform.scale2x(pygame.image.load(f'graphics/hero/ataques/ataque_{type}.png').convert_alpha())
		self.img_left = pygame.transform.flip(self.img_right, True, False)
		self.image = self.img_right
		self.rect = self.image.get_rect(bottomleft = (x, y))
		self.hitbox = self.rect.inflate(0, 0)
