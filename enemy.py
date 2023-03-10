import pygame
from entity import Entity
from support import import_folder
from random import choice
from ajustes import *
from gui import DinamicUI

class Enemy(Entity):
	def __init__(self, x, y, groups, enemy_type, player, movimiento, atacables):
		super().__init__(groups)
		#general
		self.type = enemy_type
		self.import_enemy_assets()
		self.player = player
		self.init_pos = x, y-1
		self.movimiento = movimiento
		self.order = 3

		#imagen
		self.image_index = 0

		self.flip = choice(('left', 'right'))

		self.image = self.animations[f'idle_{self.flip}'][self.image_index]

		self.rect = self.image.get_rect(bottomleft = (x, y)) 
		self.hitbox = self.rect.inflate(ENEMIGOS[self.type]['inflate'])
		self.hitbox.midbottom = self.rect.midbottom
		

		#ataque
		self.ataque = Enemyattack(enemy_type, x, y)
		

		#status
		self.distancia = {'x': 0, 'y': 0}
		self.dead = False
		self.volviendo = False
		self.speed = ENEMIGOS[self.type]['speed']
		self.vida = ENEMIGOS[self.type]['vida']
		self.mana = 0
		self.daño = ENEMIGOS[self.type]['ataque']
		self.atq_speed = ENEMIGOS[self.type]['atq_speed']
		self.range = ENEMIGOS[self.type]['range']
		self.notice = ENEMIGOS[self.type]['notice']
		self.run = ENEMIGOS[self.type]['run']
		self.special = ENEMIGOS[self.type]['special']
		self.despawn_timer = 0
		self.atacando = False
		self.invulnerable = False
		self.dañado_timer = 0
		self.triggered = False
		self.stun = False
		self.effect = None
		self.effect_timer = None
		self.effect_duration = 0
		self.ticks = 0
		self.dot = False

		#vida
		self.barra = DinamicUI(groups[0], self, 0, 0, self.rect.width, 10, 'red', 'vida')
		self.barra.rect.midbottom = self.hitbox.midtop
		self.efecto = None

		#atacables
		self.atacables = atacables
		self.visibles = groups[0]


	def import_enemy_assets(self):
		enemy_path = f'graphics/{self.type}/'
		self.animations = {'idle_right': [], 'attack_right': [], 'dead_right': [], 'walk_right': [], 'hit_right': [],}

		animations_left = {'idle_left': [], 'attack_left': [], 'dead_left': [], 'walk_left': [], 'hit_left': [],}

		for animation in self.animations:
			full_path = enemy_path + animation
			self.animations[animation] = import_folder(full_path, scale = True)

			for animation_flip in self.animations[animation]:
				animation = animation.split('_')[0] + '_left'
				animations_left[animation].append(pygame.transform.flip(animation_flip, True, False))

		

		self.animations.update(animations_left)

		for key in self.animations:
			for i in range(len(self.animations[key])):
				self.animations[key][i] = pygame.transform.scale2x(self.animations[key][i]).convert_alpha()

	def animate(self):
		
		if self.vida <= 0 or self.dead:

			if not self.dead:
				self.image_index = 0
				self.dead = True
				self.direction.x = 0

			self.animation(0.15, 'dead_', loop = False)

			if not self.despawn_timer:
				self.despawn_timer = pygame.time.get_ticks()

			self.hitbox = self.hitbox.inflate(-self.hitbox.width, -self.hitbox.height)
			self.hitbox.midbottom = self.rect.midbottom

		elif self.volviendo:

			self.animation(0.4, 'walk_')

		elif self.stun:
			self.direction.x = 0

			self.animation(0.2, 'hit_')

			if self.image_index == 0:
				self.stun = False

		elif (abs(self.distancia['x']) < self.range[0] and abs(self.distancia['x']) > self.run and abs(self.distancia['y']) < self.range[1]) or self.atacando:


			if not self.atacando:
				self.image_index = 0
				self.atacando = True



			self.animation(self.atq_speed, 'attack_')

			if int(self.image_index) == ENEMIGOS[self.type]['attack_index']:
				self.crear_ataque()

			self.direction.x = 0

			if self.image_index == 0:
				self.atacando = False

		elif self.direction.x != 0:

			self.animation(0.4, 'walk_')

		else:
			self.animation(0.15, 'idle_')


	def  animation(self, velocidad, accion, loop = True):
		self.image.set_alpha(255)
		self.image_index += velocidad
		if self.image_index >= len(self.animations[f'{accion}{self.flip}']): 

			if loop:
				self.image_index = 0
			else:
				self.image_index = len(self.animations[f'{accion}{self.flip}']) - 1

		self.image = self.animations[f'{accion}{self.flip}'][int(self.image_index)]

		self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
		self.hitbox.midbottom = self.rect.midbottom

	def actualizar_direction(self):

		self.distancia['x'] = self.player.rect.centerx - self.rect.centerx
		self.distancia['y'] = self.player.rect.centery - self.rect.centery

		if self.dead or self.volviendo or self.atacando:
			return False

		if  abs(self.distancia['x']) < self.notice[0] and abs(self.distancia['x']) > 5 and abs(self.distancia['y']) < self.notice[1] or self.triggered:
			self.triggered = True

			if self.distancia['x'] < 0:
				self.direction.x = -1
				self.flip = 'left'
			else:
				self.direction.x = 1
				self.flip = 'right'

			if abs(self.distancia['x']) <= self.run and abs(self.distancia['y']) < 64:
				self.direction.x = 1 if self.direction.x == -1 else -1
				self.flip = 'right' if self.flip == 'left' else 'left'

			return True
			
		else:
			self.direction.x = 0
			return False

	def move_enemy(self):
		self.hitbox.x += self.direction.x * (self.speed if not self.volviendo else self.speed*2)

		if self.hitbox.colliderect(self.player.hitbox) and not self.player.dashing:
			self.hitbox.x -= self.direction.x * (self.speed if not self.volviendo else self.speed*2)

		if not self.volviendo:
			for sprite in self.atacables:
				if sprite != self and sprite.type == self.type:
					if self.hitbox.colliderect(sprite.hitbox.inflate(-20, 0)):
						self.hitbox.x -= self.direction.x * self.speed 


		self.rect.midbottom = self.hitbox.midbottom

		

		for sprite in self.movimiento:
			if sprite.hitbox.colliderect(self.hitbox):
				if sprite.sprite_type == 'vuelta':

					if self.rect.x - self.init_pos[0] < 0:
						self.direction.x = 1
						self.flip = 'right'
					else:
						self.direction.x = -1
						self.flip = 'left'
				
					self.volviendo = True
					self.triggered = False

				elif sprite.sprite_type == 'bloque':
					self.hitbox.x -= self.direction.x * self.speed 
					self.rect.midbottom = self.hitbox.midbottom
					if self.direction.x == -1:
						self.hitbox.left = sprite.hitbox.right
					else:
						self.hitbox.right = sprite.hitbox.left

					self.rect.midbottom = self.hitbox.midbottom
					if self.distancia['x'] < 0:
						self.direction.x = -1
						self.flip = 'left'
					else:
						self.direction.x = 1
						self.flip = 'right'
					self.atacando = True


		if self.volviendo and self.rect.collidepoint(self.init_pos):
			
			self.volviendo = False
			self.hitbox = self.hitbox.inflate(self.hitbox_back)
			self.vida = ENEMIGOS[self.type]['vida']

		self.barra.rect.midbottom = self.hitbox.midtop
		self.barra.rect.bottom -= 20


	def despawn(self):
		current_time = pygame.time.get_ticks()
		if current_time - self.despawn_timer > 8000:
			self.kill()

	def crear_ataque(self):
		if self.flip == 'left':
			self.ataque.image = self.ataque.img_left
		else:
			self.ataque.image = self.ataque.img_right

		self.ataque.rect.center = self.rect.center

		if pygame.sprite.collide_mask(self.ataque, self.player) and not self.player.dashing:
			if not self.player.invulnerable:
				self.player.vida -= self.daño
				self.player.heal_acum += self.daño // 2
				self.player.last_dmg = self.daño
				self.dot = True
			self.player.invulnerable = True

	def check_dañado(self):

		if self.invulnerable:
			alpha = self.wave_value()
			self.image.set_alpha(alpha)
			if not self.dañado_timer:
				self.dañado_timer = pygame.time.get_ticks()

	def check_cooldown(self):

		current_time = pygame.time.get_ticks()

		if current_time - self.dañado_timer > 1000:
			self.invulnerable = False
			self.image.set_alpha(255)
			self.dañado_timer = 0

		if self.effect_timer and (current_time - self.effect_timer) > self.effect_duration:
			self.vida -= self.effect['daño']
			self.ticks += 1
			if self.effect['ticks'] > self.ticks:
				self.effect_timer = pygame.time.get_ticks()
			else:
				self.effect_timer = 0
				self.effect_duration = 0
				self.effect = None
				self.efecto.kill()
				self.ticks = 0

	def check_volviendo(self):

		if self.volviendo:
			if self.hitbox.width > 0:
				self.hitbox_back = self.hitbox.width, self.hitbox.height
				self.hitbox = self.hitbox.inflate(-self.hitbox.width, -self.hitbox.height)
				self.hitbox.midbottom = self.rect.midbottom
			self.vida = 1

	def check_effect(self):

		if self.effect and not self.effect_timer:
			self.effect_duration = self.effect['time']
			self.effect_timer = pygame.time.get_ticks()
			self.efecto = Efecto(self.effect['tipo'], self.visibles, self.effect['index'])

	def check_efecto(self):

		if self.efecto:
			self.efecto.rect.midbottom = self.barra.rect.midtop
			self.efecto.update()

	def check_special(self):
		if self.special:
			if self.special == 'multitud':
				cercanos = 0
				for sprite in self.atacables:
					if abs(sprite.hitbox.centery - self.hitbox.centery) < TILESIZE * 2 and abs(sprite.hitbox.centerx - self.hitbox.centerx) < TILESIZE * 10 and sprite.type == self.type:
						cercanos += 1

				self.daño = ENEMIGOS[self.type]['ataque'] * cercanos

			elif self.special == 'slow':
				if self.dot:
					self.player.speed *= 0.8
					self.dot = False
				if self.invulnerable or self.volviendo:
					self.player.speed = PLAYER['speed']





	def check_status(self):
		self.check_dañado()
		self.check_cooldown()
		self.check_volviendo()
		self.check_effect()
		self.check_efecto()
		self.check_special()

	def update(self):
		self.actualizar_direction()
		self.animate()
		self.check_status()
		self.move_enemy()
		if self.despawn_timer:
			self.despawn()
		self.barra.update()
		



class Enemyattack(pygame.sprite.Sprite):
	def __init__(self, type, x, y):
		super().__init__()

		
		self.img_right = pygame.transform.scale2x(pygame.transform.scale2x(pygame.image.load(f'graphics/{type}/ataque_right/ataque_00.png'))).convert_alpha()
		self.img_left = pygame.transform.flip(self.img_right, True, False)
		self.image = self.img_right
		self.rect = self.image.get_rect(bottomleft = (x, y))
		self.hitbox = self.rect.inflate(0, 0)


class Efecto(pygame.sprite.Sprite):
	def __init__(self, type, groups, speed):
		super().__init__(groups)
		self.order = 3
		self.animations = import_folder(f'graphics/efecto/{type}')
		self.image = self.animations[0]
		self.image_index = 0
		self.speed = speed
		self.rect = self.image.get_rect(center = (0, 0))

	def animate(self):
		self.image_index += self.speed
		if self.image_index >= len(self.animations): 
			self.image_index = 0

		self.image = self.animations[int(self.image_index)]

	def update(self):
		self.animate()


