from csv import reader
from os import walk
import pygame
pygame.init()

def import_csv_layout(path):
	terrain_map = []
	with open(path) as level_map:
		level = reader(level_map, delimiter = ',')
		for row in level:
			terrain_map.append(list(row))
		return terrain_map

def import_folder(path, scale = False):
	surface_list = []

	for _,__,img_files in walk(path):
		for image in img_files:
			full_path = f'{path}/{image}'
			image_surf = pygame.image.load(full_path).convert_alpha()
			if scale:
				image_surf = pygame.transform.scale2x(image_surf).convert_alpha()
			surface_list.append(image_surf)
	return surface_list
			
