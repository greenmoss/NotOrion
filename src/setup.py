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

	galaxy_age_help_text = """
Young galaxies have more mineral-rich planets and fewer planets suitable for farming.

Mature galaxies have an even mix of farming planets and mineral-rich planets.

Old galaxies have more planets suitable for farming and fewer mineral-rich planets.
"""
	galaxy_size_help_text = """
Galaxy sizes and number of stars:

Tiny: 10 x 7 parsecs, 5 stars

Small: 20 x 14 parsecs, 20 stars

Medium: 27 x 19 parsecs, 36 stars

Large: 33 x 24 parsecs, 54 stars

Huge: 38 x 27 parsecs, 71 stars"""

	def __init__(self, data):
		self.data = data
		self.window = SetupWindow()

		# Default theme, blue-colored
		self.theme = kytten.Theme(
			os.path.join(self.data.paths['resources_dir'], 'gui'), 
			override={
				"gui_color": [64, 128, 255, 255],
				"font_size": 12
			}
		)
		self.window.batch = pyglet.graphics.Batch()
		self.group = pyglet.graphics.OrderedGroup(0)

		self.show_difficulty_dialog()
	
	def on_difficulty_select(self, choice):
		if choice == 'Beginner':
			# simplest: only a few stars, type yellow, no other objects
			# distribute the stars evenly over a small area
			foreground_limits = (-250,-250,250,250)
			foreground_dispersion = 100
			self.generate_galaxy_objects(
				foreground_limits,
				foreground_dispersion,
				5, # number of stars
				object_pool=['yellow']
			)
			self.window.close()

		else:
			self.difficulty_dialog.teardown()

			if choice == "Easy":
				self.galaxy_size = "Small"
			elif choice == "Normal":
				self.galaxy_size = "Medium"
			else: # choice == "Challenging"
				self.galaxy_size = "Large"

			self.galaxy_age = "Mature"

			self.show_options_dialog()

	def on_galaxy_age_help(self):
		self.show_help_dialog(self.galaxy_age_help_text)

	def on_galaxy_age_select(self, choice):
		self.galaxy_age = choice

	def on_galaxy_size_help(self):
		self.show_help_dialog(self.galaxy_size_help_text)

	def on_galaxy_size_select(self, choice):
		self.galaxy_size = choice
	
	def on_options_continue(self):
		# copying estimated proportions from
		# http://masteroforion2.blogspot.com/2006/01/moo2-map-generator.html
		if self.galaxy_size == 'Tiny':
			foreground_limits = (-350,-500,350,500)
			foreground_star_count = 5
			nebulae_count = random.randint(0,1)
		elif self.galaxy_size == 'Small':
			foreground_limits = (-700,-1000,700,1000)
			foreground_star_count = 20
			nebulae_count = random.randint(1,2)
		elif self.galaxy_size == 'Medium':
			foreground_limits = (-950,-1350,950,1350)
			foreground_star_count = 36
			nebulae_count = random.randint(2,5)
		elif self.galaxy_size == 'Large':
			foreground_limits = (-1200,-1650,1200,1650)
			foreground_star_count = 54
			nebulae_count = random.randint(4,8)
		else: #self.galaxy_size == 'Huge'
			foreground_limits = (-1350,-1900,1350,1900)
			foreground_star_count = 71
			nebulae_count = random.randint(6,12)

		foreground_dispersion = 100
		worm_hole_count = random.randint(int(foreground_star_count/10), int(foreground_star_count)/5)

		object_pool = []
		if self.galaxy_age == 'Young':
			# MoO2: "mineral rich"
			object_pool.extend(['black hole']*30)
			object_pool.extend(['blue']*185)
			object_pool.extend(['white']*220)
			object_pool.extend(['yellow']*97)
			object_pool.extend(['orange']*89)
			object_pool.extend(['red']*372)
			object_pool.extend(['brown']*7)

		elif self.galaxy_age == 'Mature':
			# MoO2: "average"
			object_pool.extend(['black hole']*40)
			object_pool.extend(['blue']*105)
			object_pool.extend(['white']*145)
			object_pool.extend(['yellow']*136)
			object_pool.extend(['orange']*144)
			object_pool.extend(['red']*404)
			object_pool.extend(['brown']*26)

		else: #self.galaxy_age == 'Old'
			# MoO2: "organic rich"
			object_pool.extend(['black hole']*70)
			object_pool.extend(['blue']*40)
			object_pool.extend(['white']*40)
			object_pool.extend(['yellow']*305)
			object_pool.extend(['orange']*195)
			object_pool.extend(['red']*327)
			object_pool.extend(['brown']*23)

		self.generate_galaxy_objects(
			foreground_limits,
			foreground_dispersion,
			foreground_star_count,
			worm_hole_count, 
			nebulae_count,
			object_pool
		)
		self.window.close()
	
	def show_difficulty_dialog(self):
		self.difficulty_dialog = kytten.Dialog(
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
	
	def show_help_dialog(self, message):
		# must initially set to None in order to be able to define teardown()
		self.help_dialog = None

		def teardown():
			self.help_dialog.teardown()

		self.help_dialog = kytten.Dialog(
			kytten.Frame(
				kytten.VerticalLayout([
					kytten.Document(message, width=400),
					kytten.Button("Done", on_click=teardown),
				]),
			),
			window=self.window, batch=self.window.batch, group=self.group,
			anchor=kytten.ANCHOR_CENTER,
			theme=self.theme
		)

	def show_options_dialog(self):
		self.options_dialog = kytten.Dialog(
			kytten.TitleFrame(
				"Choose Game Options",
				kytten.VerticalLayout([
					kytten.HorizontalLayout([
						kytten.Label("Galaxy Size"),
						None,
						kytten.Dropdown(
							["Tiny", "Small", "Medium", "Large", "Huge"],
							selected=self.galaxy_size,
							on_select=self.on_galaxy_size_select,
						),
						kytten.Button("?", on_click=self.on_galaxy_size_help),
					]),
					kytten.HorizontalLayout([
						kytten.Label("Galaxy Age"),
						None,
						kytten.Dropdown(
							["Young", "Mature", "Old"],
							selected=self.galaxy_age,
							on_select=self.on_galaxy_age_select,
						),
						kytten.Button("?", on_click=self.on_galaxy_age_help),
					]),
					kytten.Button("Continue", on_click=self.on_options_continue),
				]),
			),
			window=self.window, batch=self.window.batch, group=self.group,
			anchor=kytten.ANCHOR_CENTER,
			theme=self.theme
		)

	def generate_galaxy_objects(self, foreground_limits, foreground_dispersion, foreground_object_count, worm_hole_count=0, nebulae_count=0, object_pool=None):
		'Generate foreground/background stars, black holes, and nebulae'

		if object_pool == None:
			object_pool = galaxy_objects.ForegroundStar.colors.keys()

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
		object_coordinates = utilities.random_dispersed_coordinates(
			foreground_limits[0], foreground_limits[1], foreground_limits[2], foreground_limits[3],
			amount=foreground_object_count, dispersion=foreground_dispersion
		)

		available_star_names = []
		with open(os.path.join(self.data.paths['resources_dir'], 'star_names.txt')) as star_names_file:
			for line in star_names_file:
				available_star_names.append(line.rstrip())

		foreground_stars = []
		black_holes = []

		# randomly generate foreground stars
		for coordinate in object_coordinates:
			object = object_pool[random.randint(0, len(object_pool)-1)]

			if object == 'black hole':
				black_holes.append(
					galaxy_objects.BlackHole(coordinate)
				)

			else:
				foreground_stars.append(
					galaxy_objects.ForegroundStar(
						coordinate, 
						available_star_names.pop(random.randint(0, len(available_star_names)-1)), 
						object
					),
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

		if nebulae_count:
			for coordinate in utilities.random_dispersed_coordinates(
				foreground_limits[0], foreground_limits[1], foreground_limits[2], foreground_limits[3],
				amount=nebulae_count,
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
