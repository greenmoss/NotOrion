#! python -O
from __future__ import division
from pyglet.window import key, Window
from pyglet.gl import *
import pyglet
import Stars

class GalaxyWindow(Window):

	def __init__(self):
		super(GalaxyWindow, self).__init__(resizable=True, caption='Galaxy')
		self.clock_display = pyglet.clock.ClockDisplay()
		glClearColor(0.0, 0.0, 0.0, 0)

		self.key_handlers = {
			key.Q: lambda: self.close(),
			key.ESCAPE: lambda: self.close(),
		}
		self.foreground_scale_label = pyglet.text.Label(
			color=(255,128,128,128),
			font_name='Arial', font_size=15,
			y=5, anchor_x='right', anchor_y='bottom')
		self.set_variables_from_window_size()

		self.foreground_center_x, self.foreground_center_y = (0,0)
		self.min_foreground_center_x = -20.0
		self.max_foreground_center_x = 20.0
		self.min_foreground_center_y = -20.0
		self.max_foreground_center_y = 20.0

		self.min_foreground_scale = 1.0
		self.max_foreground_scale = 100.0
		self.foreground_scale = 5.0
		self.foreground_absolute_scale = 480

	def zoom_foreground(self, magnification, to_x=None, to_y=None):
		self.foreground_scale *= magnification
		if self.foreground_scale < self.min_foreground_scale:
			self.foreground_scale = self.min_foreground_scale
		elif self.foreground_scale > self.max_foreground_scale:
			self.foreground_scale = self.max_foreground_scale
		#print "x, y", [self.foreground_center_x, self.foreground_center_y]
		if to_x and to_y:
			#print "to_x, to_y", [to_x, to_y]
			pass

	def pan_foreground(self, x=0, y=0):
		#print "before pan: x, y", [self.foreground_center_x, self.foreground_center_y]
		self.foreground_center_x += self.foreground_scale*float(x)
		if self.foreground_center_x < self.min_foreground_center_x:
			self.foreground_center_x = self.min_foreground_center_x
		elif self.foreground_center_x > self.max_foreground_center_x:
			self.foreground_center_x = self.max_foreground_center_x
		self.foreground_center_y += self.foreground_scale*float(y)
		if self.foreground_center_y < self.min_foreground_center_y:
			self.foreground_center_y = self.min_foreground_center_y
		elif self.foreground_center_y > self.max_foreground_center_y:
			self.foreground_center_y = self.max_foreground_center_y
		#print "after pan: x, y", [self.foreground_center_x, self.foreground_center_y]

	def focus_on_foreground(self):
		"Set projection and modelview matrices ready for rendering the stars."

		# Set projection matrix suitable for 2D rendering"
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(
			-self.height*self.aspect_ratio,
			self.height*self.aspect_ratio,
			-self.height,
			self.height)

		# Set modelview matrix to move and scale camera position"
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		height_ratio = self.height/self.foreground_scale
		gluLookAt(
			self.foreground_center_x*height_ratio, self.foreground_center_y*height_ratio, 1.0,
			self.foreground_center_x*height_ratio, self.foreground_center_y*height_ratio, -1.0,
			0.0, 1.0, 0.0)
	
	def set_variables_from_window_size(self):
		"""Set all variables that are derived from the dimensions of the window."""
		self.mouse_tracking_speed = self.height/2
		self.foreground_scale_label.x = self.width-10
		self.aspect_ratio = self.width/self.height
		self.field_of_view = self.height/64

	def focus_on_background(self):
		"Set projection and modelview matrices ready for rendering the background"
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		# why is 64 the magic number to keep background stars at constant distances?
		gluPerspective(self.field_of_view, self.aspect_ratio, .1, 1000)
		glMatrixMode(GL_MODELVIEW)

	def focus_on_hud(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, self.width, 0, self.height)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

	def on_draw(self):
		self.clear()
		global stars

		self.focus_on_background()
		stars.draw_background()

		self.focus_on_foreground()
		stars.draw_scaled(self.foreground_absolute_scale/self.foreground_scale)
		#print "star0 sprite x, y: ",[stars.named[0].sprite.x, stars.named[0].sprite.y]
		#print "star1 sprite x, y: ",[stars.named[1].sprite.x, stars.named[1].sprite.y]
		#print "star2 sprite x, y: ",[stars.named[2].sprite.x, stars.named[2].sprite.y]

		self.focus_on_hud()
		self.foreground_scale_label.text = str(self.foreground_scale)
		self.foreground_scale_label.draw()
		self.clock_display.draw()

	def on_key_press(self, symbol, modifiers):
		handler = self.key_handlers.get(symbol, lambda: None)
		handler()
	
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		reduced_x = -1*(dx/self.mouse_tracking_speed)
		reduced_y = -1*(dy/self.mouse_tracking_speed)
		self.pan_foreground(x=reduced_x,y=reduced_y)

	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		# must be larger than 1.0; increase it for faster zoom
		zoom_speed = 1.01
		converted_y = (zoom_speed**scroll_y)
		star_x = None
		star_y = None
		if (self.foreground_scale > self.min_foreground_scale) and (self.foreground_scale < self.max_foreground_scale):
			star_x = (x-self.width/2)/self.width
			star_y = (y-self.height/2)/self.height
		self.zoom_foreground(converted_y, star_x, star_y)
	
	def on_resize(self, width, height):
		self.set_variables_from_window_size()
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
