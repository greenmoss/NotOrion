#! python -O
import pyglet
from pyglet.gl import *
import kytten
import os
import galaxy
import galaxy_objects
import random
import utilities

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

		self.data.galaxy_objects = galaxy_objects.All(
				# foreground stars
				[
					galaxy_objects.ForegroundStar((-1000, 900), 'Xi Bootis', 'red'),
					galaxy_objects.ForegroundStar((1225, 125), 'Alpha Centauri', 'green'),
					galaxy_objects.ForegroundStar((250, 250), 'Sol', 'blue'),
					galaxy_objects.ForegroundStar((0, 0), 'Tau Ceti', 'yellow'),
					galaxy_objects.ForegroundStar((-1125, -125), 'Eta Cassiopeiae', 'white'),
					galaxy_objects.ForegroundStar((750, -950), 'Delta Pavonis', 'brown'),
					galaxy_objects.ForegroundStar((-250, -250), 'Eridani', 'orange'),
				],
				background_stars
			)
		galaxy.Window(self.data)
		#self.window.close()
	
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
