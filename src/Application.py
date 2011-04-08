#! python -O
from __future__ import division
from pyglet.window import key, Window
from pyglet.gl import *
import pyglet
import Stars

class GalaxyWindow(Window):

	def __init__(self):
		super(GalaxyWindow, self).__init__(resizable=True, caption='Galaxy', width=1024, height=768)
		self.clock_display = pyglet.clock.ClockDisplay()
		glClearColor(0.0, 0.0, 0.0, 0)

		self.key_handlers = {
			key.Q: lambda: self.close(),
			key.ESCAPE: lambda: self.close(),
		}

		self.min_absolute_center_x = -10.0
		self.max_absolute_center_x = 10.0
		self.absolute_center_x = 0.0

		self.min_foreground_center_y = -10.0
		self.max_foreground_center_y = 10.0
		self.absolute_center_y = 0.0

		self.min_foreground_scale = 1.0
		self.max_foreground_scale = 10.0
		self.foreground_scale = 1.0

		self.foreground_scale_label = pyglet.text.Label(
			color=(255,255,255,128),
			font_name='Arial', font_size=10,
			y=5, anchor_x='right', anchor_y='bottom')
		self.look_coords_label = pyglet.text.Label(
			color=(255,255,255,128),
			font_name='Arial', font_size=10,
			anchor_x='right', anchor_y='top'
			)
		self.star0_coords = pyglet.text.Label(
			color=(255,255,255,128),
			font_name='Arial', font_size=10,
			anchor_x='right', anchor_y='top'
			)
		self.star1_coords = pyglet.text.Label(
			color=(255,255,255,128),
			font_name='Arial', font_size=10,
			anchor_x='right', anchor_y='top'
			)
		self.window_measurements_label = pyglet.text.Label(
			color=(255,255,255,128),
			font_name='Arial', font_size=10,
			anchor_x='right', anchor_y='top')
		self.coords_conversion_label = pyglet.text.Label(
			color=(255,255,255,128),
			font_name='Arial', font_size=10,
			text="no conversions available yet",
			anchor_x='right', anchor_y='top')

		self.set_variables_from_window_size()
	
	def debug_star_coords(self, index):
		global stars
		return "%s; abs coords: %0.4f, %0.4f; rel coords: %0.4f, %0.4f" % (stars.named[index].name, stars.named[index].sprite.x/self.scaled_height, stars.named[index].sprite.y/self.scaled_height, stars.named[index].sprite.x, stars.named[index].sprite.y)
	
	def set_variables_from_window_size(self):
		"""Set all variables that are derived from the dimensions of the window."""
		self.mouse_tracking_speed = self.height/2

		self.aspect_ratio = self.width/self.height
		# why is 64 the magic number to keep background stars at fixed positions?
		self.field_of_view = self.height/64

		self.set_foreground_scale_variables()

		# many debugging labels
		self.foreground_scale_label.x = self.width-10

		self.window_measurements_label.x = self.width-10
		self.window_measurements_label.y = self.height-10

		self.look_coords_label.x = self.width-10
		self.look_coords_label.y = self.height-25

		self.coords_conversion_label.x = self.width-10
		self.coords_conversion_label.y = self.height-40

		self.star0_coords.x = self.width-10
		self.star0_coords.y = self.height-55
		self.star0_coords.text = self.debug_star_coords(0)

		self.star1_coords.x = self.width-10
		self.star1_coords.y = self.height-70
		self.star1_coords.text = self.debug_star_coords(1)

		self.window_measurements_label.text = 'width: %i; height: %i; aspect_ratio: %0.4f'%(self.width, self.height, self.aspect_ratio)
		self.look_coords_label.text = "abs center; x,y: %0.4f, %0.4f; foreground scale: %0.4f; rel center x,y: %0.2f, %0.2f" % (self.absolute_center_x, self.absolute_center_y, self.foreground_scale, self.relative_center_x, self.relative_center_y)

	def set_foreground_scale_variables(self):
		self.scaled_height = self.height/self.foreground_scale
		self.relative_center_x = self.absolute_center_x*self.scaled_height
		self.relative_center_y = self.absolute_center_y*self.scaled_height
		#print "reverse x,y: %0.4f %0.4f"%(self.relative_center_x/self.scaled_height, self.relative_center_y/self.scaled_height)

	def focus_on_foreground(self):
		"Set projection and modelview matrices ready for rendering the stars."

		# Set projection matrix suitable for 2D rendering"
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(-self.width, self.width, -self.height, self.height)

		# Set modelview matrix to move and scale camera position"
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		gluLookAt(
			self.relative_center_x, self.relative_center_y, 1.0,
			self.relative_center_x, self.relative_center_y, -1.0,
			0.0, 1.0, 0.0)

	def focus_on_background(self):
		"Set projection and modelview matrices ready for rendering the background"
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
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
		# this must be inverse, otherwise zooming has weird artifacts
		stars.draw_scaled(1/self.foreground_scale)

		self.focus_on_hud()
		self.foreground_scale_label.text = "scale: %0.4f" % self.foreground_scale
		self.foreground_scale_label.draw()
		self.look_coords_label.draw()
		self.star0_coords.draw()
		self.star1_coords.draw()
		self.window_measurements_label.draw()
		self.clock_display.draw()
		self.coords_conversion_label.draw()

	def on_key_press(self, symbol, modifiers):
		handler = self.key_handlers.get(symbol, lambda: None)
		handler()
	
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		reduced_x = -1*(dx/self.mouse_tracking_speed)
		reduced_y = -1*(dy/self.mouse_tracking_speed)

		self.absolute_center_x += self.foreground_scale*float(reduced_x)
		if self.absolute_center_x < self.min_absolute_center_x:
			self.absolute_center_x = self.min_absolute_center_x
		elif self.absolute_center_x > self.max_absolute_center_x:
			self.absolute_center_x = self.max_absolute_center_x
		self.absolute_center_y += self.foreground_scale*float(reduced_y)
		if self.absolute_center_y < self.min_foreground_center_y:
			self.absolute_center_y = self.min_foreground_center_y
		elif self.absolute_center_y > self.max_foreground_center_y:
			self.absolute_center_y = self.max_foreground_center_y

		self.set_foreground_scale_variables()
		self.look_coords_label.text = "abs center; x,y: %0.4f, %0.4f; foreground scale: %0.4f; rel center x,y: %0.2f, %0.2f" % (self.absolute_center_x, self.absolute_center_y, self.foreground_scale, self.relative_center_x, self.relative_center_y)

	def on_mouse_press(self, x, y, button, modifiers):
		self.convert_coords_debug('press', x, y)

	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		# .01 more or less than 1.0 should be fast enough
		zoom_speed = 1.01
		converted_y = (zoom_speed**scroll_y)

		self.foreground_scale *= converted_y
		if self.foreground_scale < self.min_foreground_scale:
			self.foreground_scale = self.min_foreground_scale
		elif self.foreground_scale > self.max_foreground_scale:
			self.foreground_scale = self.max_foreground_scale

		self.set_foreground_scale_variables()
		self.look_coords_label.text = "abs center; x,y: %0.4f, %0.4f; foreground scale: %0.4f; rel center x,y: %0.2f, %0.2f" % (self.absolute_center_x, self.absolute_center_y, self.foreground_scale, self.relative_center_x, self.relative_center_y)
		self.star0_coords.text = self.debug_star_coords(0)
		self.star1_coords.text = self.debug_star_coords(1)

		if (self.foreground_scale > self.min_foreground_scale) and (self.foreground_scale < self.max_foreground_scale):
			self.convert_coords_debug('scroll', x, y)
	
	def on_resize(self, width, height):
		self.set_variables_from_window_size()
		glViewport(0, 0, width, height)
		glMatrixMode(gl.GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, width, 0, height, -1, 1)
		glMatrixMode(gl.GL_MODELVIEW)
	
	def screen_coords_to_relative(self, x, y):
		# to center 0,0
		center0_x = (x-self.width/2)
		center0_y = (y-self.height/2)
		# account for window scaling (why 2?)
		scaled_x = center0_x*2
		scaled_y = center0_y*2
		# offset (?)
		relative_x = scaled_x+self.relative_center_x
		relative_y = scaled_y+self.relative_center_y
		return (relative_x, relative_y)
	
	def screen_coords_to_absolute(self, x, y):
		(relative_x, relative_y) = self.screen_coords_to_relative(x, y)
		absolute_x = relative_x/self.scaled_height
		absolute_y = relative_y/self.scaled_height
		return (absolute_x, absolute_y)

	def convert_coords_debug(self, event, x, y):
		(rel_x, rel_y) = self.screen_coords_to_relative(x, y)
		(abs_x, abs_y) = self.screen_coords_to_absolute(x, y)
		self.coords_conversion_label.text = "%s pos x,y: %0.1f, %0.1f; rel scaled x,y: %0.1f, %0.1f; abs scaled x,y: %0.1f, %0.1f"%(event, x, y, rel_x, rel_y, abs_x, abs_y)

class Application(object):
	"""Controller class for all game objects."""

	def __init__(self):
		global stars
		stars = Stars.All()

		galaxy_window = GalaxyWindow()
		pyglet.app.run()

if __name__ == "__main__":
	application = Application()
