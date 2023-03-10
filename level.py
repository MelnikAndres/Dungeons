import pygame
from support import import_csv_layout, import_folder
from ajustes import TILESIZE
from tiles import Tile
from player import Player
from enemy import Enemy
from gui import *
from random import choice
from objeto import *

class Level:
	def __init__(self, screen, restart):

		#general setup
		self.display_surf = pygame.display.get_surface()
		self.world_shift = 0
		self.restart = restart

		#sprites groups
		self.visible_sprites = CameraGroup()
		self.obstacle_sprites = pygame.sprite.Group()
		self.movimiento_sprites = pygame.sprite.Group()
		self.atacables_sprites = pygame.sprite.Group()
		self.magia_sprites = pygame.sprite.Group()
		self.gui = pygame.sprite.Group()

		#create map
		self.create_map()


	def create_map(self):
		level = choice((0, 1))

		layouts = {
			'dark': import_csv_layout(f'map/map_{level}/mapa_Dark.csv'),
			'player': import_csv_layout(f'map/map_{level}/mapa_Player.csv'),
			'entities': import_csv_layout(f'map/map_{level}/mapa_Entities.csv'),
			'plataformas': import_csv_layout(f'map/map_{level}/mapa_Plataformas.csv'),
			'movimiento': import_csv_layout(f'map/map_{level}/mapa_Movimiento.csv'),
			'fondo': import_csv_layout(f'map/map_{level}/mapa_Fondo.csv'),

		}

		graphics = {
			'fondo': import_folder('graphics/fondo_tiles'),
			'plataformas': import_folder('graphics/plataformas_tiles'),
			'dark': import_folder('graphics/dark_tiles'),
		}

		skills = ['skull', 'thunder', 'dash']

		for style, layout in layouts.items():
			for row_index, row in enumerate(layout):
				enemigo_x = []
				enemigo_y = 0
				value = 0
				rango_posible = []
				unitario = 0
				for col_index, col in enumerate(row):
					if col == '-1':
						continue
					x = col_index * TILESIZE
					y = row_index * TILESIZE

					if style == 'fondo':
						surf = graphics['fondo'][int(col)]
						Tile(x, y, [self.visible_sprites], 'fondo', surf)

					elif style == 'plataformas':
						if col == '15' or col == '12':
							surf = graphics['plataformas'][int(col)]
							Tile(x, y, [self.visible_sprites], 'plataforma', surf)
						else:
							surf = graphics['plataformas'][int(col)]
							Tile(x, y, [self.obstacle_sprites, self.visible_sprites], 'plataforma', surf)

					elif style == 'player':
						if col == '1':
							self.player = Player(x, y, [self.visible_sprites], self.obstacle_sprites, self.atacables_sprites, self.magia_sprites, self.gui, self.restart)
					elif style == 'entities':

						if col == '4':
							if skills and choice((0,1)):
								skill = skills.pop(choice(range(len(skills))))
								Objeto([self.visible_sprites, self.atacables_sprites], x, y, 'cofre', skill, self.player)

						elif col == '3':
							unitario = choice((2,3))
							if unitario == 2:
								Enemy(x, y, [self.visible_sprites, self.atacables_sprites], 'skeleton', self.player, self.movimiento_sprites, self.atacables_sprites)
							elif unitario == 3:
								Enemy(x, y, [self.visible_sprites, self.atacables_sprites], 'eyeball', self.player, self.movimiento_sprites, self.atacables_sprites)


						else:
							enemigo_x.append(x)
							enemigo_y = y

					elif style == 'dark':
						surf = graphics['dark'][int(col)]
						Tile(x, y, [self.visible_sprites], 'dark', surf)

					elif style == 'movimiento':
						if col == '0':
							Tile(x, y, [self.movimiento_sprites], 'vuelta')
						elif col == '1':
							Tile(x, y, [self.movimiento_sprites], 'bloque')

				if enemigo_x:
					rango_posible = list(range(enemigo_x[0], enemigo_x[-1], TILESIZE*4))
					while value < len(enemigo_x):
						x_posible = choice(range(len(rango_posible)))
						x_enem = rango_posible[x_posible]
						rango_posible.pop(x_posible)
						enem = choice((2,3))
						if enem == 2:
							value += 1
							Enemy(x_enem, enemigo_y, [self.visible_sprites, self.atacables_sprites], 'skeleton', self.player, self.movimiento_sprites, self.atacables_sprites)
						elif enem == 3:
							value += 2
							Enemy(x_enem, enemigo_y, [self.visible_sprites, self.atacables_sprites], 'eyeball', self.player, self.movimiento_sprites, self.atacables_sprites)


		DinamicUI([self.gui], self.player, 35, 10, 257, 21, 'red', 'vida')
		DinamicUI([self.gui], self.player, 35, 10, 257, 21, 'red', 'heal', alpha = 100)
		DinamicUI([self.gui], self.player, 35, 10, 257, 21, 'green', 'daño', alpha = 100)
		DinamicUI([self.gui], self.player, 36, 44, 206, 16, 'blue', 'mana')
		StaticUI([self.gui])




	def check_win(self):
		if not self.atacables_sprites.sprites():
			self.restart()

	def run(self):
		self.visible_sprites.custom_draw(self.player)
		self.visible_sprites.update()
		self.gui.draw(self.display_surf)
		self.gui.update()
		self.check_win()

class CameraGroup(pygame.sprite.Group):
	def  __init__(self):

		#generl setup
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.half_width = self.display_surface.get_size()[0] // 2
		self.half_height = self.display_surface.get_size()[1] // 2
		self.offset = pygame.math.Vector2(0,0)

	def custom_draw(self, player):

		#getting the offset
		self.offset.x = player.rect.centerx - self.half_width
		self.offset.y = player.camera - self.half_height

		if self.offset.y < 0:
			self.offset.y = 0
		if self.offset.y > 864:
			self.offset.y = 864

		if self.offset.x < 64:
			self.offset.x = 64
		if self.offset.x > 1024:
			self.offset.x = 1024

		for sprite in sorted(self.sprites(), key = lambda sprite: sprite.order, reverse = True):
			offset_pos = sprite.rect.topleft - self.offset
			self.display_surface.blit(sprite.image, offset_pos)



		
