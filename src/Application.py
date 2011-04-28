#! python -O
from __future__ import division
from pyglet.window import key, Window
from pyglet.gl import *
import pyglet
import Stars

class RangeException(Exception): pass

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
	# start out viewing coordinates 0, 0
	absolute_center_coordinates = (0, 0)
	foreground_scale = 5.0

	def __init__(self, width=1024, height=768, data=None):
		if not (self.min_dimension < width < self.max_dimension) or not (self.min_dimension < height < self.max_dimension):
			raise RangeException, "width and height must be between 50 and 5000"
		super(GalaxyWindow, self).__init__(resizable=True, caption='Galaxy', width=width, height=height)
		if not (data == None):
			self.data = data
		self.clock_display = pyglet.clock.ClockDisplay()

		self.key_handlers = {
			key.ESCAPE: lambda: self.close(),
			key.Q: lambda: self.close(),
		}

		self.derive_from_window_dimensions(self.width, self.height)
	
	def derive_from_window_dimensions(self, width, height):
		"Set attributes that are based on window dimensions."
		self.window_aspect_ratio = width/height
		self.dimensions_into_foreground_scale = height/self.foreground_scale
		self.foreground_scale_into_dimensions = self.foreground_scale/height
	
	def rescale(self, new_scale):
		"Set a new scaling factor."
		self.dimensions_into_foreground_scale = self.height/new_scale
		self.foreground_scale_into_dimensions = new_scale/self.height
		self.foreground_scale = new_scale

	def on_draw(self):
		glClearColor(0.0, 0.0, 0.0, 0)
		self.clear()

		## for rendering background stars
		# set 3D perspective view
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(self.height, self.window_aspect_ratio, .1, 1000)
		glMatrixMode(GL_MODELVIEW)

		# then, draw the background stars
		self.data.stars.background_vertex_list.draw(pyglet.gl.GL_POINTS)

		## for rendering foreground stars and other objects
		# set 2D projection view
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, self.width, 0, self.height)

		# then, set the center of the viewing area
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		#gluLookAt(
		#	self.absolute_center_coordinates[0], self.absolute_center_coordinates[1], 1.0,
		#	self.absolute_center_coordinates[0], self.absolute_center_coordinates[1], -1.0,
		#	0.0, 1.0, 0.0)

		# then, draw the foreground stars and other objects
		#self.data.stars.draw_scaled(1.0)

	def on_key_press(self, symbol, modifiers):
		handler = self.key_handlers.get(symbol, lambda: None)
		handler()
	
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		reduced_x = -1*(dx/64)
		reduced_y = -1*(dy/64)
		self.absolute_center_coordinates = (self.absolute_center_coordinates[0]-dx, self.absolute_center_coordinates[1]-dy)

	def on_mouse_press(self, x, y, button, modifiers):
		pass

	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		new_zoom = (self.zoom_speed**scroll_y)
	
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
			Stars.NamedStar((-4000, 4000), 'Xi Bootis', star_image),
			Stars.NamedStar((500, 500), 'Alpha Centauri', star_image),
			Stars.NamedStar((1000, 1000), 'Sol', star_image),
			Stars.NamedStar((0, 0), 'Tau Ceti', star_image),
			Stars.NamedStar((-500, -500), 'Eta Cassiopeiae', star_image),
			Stars.NamedStar((4000, -4000), 'Delta Pavonis', star_image),
			Stars.NamedStar((-1000, -1000), 'Eridani', star_image),
		],
		[
			Stars.BackgroundStar((0, 0), (0, 0, 255)),
			Stars.BackgroundStar((10, 20), (200, 255, 255)),
			Stars.BackgroundStar((-25, 30), (255, 255, 200)),
			Stars.BackgroundStar((40, -10), (255, 200, 255)),
			Stars.BackgroundStar((20, -30), (255, 255, 255)),
			Stars.BackgroundStar((-40, 0), (255, 255, 215)),
			Stars.BackgroundStar((-20, -35), (255, 215, 255)),
			Stars.BackgroundStar((10, 35), (255, 255, 255)),
			Stars.BackgroundStar((-30, -25), (228, 255, 255)),
			Stars.BackgroundStar((20, -30), (255, 255, 228)),
			Stars.BackgroundStar((-40, 40), (255, 215, 255)),
		])

	application = Application(data)
	pyglet.app.run()
