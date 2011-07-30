#! python -O
import pyglet
from pyglet.gl import *
import kytten
import os
import galaxy
import galaxy_objects
import random

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
		background_stars = []
		for coordinate in self.choose_object_coordinates(amount=8000):
			color = []
			for index in range(0,3):
				color.append(255)
			# allow one of the bytes to be less, which allows slight coloration
			color[random.randint(0,2)] = random.randint(64,255)
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

	def choose_object_coordinates(self, bottom=-1000, left=-1000, top=1000, right=1000, amount=500, dispersion=1):
		'choose and return a set of  non-duplicate coordinates between min/max limits'

		object_coordinates = {}
		all_used_coordinates = {}
		# never allow retries to exceed the number of available placement coordinates
		# permissible retries starts with the full number of available coordinates
		# and decrements for every used coordinate
		# actually this is not an accurate way to define all remaining available coordinates
		# so we're sacrifice accuracy in favor of simplicity
		permissible_retries = (right-left+1) * (top-bottom+1)

		retry_vector = (random.randint(int(left/10), int(right/10)),random.randint(int(bottom/10), int(top/10)))
		for i in range(amount):
			random_coordinate = (random.randint(left, right), random.randint(bottom, top))
			first_coordinate = random_coordinate
			retries = 0
			while all_used_coordinates.has_key(random_coordinate):
				random_coordinate = (random_coordinate[0]+retry_vector[0], random_coordinate[1]+retry_vector[1])
				if (random_coordinate == first_coordinate):
					# retry with a different random vector
					retry_vector = (random.randint(int(left/10), int(right/10)),random.randint(int(bottom/10), int(top/10)))
					if retries > permissible_retries:
						raise Exception, 'ran out of available placement coordinates'
			chosen = random_coordinate
			# disallow use of neighbors, out to dispersion distance
			for x in range(chosen[0]-dispersion+1,chosen[0]+dispersion):
				for y in range(chosen[1]-dispersion+1,chosen[1]+dispersion):
					if not all_used_coordinates.has_key((x,y)):
						all_used_coordinates[(x,y)] = True
						permissible_retries -= 1
			object_coordinates[chosen] = True

		return object_coordinates.keys()
	
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
