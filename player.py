import pygame
from ajustes import *
from entity import Entity
from support import import_folder
from gui import Cooldown, Bloqueado

class Player(Entity):
	def __init__(self, x, y, groups, obstacle_sprites, atacables, magia, gui, restart):
		super().__init__(groups)
		
		#general
		self.import_player_assets()

		self.image_index = 0
		self.image = self.animations['idle_right'][self.image_index]

		self.rect = self.image.get_rect(bottomleft = (x, y)) 
		self.hitbox = self.rect.inflate(-40, -50)

		self.restart = restart
		self.camera = self.rect.centery
		self.order = 2

		#stats
		self.speed = PLAYER['speed']
		self.vida = PLAYER['vida']
		self.mana = PLAYER['mana']
		self.daño = PLAYER['ataque']
		self.manareg = PLAYER['manareg']

		#status
		self.flip = 'right'
		self.accion = 'idle_'
		self.bussy = False
		self.saltando = False
		self.crouching = False
		self.atacando = False
		self.invulnerable = False
		self.dañado_timer = 0
		self.dashing = False
		self.dash_timer = 0
		self.dash_cd = 0
		self.magic_timer_w = 0
		self.magic_timer_e = 0
		self.magic_timer_r = 0
		self.magic_timer_b = 0
		self.healing = False
		self.heal_acum = 0
		self.last_dmg = 0
		self.mana_cool = None


		#habilidades disponibles
		self.heal = True
		self.healblock = None
		self.thunder = False
		self.thunderblock = None
		self.skull = False
		self.skullblock = None
		self.dash = False
		self.dashblock = None

		#exception
		self.jumpattack_index = 0

		#sprite group
		self.obstacle_sprites = obstacle_sprites
		self.atacables = atacables
		self.ataque = None
		self.magia = magia
		self.hechizo = None
		self.visibles = groups[0]
		self.gui = gui

	def import_player_assets(self):
		player_path = 'graphics/hero/'
		self.animations = {'idle_right': [], 'run_right': [], 'jump_right': [], 
							'attack_right': [], 'magicself_right': [], 'magicfront_right': [], 
							'crouch_right': [], 'hurt_right': [], 'jumpattack_right': [], 
							'crouchattack_right': [], 'crouchreverse_right': [], 'dash_right': [],}

		animations_left = {'idle_left': [], 'run_left': [], 'jump_left': [], 
							'attack_left': [], 'magicself_left': [], 'magicfront_left': [], 
							'crouch_left': [], 'hurt_left': [], 'jumpattack_left': [], 
							'crouchattack_left': [], 'crouchreverse_left': [], 'dash_left': [],}

		for animation in self.animations:
			full_path = player_path + animation
			self.animations[animation] = import_folder(full_path, scale = True)

			for animation_flip in self.animations[animation]:
				animation = animation.split('_')[0] + '_left'
				animations_left[animation].append(pygame.transform.flip(animation_flip, True, False))

		self.animations.update(animations_left)

	def input(self):
		keys = pygame.key.get_pressed()

		if self.bussy:
			self.direction.x = 0
			if self.accion != 'hurt_':
				if keys[pygame.K_LALT] and not self.dashing and not self.dash_cd and self.dash:
					self.dashing = True
					self.bussy = False
					self.dash_timer = pygame.time.get_ticks()
					self.image_index = 0
					self.accion = 'dash_'
					self.speed = PLAYER['speed'] * 2.5
					if self.direction.x == 0:
						self.direction.x = 1 if self.flip == 'right' else -1
					if self.gravedad > 0:
						self.gravedad = 0	

				self.habilidades(keys)
			return


		if self.dashing:
			if not keys[pygame.K_LALT]:
				self.dashing = False
				self.dash_timer = 0
				self.dash_cd = pygame.time.get_ticks()
				Cooldown([self.gui], 'dash', self.dash_cd)
				self.speed = PLAYER['speed']
			return


		if keys[pygame.K_UP]:
			if not self.atacando and self.gravedad < 0:
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

		elif not self.dashing:
			self.direction.x = 0

		if keys[pygame.K_DOWN] and not self.saltando:
			self.direction.x = 0
			self.accion = 'crouch_'
			self.direction.x = 0
			self.crouching = True

		elif self.crouching:
			self.crouching = False
			self.accion = 'idle_'

		if keys[pygame.K_q] and not self.atacando:
			
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

		if keys[pygame.K_LALT] and not self.dashing and not self.dash_cd and self.dash:
			self.dashing = True
			self.bussy = False
			self.dash_timer = pygame.time.get_ticks()
			self.image_index = 0
			self.accion = 'dash_'
			self.speed = PLAYER['speed'] * 2.5
			if self.direction.x == 0:
				self.direction.x = 1 if self.flip == 'right' else -1
			if self.gravedad > 0:
				self.gravedad = 0

		self.habilidades(keys)
		
	def habilidades(self, keys):

		if keys[pygame.K_b] and not self.magic_timer_b and self.mana < 100 and not self.bussy:
			if self.accion != 'magicself_':
				self.image_index = 0
			self.hechizo = 'mana'
			self.accion = 'magicself_'
			self.healing = True
			self.bussy = True

		if keys[pygame.K_w] and not self.magic_timer_w and self.heal:

			if self.mana - HECHIZOS['heal']['mana'] >= 0:
				self.hechizo = 'heal'
				self.speed = PLAYER['speed']
				self.mana -= HECHIZOS['heal']['mana']
				self.accion = 'magicself_'
				self.healing = True
				self.image_index = 0
				self.magic_timer_w = pygame.time.get_ticks()
				self.bussy = True
				Cooldown([self.gui], 'heal', self.magic_timer_w)

		if keys[pygame.K_e] and not self.magic_timer_e and self.thunder:

			if self.mana - HECHIZOS['thunder']['mana'] >= 0:
				self.hechizo = 'thunder'
				self.mana -= HECHIZOS['thunder']['mana']
				self.accion = 'magicfront_'
				self.image_index = 0
				self.magic_timer_e = pygame.time.get_ticks()
				self.bussy = True
				Cooldown([self.gui], 'thunder', self.magic_timer_e)

		if keys[pygame.K_r] and not self.magic_timer_r and self.skull:

			if self.mana - HECHIZOS['skull']['mana'] >= 0:
				self.hechizo = 'skull'
				self.mana -= HECHIZOS['skull']['mana']
				self.accion = 'magicfront_'
				self.image_index = 0
				self.magic_timer_r = pygame.time.get_ticks()
				self.bussy = True
				Cooldown([self.gui], 'skull', self.magic_timer_r)

	def animate(self):

		if self.invulnerable and self.bussy:
			if self.accion != 'hurt_':
				self.accion = 'hurt_'
				self.image_index = 0

			self.animation(0.15, loop = False)

			if self.image_index == len(self.animations[f'{self.accion}{self.flip}']) - 1:
				self.bussy = False
				self.input()

		elif self.dashing:

			self.animation(0)

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

		elif self.accion == 'magicfront_':
			self.animation(HECHIZOS[self.hechizo]['anim'], loop = False, end_action = True)

			if 1 <= self.image_index < 1 + HECHIZOS[self.hechizo]['anim']:
				Magia([self.visibles], self.hechizo, self.rect.right if self.flip == 'right' else self.rect.left , self.rect.centery, self.atacables, self.flip)

		elif self.accion == 'magicself_':

			self.animation(HECHIZOS[self.hechizo]['anim'], loop = False, end_action = True)

			if 1.1 < self.image_index < 1.3:
				Heal([self.visibles], self.rect.centerx, self.rect.top, self.hechizo, self)


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
				self.image_index = 0
				self.accion = 'idle_'
				self.bussy = False
				self.input()

		self.image = self.animations[f'{self.accion}{self.flip}'][int(self.image_index)]

		self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
		self.hitbox.midbottom = self.rect.midbottom

	def jumpattack_animation(self):
		self.image_index += 0.12
		self.jumpattack_index += 0.3
		if self.jumpattack_index >= len(self.animations[f'{self.accion}{self.flip}']): 
			self.accion = 'jump_'
			self.image = self.animations[f'{self.accion}{self.flip}'][int(self.image_index)]
		else:
			self.image = self.animations[f'{self.accion}{self.flip}'][int(self.jumpattack_index)]

		self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
		self.hitbox.midbottom = self.rect.midbottom

	def check_status(self):
		self.check_salto()
		self.check_attack()
		self.check_pos()
		self.check_dañado()
		self.check_cooldowns()
		self.mana_regen()
		self.check_vida()
		self.check_bloqueados()
		self.check_camara()
		
	def check_salto(self):
		if self.dashing:
			return

		if self.gravedad < 0:
			return

		if self.gravedad > 6:
			self.saltando = True

		elif self.saltando and self.en_piso:
			self.saltando = False

		if self.gravedad > 21 and self.accion != 'jump_' and self.accion != 'magicfront_' and self.accion != 'magicself_':
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
				self.magic_timer_b = pygame.time.get_ticks()
				if self.mana_cool:
					self.mana_cool.kill()
				self.mana_cool = Cooldown([self.gui], 'mana', self.magic_timer_b)

	def check_cooldowns(self):
		current_time = pygame.time.get_ticks()

		if current_time - self.dañado_timer > 1200:
			self.invulnerable = False
			self.image.set_alpha(255)
			self.dañado_timer = 0

		if self.dash_timer and current_time - self.dash_timer > 400:
			self.dashing = False
			self.dash_timer = 0
			self.dash_cd = pygame.time.get_ticks()
			Cooldown([self.gui], 'dash', self.dash_cd)
			self.speed = PLAYER['speed']

		if self.dash_cd and current_time - self.dash_cd > 4500:
			self.dash_cd = 0

		if self.magic_timer_r and current_time - self.magic_timer_r > HECHIZOS['skull']['time']:
			self.magic_timer_r = 0

		if self.magic_timer_e and current_time - self.magic_timer_e > HECHIZOS['thunder']['time']:
			self.magic_timer_e = 0

		if self.magic_timer_w and current_time - self.magic_timer_w > HECHIZOS['heal']['time']:
			self.magic_timer_w = 0

		if self.magic_timer_b and current_time - self.magic_timer_b > HECHIZOS['mana']['time']:
			self.magic_timer_b = 0

	def check_vida(self):
		if self.vida <= 0:
			self.restart()

	def mana_regen(self):
		if self.mana < 100:
			self.mana += self.manareg

	def check_bloqueados(self):
		if not self.heal:
			if not self.healblock:
				self.healblock = Bloqueado([self.gui], 'heal')
		elif self.healblock:
			self.healblock.kill()

		if not self.thunder:
			if not self.thunderblock:
				self.thunderblock = Bloqueado([self.gui], 'thunder')
		elif self.thunderblock:
			self.thunderblock.kill()

		if not self.skull:
			if not self.skullblock:
				self.skullblock = Bloqueado([self.gui], 'skull')
		elif self.skullblock:
			self.skullblock.kill()

		if not self.dash:
			if not self.dashblock:
				self.dashblock = Bloqueado([self.gui], 'dash')
		elif self.dashblock:
			self.dashblock.kill()

	def check_camara(self):
		if self.crouching and self.camera < (self.rect.centery + 160):
			self.camera += 8
		elif not self.crouching:
			self.camera = self.rect.centery

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
		self.check_status()
		self.input()
		self.move(self.speed)	
		self.animate()
		if self.magia:
			self.magia.update()

