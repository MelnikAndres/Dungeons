ALTO = 608
ANCHO = 1280
FPS = 30
TILESIZE = 32

PLAYER = {'vida': 100, 'mana': 100, 'manareg': 0.05, 'ataque': 6, 'armadura': 6, 'resistencia': 3, 'speed':12, }

ENEMIGOS = {'skeleton': {'vida': 34, 'ataque': 15,'atq_speed': 0.5,  'speed': 5, 'inflate': (-64, -55), 'range': (64, 96),'run': 0, 'notice': (300, 64), 'attack_index': 7, 'special': 'multitud'},
			'eyeball': {'vida': 25, 'ataque': 40,'atq_speed': 0.6,  'speed': 8, 'inflate': (0, -136), 'range': (320, 96),'run': 180, 'notice': (520, 64), 'attack_index': 10, 'special': 'slow'},}

HECHIZOS = {'thunder': {'mana': 20, 'damage': 1, 'time': 2500, 'travel': 1500, 'anim': 0.2, 'speed': 20, 'stun': True, 'effect': {'tipo':'electric','daño': 4,'time': 600,'ticks': 1, 'index': 0.2}},
			'skull': {'mana': 40, 'damage': 15, 'time': 5000,'travel': 1500, 'anim': 0.15, 'speed': 10, 'stun': False, 'effect': {'tipo':'dark','daño': 2,'time': 1000,'ticks': 3, 'index': 0.3}}, 
			'heal': {'mana': 50, 'damage': 45, 'time': 7500,'travel': 0, 'anim': 0.2, 'speed': 0, 'stun': False, 'effect': None},
			'mana':{'anim': 0.2, 'time': 8000},}

COOLDOWNS = {'mana':{'cd': 8000, 'pos': (469, 554)}, 'dash':{'cd': 4500, 'pos': (540, 554)}, 'heal':{'cd': 7500, 'pos': (576, 554)}, 'thunder':{'cd': 2500, 'pos': (612, 554)}, 'skull':{'cd': 5000, 'pos': (648, 554)},}

OBJETOS = {'cofre':{'vida': 18}}