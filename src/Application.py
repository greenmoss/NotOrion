#! python -O
from __future__ import division
from pyglet.window import key, Window
from pyglet.gl import *
import pyglet
import Stars

class Camera(object):

	def __init__(self, position=None, scale=None, width=640, height=480):
		if position is None:
			position = (0, 0)
		self.x, self.y = position
		self.eventual_x = self.x
		self.min_x = -20.0
		self.max_x = 20.0
		self.eventual_y = self.y
		self.min_y = -20.0
		self.max_y = 20.0

		if scale is None:
			scale = 1.0
		self.min_scale = 1.0
		self.max_scale = 100.0
		self.scale = scale
		self.eventual_scale = self.scale
		self.set_proportions(width, height)
		self.foreground_scale = 480

	def set_proportions(self, width, height):
		"""Set proportions for anything derived from height and/or width."""
		self.aspect_ratio = width/height

	def zoom(self, magnification):
		self.eventual_scale *= magnification

	def pan(self, x=0, y=0):
		self.eventual_x += self.scale*float(x)
		self.eventual_y += self.scale*float(y)

	def update(self):
		if self.eventual_x < self.min_x:
			self.eventual_x = self.min_x
		elif self.eventual_x > self.max_x:
			self.eventual_x = self.max_x
		self.x += self.eventual_x-self.x

		if self.eventual_y < self.min_y:
			self.eventual_y = self.min_y
		elif self.eventual_y > self.max_y:
			self.eventual_y = self.max_y
		self.y += self.eventual_y-self.y

		if self.eventual_scale < self.min_scale:
			self.eventual_scale = self.min_scale
		elif self.eventual_scale > self.max_scale:
			self.eventual_scale = self.max_scale
		self.scale += self.eventual_scale-self.scale

	def focus_on_background(self, width, height):
		"Set projection and modelview matrices ready for rendering the background"

		# Set projection matrix suitable for 2D rendering"
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		# why is 64 the magic number to keep background stars at constant distances?
		field_of_view = height/64
		gluPerspective(field_of_view, self.aspect_ratio, .1, 1000)
		glMatrixMode(GL_MODELVIEW)

	def focus_on_foreground(self, width, height):
		"Set projection and modelview matrices ready for rendering the stars."

		# Set projection matrix suitable for 2D rendering"
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(
			-height*self.aspect_ratio,
			height*self.aspect_ratio,
			-height,
			height)

		# Set modelview matrix to move, scale & rotate to camera position"
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		height_ratio = height/self.scale
		gluLookAt(
			self.x*height_ratio, self.y*height_ratio, 1.0,
			self.x*height_ratio, self.y*height_ratio, -1.0,
			0.0, 1.0, 0.0)

	def focus_on_hud(self, width, height):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, width, 0, height)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

class GalaxyWindow(Window):

	def __init__(self):
		super(GalaxyWindow, self).__init__(resizable=True, caption='Galaxy')
		self.clock_display = pyglet.clock.ClockDisplay()
		glClearColor(0.0, 0.0, 0.0, 0)
		self.camera = Camera((0, 0), 5, self.width, self.height)

		self.key_handlers = {
			key.Q: lambda: self.close(),
			key.ESCAPE: lambda: self.close(),
			key.MINUS: lambda: self.camera.zoom(2.0),
			key.EQUAL: lambda: self.camera.zoom(0.5),
			key.LEFT: lambda: self.camera.pan(x=-1),
			key.RIGHT: lambda: self.camera.pan(x=1),
			key.DOWN: lambda: self.camera.pan(y=-1),
			key.UP: lambda: self.camera.pan(y=1),
		}

	def on_draw(self):
		self.clear()
		self.camera.update()
		global stars

		self.camera.focus_on_background(self.width, self.height)
		stars.draw_background()

		self.camera.focus_on_foreground(self.width, self.height)
		stars.draw_scaled(self.camera.foreground_scale/self.camera.scale)

		self.camera.focus_on_hud(self.width, self.height)
		self.clock_display.draw()

	def on_key_press(self, symbol, modifiers):
		handler = self.key_handlers.get(symbol, lambda: None)
		handler()
	
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		# scale down dx/dy so screen tracks mouse
		tracking_speed = self.height/480*240.0
		reduced_x = -1*(dx/tracking_speed)
		reduced_y = -1*(dy/tracking_speed)
		self.camera.pan(x=reduced_x,y=reduced_y)

	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		# must be larger than 1.0; increase it for faster zoom
		zoom_speed = 1.01
		converted_y = (zoom_speed**scroll_y)
		self.camera.zoom(converted_y)
	
	def on_resize(self, width, height):
		self.camera.set_proportions(width, height)
		glViewport(0, 0, width, height)
		glMatrixMode(gl.GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, width, 0, height, -1, 1)
		glMatrixMode(gl.GL_MODELVIEW)

class Application(object):
	"""Controller class for all game objects."""

	def __init__(self):
		global stars
		stars = Stars.All()

		galaxy_window = GalaxyWindow()
		pyglet.app.run()

if __name__ == "__main__":
	application = Application()
