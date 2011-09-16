#! python -O
import pyglet
from pyglet.gl import *
import kytten
import os
import galaxy
import galaxy_objects
import random
import utilities
import sys

class Choose(object):
	'Choose parameters for pre-game setup'

	def __init__(self, data):
		self.data = data
		self.window = SetupWindow()

		# Default theme, blue-colored
		self.theme = kytten.Theme(
			os.path.join(os.getcwd(), 'resources', 'gui'), 
			override={
				"gui_color": [64, 128, 255, 255],
				"font_size": 12
			}
		)
		self.window.batch = pyglet.graphics.Batch()
		self.group = pyglet.graphics.OrderedGroup(0)
		self.dialog = kytten.Dialog(
			kytten.TitleFrame(
				"Choose Game Difficulty",
				kytten.VerticalLayout([
					kytten.Menu(
						options=["Beginner", "Easy", "Normal", "Challenging"],
						on_select=self.on_difficulty_select
					)
				]),
			),
			window=self.window, batch=self.window.batch, group=self.group,
			anchor=kytten.ANCHOR_CENTER,
			theme=self.theme
		)
	
	def on_difficulty_select(self, choice):
		print choice
		self.generate_galaxy_objects()

	def generate_galaxy_objects(self):
		'Generate foreground/background stars, black holes, and nebulae'
		foreground_limits = (-1500,-1500,1500,1500)
		foreground_dispersion = 200
		foreground_star_count = 50
		black_hole_count = random.randint(int(foreground_star_count/10), int(foreground_star_count)/5)
		worm_hole_count = random.randint(int(foreground_star_count/10), int(foreground_star_count)/5)

		# randomly generate background stars
		background_stars = []
		for coordinate in utilities.random_dispersed_coordinates(amount=8000, dispersion=3):
			color = []
			for index in range(0,3):
				color.append(64)
			# allow one or two of the bytes to be less, which allows slight coloration
			color[random.randint(0,2)] = random.randint(32,64)
			color[random.randint(0,2)] = random.randint(32,64)
			background_stars.append(
				galaxy_objects.BackgroundStar(coordinate, color),
			)

		# generate coordinates for foreground stars AND black holes in one pass
		# since they may not overlap
		star_coordinates = utilities.random_dispersed_coordinates(
			foreground_limits[0], foreground_limits[1], foreground_limits[2], foreground_limits[3],
			amount=foreground_star_count+black_hole_count, dispersion=foreground_dispersion
		)
		# randomly pull coordinates out as black holes
		black_hole_coordinates = []
		for repeated in range(black_hole_count):
			black_hole_coordinates.append( 
				star_coordinates.pop(random.randint(0,len(star_coordinates)-1))
			)

		# randomly generate foreground stars
		foreground_stars = []
		available_colors = galaxy_objects.ForegroundStar.colors.keys()
		available_star_names = []
		with open('resources/star_names.txt') as star_names_file:
			for line in star_names_file:
				available_star_names.append(line.rstrip())
		for coordinate in star_coordinates:
			foreground_stars.append(
				galaxy_objects.ForegroundStar(
					coordinate, 
					available_star_names.pop(random.randint(0, len(available_star_names)-1)), 
					available_colors[random.randint(0, len(available_colors)-1)]
				),
			)

		# generate black hole objects
		black_holes = []
		for coordinate in black_hole_coordinates:
			black_holes.append(
				galaxy_objects.BlackHole(coordinate, initial_rotation=random.randint(0,359))
			)

		# generate nebulae
		nebulae = []
		nebula_colors = galaxy_objects.Nebula.lobe_colors.keys()
		nebula_color_index = random.randint(0, len(nebula_colors)-1)
		nebula_offset = 80
		min_lobes = 3
		max_lobes = galaxy_objects.Nebula.max_lobes

		# minimize repeated lobe secondary/sprite combinations
		nebula_secondary_sprite_permutations = [
			(0, 1), (0, 2), (1, 1), (1, 2)
		]
		nebula_permutations_index = random.randint(0,3)

		for coordinate in utilities.random_dispersed_coordinates(
			foreground_limits[0], foreground_limits[1], foreground_limits[2], foreground_limits[3],
			amount=random.randint(3,6),
			dispersion=galaxy_objects.Nebula.max_offset*2
		):
			color = nebula_colors[nebula_color_index]
			# cycle through all nebula colors
			nebula_color_index -= 1
			if nebula_color_index < 0:
				nebula_color_index = len(nebula_colors)-1

			lobe_count = random.randint(min_lobes, max_lobes)
			lobes = []
			for lobe_coordinate in utilities.random_dispersed_coordinates(
				-nebula_offset, -nebula_offset, nebula_offset, nebula_offset,
				amount = lobe_count,
				dispersion = 15
			):
				# cycle through all lobe secondary/sprite combinations
				secondary_sprite = nebula_secondary_sprite_permutations[nebula_permutations_index]
				nebula_permutations_index -= 1
				if nebula_permutations_index < 0:
					nebula_permutations_index = 3

				lobes.append(
					(
						random.randint(0,1),
						random.randint(1,2),
						lobe_coordinate,
						random.randint(0,359),
						# use exponentiation to ensure floats less than 1.0 are as common as floats greater than 1.0
						10**random.uniform(-0.3, 0.3)
					)
				)
			nebulae.append( galaxy_objects.Nebula(coordinate, color, lobes) )

		# generate worm holes
		star_indexes = range(len(foreground_stars))
		worm_holes = []
		for repeat in range(worm_hole_count):
			index1 = star_indexes.pop(random.randint(0, len(star_indexes)-1))
			index2 = star_indexes.pop(random.randint(0, len(star_indexes)-1))
			worm_holes.append((index1, index2))

		self.data.galaxy_objects = galaxy_objects.All(
			foreground_stars,
			background_stars,
			black_holes,
			nebulae,
			worm_holes
		)
		galaxy.Window(self.data)
		self.window.close()
	
class SetupWindow(pyglet.window.Window):

	def __init__(self, resizable=False, caption='New game', width=640, height=480):
		super(SetupWindow, self).__init__(
			resizable=resizable, caption=caption, width=width, height=height, 
			style=pyglet.window.Window.WINDOW_STYLE_DIALOG)
		self.register_event_type('on_update')
		pyglet.clock.schedule(self.update)

	def on_draw(self):
		glClearColor(0.0, 0.0, 0.0, 0)
		self.clear()
		self.batch.draw()

	def update(self, dt):
		self.dispatch_event('on_update', dt)