class Allyattack(pygame.sprite.Sprite):
	def __init__(self, type, x, y):
		super().__init__()

		
		self.img_right = pygame.transform.scale2x(pygame.image.load(f'graphics/hero/ataques/ataque_{type}.png').convert_alpha())
		self.img_left = pygame.transform.flip(self.img_right, True, False)
		self.image = self.img_right
		self.rect = self.image.get_rect(bottomleft = (x, y))
		self.hitbox = self.rect.inflate(0, 0)

class Magia(pygame.sprite.Sprite):
	def __init__(self, groups, type, x , y, atacables, flip):
		super().__init__(groups)

		#general
		self.order = 3
		self.flip = True if flip == 'left' else False

		animations_right = import_folder(f'graphics/hero/magia/{type}_cast', scale = True)
		if self.flip:
			animations_left = [pygame.transform.flip(imagen, True, False) for imagen in animations_right]

		self.animations = animations_left if self.flip else animations_right
		self.image = self.animations[0]
		self.image_index = 0
		self.rect = self.image.get_rect(center = (x, y))

		hitbox_image = pygame.image.load(f'graphics/hero/magia/{type}_hitbox/hitbox.png')
		self.hitbox = hitbox_image.get_rect(center = self.rect.center)

		self.hit_animation = import_folder(f'graphics/hero/magia/{type}_hit', scale = True)

		self.timer = pygame.time.get_ticks()

		self.atacables = atacables
		self.direction = pygame.math.Vector2(0, 0)
		self.direction.x = -1 if self.flip else 1

		self.atacables = atacables


		self.damage = HECHIZOS[type]['damage']
		self.time = HECHIZOS[type]['time']
		self.anim = HECHIZOS[type]['anim']
		self.speed = HECHIZOS[type]['speed']
		self.stun = HECHIZOS[type]['stun']
		self.effect = HECHIZOS[type]['effect']
		self.travel = HECHIZOS[type]['travel']

		self.dead = False


	def animate(self):
		self.image_index += self.anim
		if self.image_index >= len(self.animations): 
			if not self.dead:
				self.image_index = 0
			else:
				self.kill()
				return

		self.image = self.animations[int(self.image_index)]
		self.hitbox.center = self.rect.center

	def move(self):
		if not self.dead:
			self.hitbox.x += self.direction.x * self.speed
			self.rect.center = self.hitbox.center

	def despawn(self):
		current_time = pygame.time.get_ticks()

		if current_time - self.timer > self.travel:
			self.kill()

	def hit(self):
		if not self.dead:
			for sprite in self.atacables:
				if sprite.type == 'cofre':
					continue
				if sprite.hitbox.colliderect(self.hitbox):
					sprite.vida -= self.damage
					sprite.invulnerable = True
					sprite.triggered = True
					sprite.stun = self.stun
					sprite.image_index = 0
					sprite.effect = self.effect
					self.dead = True
					self.animations = self.hit_animation
					self.image = self.animations[0]
					self.image_index = 0


	def update(self):
		self.animate()
		self.move()
		self.despawn()
		self.hit()

class Heal(pygame.sprite.Sprite):
	def __init__(self, groups, x, y, type, player):
		super().__init__(groups)
		self.order = 3
		self.animations = import_folder(f'graphics/hero/magia/{type}')
		self.image = self.animations[0]
		self.image_index = 0
		self.rect = self.image.get_rect(midbottom = (x, y))

		self.type = type
		self.player = player
		self.aplicado = False

	def animate(self):
		self.image_index += 0.2
		if self.image_index >= len(self.animations): 
			self.kill()
			return

		self.image = self.animations[int(self.image_index)]

	def aplicar(self):
		if self.type == 'heal' and not self.aplicado:
			self.player.vida += self.player.heal_acum
			self.player.heal_acum //= 3 
			if self.player.vida > 100:
				self.player.vida = 100
			self.aplicado = True

		elif self.type == 'mana':
			self.player.mana += self.player.manareg * 9
			if self.player.mana > 100:
				self.player.mana = 100

	def update(self):
		self.animate()
		self.aplicar()

