#! python -O
from __future__ import division
from pyglet.window import key, Window
from pyglet.gl import *
import pyglet
import Stars

class RangeException(Exception): pass
class MissingDataException(Exception): pass

class DataContainer(object):
	"""A simple object to store all application data."""
	def __init__(self):
		True

class GalaxyWindow(Window):
	data = DataContainer()
	max_dimension = 5000
	min_dimension = 50
	# .01 more or less than 1.0 should be fast enough zoom speed
	zoom_speed = 1.01
	# empty margin around outermost foreground stars, in window pixels
	window_margin = 100

	def __init__(self, width=1024, height=768, data=None):
		if not (self.min_dimension < width < self.max_dimension) or not (self.min_dimension < height < self.max_dimension):
			raise RangeException, "width and height must be between 50 and 5000"
		super(GalaxyWindow, self).__init__(resizable=True, caption='Galaxy', width=width, height=height, visible=False)
		if not (data == None):
			self.data = data

		# MUST have stars
		if not hasattr(self.data, 'stars'):
			raise MissingDataException, "self.data must have attribute stars"
		if not isinstance(self.data.stars, Stars.All):
			raise MissingDataException, "self.data.stars must be an instance of Stars.All"
		self.stars_bounding_y = self.data.stars.top_bounding_y
		if -self.data.stars.bottom_bounding_y > self.data.stars.top_bounding_y:
			self.stars_bounding_y = -self.data.stars.bottom_bounding_y
		self.stars_bounding_x = self.data.stars.right_bounding_x
		if -self.data.stars.left_bounding_x > self.data.stars.right_bounding_x:
			self.stars_bounding_x = -self.data.stars.left_bounding_x

		self.clock_display = pyglet.clock.ClockDisplay()

		self.key_handlers = {
			key.ESCAPE: lambda: self.close(),
			key.Q: lambda: self.close(),
		}

		self.derive_from_window_dimensions(self.width, self.height)
		self.set_scale(self.maximum_scale)

		self.set_center((0, 0))

		self.set_visible()
	
	def derive_from_window_dimensions(self, width, height):
		"Set attributes that are based on window dimensions."
		self.half_width = width/2
		self.half_height = height/2

		# Derive minimum and maximum scale, based on minimum and maximum distances between foreground stars.
		self.minimum_dimension = (width < height) and width or height
			
		self.minimum_scale = self.data.stars.min_distance/self.minimum_dimension*2.0
		self.maximum_scale = self.data.stars.max_distance/self.minimum_dimension
		# 35 is minimum absolute distance between star sprites and labels
		if(self.data.stars.min_distance/self.maximum_scale < 35.0):
			self.maximum_scale = self.data.stars.min_distance/35

	def set_center(self, coordinates):
		"Set the window center, for rendering foreground objects/stars."
		coordinates = [coordinates[0], coordinates[1]]
		# would the new center make us fall outside acceptable margins?
		if coordinates[1] > self.center_limits['top']:
			coordinates[1] = self.center_limits['top']
		elif coordinates[1] < self.center_limits['bottom']:
			coordinates[1] = self.center_limits['bottom']

		if coordinates[0] > self.center_limits['right']:
			coordinates[0] = self.center_limits['right']
		elif coordinates[0] < self.center_limits['left']:
			coordinates[0] = self.center_limits['left']
		self.absolute_center = (coordinates[0], coordinates[1])
	
	def set_scale(self, foreground_scale):
		"Set attributes that are based on zoom/scale."

		# scale must be larger than 0
		if foreground_scale <= 0:
			raise RangeException, "scale must be greater than 0"

		if (foreground_scale < self.minimum_scale):
			foreground_scale = self.minimum_scale
		elif (foreground_scale > self.maximum_scale):
			foreground_scale = self.maximum_scale

		self.center_limits = {
			'top':self.stars_bounding_y/foreground_scale+self.window_margin-self.half_height,
			'right':self.stars_bounding_x/foreground_scale+self.window_margin-self.half_width,
			'bottom':-self.stars_bounding_y/foreground_scale-self.window_margin+self.half_height,
			'left':-self.stars_bounding_x/foreground_scale-self.window_margin+self.half_width,
		}
		if self.center_limits['top'] < self.center_limits['bottom']:
			self.center_limits['top'] = 0
			self.center_limits['bottom'] = 0
		if self.center_limits['right'] < self.center_limits['left']:
			self.center_limits['right'] = 0
			self.center_limits['left'] = 0

		self.foreground_scale = foreground_scale

	def window_to_absolute(self, coordinates):
		"Translate a window coordinate into absolute foreground coordinates, accounting for window center and scale."
		return(
			self.absolute_center[0]*self.foreground_scale+
				(coordinates[0]-self.half_width)*self.foreground_scale,
			self.absolute_center[1]*self.foreground_scale+
				(coordinates[1]-self.half_height)*self.foreground_scale)

	def on_draw(self):
		glClearColor(0.0, 0.0, 0.0, 0)
		self.clear()

		# set 2D perspective view
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(-self.half_width, self.half_width, -self.half_height, self.half_height)
		glMatrixMode(GL_MODELVIEW)

		# draw the background stars
		self.data.stars.background_vertex_list.draw(pyglet.gl.GL_POINTS)

		# set the center of the viewing area
		gluLookAt(
			self.absolute_center[0], self.absolute_center[1], 0.0,
			self.absolute_center[0], self.absolute_center[1], -100.0,
			0.0, 1.0, 0.0)

		# draw the foreground stars and other objects
		self.data.stars.draw_scaled(self.foreground_scale)

		# for HUD objects, set 2D projection view with origin at lower left
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, self.width, 0, self.height)
		glMatrixMode(GL_MODELVIEW)

		# then draw the HUD objects

		# reset identity stack
		glLoadIdentity()

	def on_key_press(self, symbol, modifiers):
		handler = self.key_handlers.get(symbol, lambda: None)
		handler()
	
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.set_center((self.absolute_center[0] - dx, self.absolute_center[1] - dy))

	def on_mouse_press(self, x, y, button, modifiers):
		pass

	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		self.set_scale(self.foreground_scale*(self.zoom_speed**scroll_y))
		# ensure center is still in a valid position
		self.set_center((self.absolute_center[0], self.absolute_center[1]))
	
	def on_resize(self, width, height):
		if not (self.min_dimension < width < self.max_dimension) or not (self.min_dimension < height < self.max_dimension):
			raise RangeException, "width and height must be between 50 and 5000"

		# reset openGL attributes to match new window dimensions
		glViewport(0, 0, width, height)
		glMatrixMode(gl.GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, width, 0, height, -1, 1)
		glMatrixMode(gl.GL_MODELVIEW)

		self.derive_from_window_dimensions(width, height)
		# window resize changes min/max scale, so ensure we are still within scale bounds
		self.set_scale(self.foreground_scale)
		# ensure center is still in a valid position
		self.set_center((self.absolute_center[0], self.absolute_center[1]))

