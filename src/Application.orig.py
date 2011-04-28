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

	def __init__(self, width=1024, height=768, data=None):
		if not (50 < width < 5000) or not (50 < height < 5000):
			raise RangeException, "width and height must be between 50 and 5000"
		super(GalaxyWindow, self).__init__(resizable=False, caption='Galaxy', width=width, height=height)
		if not (data == None):
			self.data = data
		self.clock_display = pyglet.clock.ClockDisplay()

		self.key_handlers = {
			key.ESCAPE: lambda: self.close(),
			key.Q: lambda: self.close(),
		}

		self.foreground_scale = 4.5
		self.absolute_center = (-3.0, -2.25)

		self.window_aspect_ratio = self.width/self.height
		self.height_over_scale = self.height/self.foreground_scale
		self.scale_over_height = self.foreground_scale/self.height

		self.relative_center = (self.absolute_center[0]*self.height_over_scale, self.absolute_center[1]*self.height_over_scale)

	def on_draw(self):
		glClearColor(0.0, 0.0, 0.0, 0)
		self.clear()

		# Set projection and modelview matrices ready for rendering the background
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(self.height, self.window_aspect_ratio, .1, 1000)
		glMatrixMode(GL_MODELVIEW)
		self.data.stars.background_vertex_list.draw(pyglet.gl.GL_POINTS)

		# Set projection and modelview matrices ready for rendering the stars.
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, self.width, 0, self.height)

		# Set modelview matrix to move and scale camera position
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		gluLookAt(
			self.relative_center[0], self.relative_center[1], 1.0,
			self.relative_center[0], self.relative_center[1], -1.0,
			0.0, 1.0, 0.0)
		# this must be inverse, otherwise zooming has weird artifacts
		self.data.stars.draw_scaled(1/self.foreground_scale)

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, self.width, 0, self.height)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		self.clock_display.draw()

	def on_key_press(self, symbol, modifiers):
		handler = self.key_handlers.get(symbol, lambda: None)
		handler()
	
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.absolute_center = (self.absolute_center[0] - dx*self.scale_over_height, 
			self.absolute_center[1] - dy*self.scale_over_height)

		self.relative_center = (self.absolute_center[0]*self.height_over_scale, 
			self.absolute_center[1]*self.height_over_scale)

class Application(object):
	"""Controller class for all game objects."""

	def __init__(self):
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

		galaxy_window = GalaxyWindow(1024, 768, data)

if __name__ == "__main__":
	application = Application()
	pyglet.app.run()
