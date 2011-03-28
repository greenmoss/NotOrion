#! python -O
from __future__ import division
from pyglet.window import key, Window
from pyglet.gl import *
import pyglet
import Stars

class Camera(object):

	def __init__(self, position=None, scale=None):
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
			scale = 1
		self.min_scale = 1.0
		self.max_scale = 100.0
		self.scale = scale
		self.eventual_scale = self.scale
		self.label_scale = 512
		self.star_scale = 512

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
		aspect_ratio = width/height
		gluOrtho2D(
			-self.scale*aspect_ratio,
			+self.scale*aspect_ratio,
			-self.scale,
			+self.scale)

		# Set modelview matrix to move, scale & rotate to camera position"
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		gluLookAt(
			self.x, self.y, 1.0,
			self.x, self.y, -1.0,
			0.0, 1.0, 0.0)

	def focus_on_star_field(self, width, height):
		"Set projection and modelview matrices ready for rendering the stars."

		# Set projection matrix suitable for 2D rendering"
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		aspect_ratio = width/height
		gluOrtho2D(
			-self.star_scale*aspect_ratio,
			+self.star_scale*aspect_ratio,
			-self.star_scale,
			+self.star_scale)

		# Set modelview matrix to move, scale & rotate to camera position"
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		diff = self.star_scale /self.scale
		gluLookAt(
			self.x*diff, self.y*diff, 1.0,
			self.x*diff, self.y*diff, -1.0,
			0.0, 1.0, 0.0)

	def focus_on_hud(self, width, height):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, width, 0, height)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

	def scale_label_coordinates(self, unscaled_x, unscaled_y):
		scaled_x = (unscaled_x)*self.label_scale/self.scale
		scaled_y = (unscaled_y)*self.label_scale/self.scale
		return scaled_x, scaled_y

class GalaxyWindow(Window):

	def __init__(self):
		super(GalaxyWindow, self).__init__(resizable=True)
		self.clock_display = pyglet.clock.ClockDisplay()
		glClearColor(0.0, 0.0, 0.0, 0)
		self.camera = Camera((0, 0), 5)

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

		self.camera.focus_on_background(self.width, self.height)
		# background stars/points drawing goes here

		self.camera.focus_on_star_field(self.width, self.height)
		global stars
		stars.draw_scaled(self.camera.star_scale/self.camera.scale)

		self.camera.focus_on_hud(self.width, self.height)
		self.clock_display.draw()

	def on_key_press(self, symbol, modifiers):
		handler = self.key_handlers.get(symbol, lambda: None)
		handler()
	
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		# scale down dx/dy so screen tracks mouse
		tracking_speed = 240.0
		reduced_x = -1*(dx/tracking_speed)
		reduced_y = -1*(dy/tracking_speed)
		self.camera.pan(x=reduced_x,y=reduced_y)

	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		# must be larger than 1.0; increase it for faster zoom
		zoom_speed = 1.01
		converted_y = (zoom_speed**scroll_y)
		self.camera.zoom(converted_y)
	
	def on_resize(self, width, height):
		print "width, height: ", [width, height]

class Application(object):
	"""Controller class for all game objects."""

	def __init__(self):
		global stars
		stars = Stars.All()

		galaxy_window = GalaxyWindow()
		pyglet.app.run()

if __name__ == "__main__":
	application = Application()