class Application(object):
	"""Controller class for all game objects."""
	data = DataContainer()

	def __init__(self, data=None):
		if not (data == None):
			self.data = data

		galaxy_window = GalaxyWindow(1024, 768, self.data)

if __name__ == "__main__":
	data = DataContainer()
	pyglet.resource.path = ['../images']
	pyglet.resource.reindex()
	star_image = pyglet.resource.image('star.png')

	# some test data
	data.stars = Stars.All(
		[
			Stars.NamedStar((-1000, 900), 'Xi Bootis', star_image),
			Stars.NamedStar((1225, 125), 'Alpha Centauri', star_image),
			Stars.NamedStar((250, 250), 'Sol', star_image),
			Stars.NamedStar((0, 0), 'Tau Ceti', star_image),
			Stars.NamedStar((-1125, -125), 'Eta Cassiopeiae', star_image),
			Stars.NamedStar((750, -950), 'Delta Pavonis', star_image),
			Stars.NamedStar((-250, -250), 'Eridani', star_image),
		],
		[
			Stars.BackgroundStar((0, 0), (0, 0, 255)),
			Stars.BackgroundStar((250, 250), (0, 255, 0)),
			Stars.BackgroundStar((-250, -250), (255, 0, 0)),
			Stars.BackgroundStar((10, -100), (228, 255, 255)),
			Stars.BackgroundStar((100, 100), (255, 255, 228)),
			Stars.BackgroundStar((-200, -300), (255, 228, 255)),
			Stars.BackgroundStar((-160, 228), (228, 255, 255)),
			Stars.BackgroundStar((589, -344), (228, 255, 255)),
			Stars.BackgroundStar((-420, -300), (255, 255, 228)),
			Stars.BackgroundStar((-400, 299), (255, 228, 255)),
			Stars.BackgroundStar((589, -344), (228, 255, 255)),
			Stars.BackgroundStar((420, -300), (255, 255, 228)),
			Stars.BackgroundStar((400, 199), (255, 228, 255)),
		])

	application = Application(data)
	pyglet.app.run()
