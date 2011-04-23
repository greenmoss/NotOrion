#! python -O
from __future__ import division
from pyglet.window import key, Window
from pyglet.gl import *
import pyglet
import Stars

class GalaxyWindow(Window):

	def __init__(self, data):
		super(GalaxyWindow, self).__init__(resizable=True, caption='Galaxy', width=1024, height=768)
		self.data = data
		self.clock_display = pyglet.clock.ClockDisplay()

		self.key_handlers = {
			key.ESCAPE: lambda: self.close(),
			key.HOME: lambda: self.handle_home_key(),
			key.Q: lambda: self.close(),
		}

		print "left: %i, right: %i, bottom: %i, top: %i" % (self.data.stars.left_bounding_x, self.data.stars.right_bounding_x, self.data.stars.bottom_bounding_y, self.data.stars.top_bounding_y)

		self.min_absolute_center_x = -10.0
		self.max_absolute_center_x = 10.0

		self.min_absolute_center_y = -10.0
		self.max_absolute_center_y = 10.0

		self.min_foreground_scale = 1.0
		self.max_foreground_scale = 10.0
		self.reset_scale = (self.max_foreground_scale-self.min_foreground_scale)/2

		self.reset_foreground()

		self.scale_indicator_size = 50.0
		self.scale_indicator_offset = 10.0

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
		self.coords_conversion_labels = [
			pyglet.text.Label(
				color=(255,255,255,128),
				font_name='Arial', font_size=10,
				text="no coordinates set",
				anchor_x='right', anchor_y='top'),
			pyglet.text.Label(
				color=(255,255,255,128),
				font_name='Arial', font_size=10,
				text="no coordinates set",
				anchor_x='right', anchor_y='top')
		]

		self.set_variables_from_window_size()

		self.calculate_mini_screen()

	def calculate_mini_screen(self):
		# calculate scale indicator vars
		self.absolute_width = self.max_absolute_center_x-self.min_absolute_center_x
		self.absolute_height = self.max_absolute_center_y-self.min_absolute_center_y
		if self.absolute_height > self.absolute_width:
			self.scale_indicator_height = self.scale_indicator_size
			self.scale_indicator_width = self.absolute_height/self.absolute_width*self.scale_indicator_size
		else:
			self.scale_indicator_width = self.scale_indicator_size
			self.scale_indicator_height = self.absolute_width/self.absolute_height*self.scale_indicator_size
		self.scale_indicator_width_ratio = self.scale_indicator_width/self.absolute_width
		self.scale_indicator_height_ratio = self.scale_indicator_height/self.absolute_height

		self.mini_map_right_x = self.width-self.scale_indicator_offset
		self.mini_map_left_x = self.mini_map_right_x-self.scale_indicator_width
		self.mini_map_bottom_y = self.scale_indicator_offset
		self.mini_map_top_y = self.mini_map_bottom_y+self.scale_indicator_height
		self.mini_map_vertices = pyglet.graphics.vertex_list(4,
			('v2f', (
				self.mini_map_left_x, self.mini_map_bottom_y,
				self.mini_map_right_x, self.mini_map_bottom_y,
				self.mini_map_right_x, self.mini_map_top_y,
				self.mini_map_left_x, self.mini_map_top_y)),
			('c4B', (
				255, 255, 255, 255,
				255, 255, 255, 255,
				255, 255, 255, 255,
				255, 255, 255, 255))
		)

		# convert screen coordinates to origin:0,0 and scale downward to minimap size
		(lower_left_x, lower_left_y) = self.screen_coords_to_absolute(0, 0)
		(upper_right_x, upper_right_y) = self.screen_coords_to_absolute(self.width, self.height)
		mini_screen_left_x = self.mini_map_left_x+((lower_left_x+(self.absolute_width/2))*self.scale_indicator_width_ratio)
		mini_screen_bottom_y = self.mini_map_bottom_y+((lower_left_y+(self.absolute_height/2))*self.scale_indicator_height_ratio)
		mini_screen_right_x = self.mini_map_left_x+((upper_right_x+(self.absolute_width/2))*self.scale_indicator_width_ratio)
		mini_screen_top_y = self.mini_map_bottom_y+((upper_right_y+(self.absolute_height/2))*self.scale_indicator_height_ratio)
		self.mini_screen_vertices = pyglet.graphics.vertex_list(4,
			('v2f', (
				mini_screen_left_x, mini_screen_bottom_y,
				mini_screen_right_x, mini_screen_bottom_y,
				mini_screen_right_x, mini_screen_top_y,
				mini_screen_left_x, mini_screen_top_y)),
			('c4B', (
				0, 255, 0, 255,
				0, 255, 0, 255,
				0, 255, 0, 255,
				0, 255, 0, 255))
		)
	
	def debug_star_coords(self, index):
		return "%s; abs coords: %0.4f, %0.4f; rel coords: %0.4f, %0.4f" % (self.data.stars.named[index].name, self.data.stars.named[index].sprite.x/self.scaled_foreground, self.data.stars.named[index].sprite.y/self.scaled_foreground, self.data.stars.named[index].sprite.x, self.data.stars.named[index].sprite.y)

	def handle_home_key(self):
		self.reset_foreground()
		self.set_foreground_scale_variables()

	def reset_foreground(self):
		self.absolute_center_x = 0.0
		self.absolute_center_y = 0.0
		self.foreground_scale = self.reset_scale
	
	def set_variables_from_window_size(self):
		"""Set all variables that are derived from the dimensions of the window."""
		self.smallest_window_dimension = self.height
		if self.width < self.height:
			self.smallest_window_dimension = self.width

		self.screen_aspect_ratio = self.width/self.height
		
		# why is 64 the magic number to keep background stars at fixed positions?
		self.background_field_of_view = self.height/64

		self.set_foreground_scale_variables()

		self.mouse_tracking_speed = self.smallest_window_dimension/2

		# set "scaling box" dimensions

		# many debugging labels
		top_offset = 10
		top_separator_height = 15
		self.window_measurements_label.x = self.width-10
		self.window_measurements_label.y = self.height-top_offset
		top_offset += top_separator_height

		self.look_coords_label.x = self.width-10
		self.look_coords_label.y = self.height-top_offset
		top_offset += top_separator_height

		for label in self.coords_conversion_labels:
			label.x = self.width-10
			label.y = self.height-top_offset
			top_offset += top_separator_height

		self.star0_coords.x = self.width-10
		self.star0_coords.y = self.height-top_offset
		self.star0_coords.text = self.debug_star_coords(0)
		top_offset += top_separator_height

		self.star1_coords.x = self.width-10
		self.star1_coords.y = self.height-top_offset
		self.star1_coords.text = self.debug_star_coords(1)
		top_offset += top_separator_height

		self.window_measurements_label.text = 'width: %i; height: %i; screen_aspect_ratio: %0.4f'%(self.width, self.height, self.screen_aspect_ratio)
		self.look_coords_label.text = "abs center; x,y: %0.4f, %0.4f; foreground scale: %0.4f; rel center x,y: %0.2f, %0.2f" % (self.absolute_center_x, self.absolute_center_y, self.foreground_scale, self.relative_center_x, self.relative_center_y)

	def set_foreground_scale_variables(self):
		self.scaled_foreground = self.smallest_window_dimension/self.foreground_scale
		self.relative_center_x = float(self.absolute_center_x)*self.scaled_foreground
		self.relative_center_y = float(self.absolute_center_y)*self.scaled_foreground
		#print "reverse x,y: %0.4f %0.4f"%(self.relative_center_x/self.scaled_foreground, self.relative_center_y/self.scaled_foreground)

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
		gluPerspective(self.background_field_of_view, self.screen_aspect_ratio, .1, 1000)
		glMatrixMode(GL_MODELVIEW)

	def focus_on_hud(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, self.width, 0, self.height)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

	def on_draw(self):
		glClearColor(0.0, 0.0, 0.0, 0)
		self.clear()

		self.focus_on_background()
		self.data.stars.draw_background()

		self.focus_on_foreground()
		# this must be inverse, otherwise zooming has weird artifacts
		self.data.stars.draw_scaled(1/self.foreground_scale)

		self.focus_on_hud()
		self.look_coords_label.draw()
		self.star0_coords.draw()
		self.star1_coords.draw()
		self.window_measurements_label.draw()
		self.clock_display.draw()
		for label in self.coords_conversion_labels:
			label.draw()
		# zoom indicator
		self.mini_map_vertices.draw(pyglet.gl.GL_LINE_LOOP)
		self.mini_screen_vertices.draw(pyglet.gl.GL_LINE_LOOP)

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
		if self.absolute_center_y < self.min_absolute_center_y:
			self.absolute_center_y = self.min_absolute_center_y
		elif self.absolute_center_y > self.max_absolute_center_y:
			self.absolute_center_y = self.max_absolute_center_y

		self.set_foreground_scale_variables()
		self.look_coords_label.text = "abs center; x,y: %0.4f, %0.4f; foreground scale: %0.4f; rel center x,y: %0.2f, %0.2f" % (self.absolute_center_x, self.absolute_center_y, self.foreground_scale, self.relative_center_x, self.relative_center_y)
		(lower_left_x, lower_left_y) = self.screen_coords_to_absolute(0, 0)
		self.generic_coords_label('lower left absolute', 0, lower_left_x, lower_left_y)
		(upper_right_x, upper_right_y) = self.screen_coords_to_absolute(self.width, self.height)
		self.generic_coords_label('upper right absolute', 1, upper_right_x, upper_right_y)
		self.calculate_mini_screen()

	def on_mouse_press(self, x, y, button, modifiers):
		(abs_x, abs_y) = self.screen_coords_to_absolute(x, y)
		offset_x = abs_x - self.absolute_center_x
		offset_y = abs_y - self.absolute_center_y
		self.generic_coords_label('click difference', 0, offset_x, offset_y)

	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		# .01 more or less than 1.0 should be fast enough
		zoom_speed = 1.01
		converted_y = (zoom_speed**scroll_y)

		self.foreground_scale *= converted_y
		if self.foreground_scale < self.min_foreground_scale:
			self.foreground_scale = self.min_foreground_scale
		elif self.foreground_scale > self.max_foreground_scale:
			self.foreground_scale = self.max_foreground_scale

		if (self.foreground_scale > self.min_foreground_scale) and (self.foreground_scale < self.max_foreground_scale):
			self.generic_coords_label('current absolute center', 0, self.absolute_center_x, self.absolute_center_y)
			(abs_x, abs_y) = self.screen_coords_to_absolute(x, y)
			offset_x = (self.absolute_center_x-abs_x)/2
			offset_y = (self.absolute_center_y-abs_y)/2
			#scaled_offset_x = 1/offset_x
			#scaled_offset_y = 1/offset_y
			#self.generic_coords_label('new absolute center', offset_x, offset_y)
			#self.absolute_center_x = offset_x
			#self.absolute_center_y = offset_y

		self.set_foreground_scale_variables()
		self.calculate_mini_screen()
		self.look_coords_label.text = "abs center; x,y: %0.4f, %0.4f; foreground scale: %0.4f; rel center x,y: %0.2f, %0.2f" % (self.absolute_center_x, self.absolute_center_y, self.foreground_scale, self.relative_center_x, self.relative_center_y)
		self.star0_coords.text = self.debug_star_coords(0)
		self.star1_coords.text = self.debug_star_coords(1)
	
	def on_resize(self, width, height):
		self.set_variables_from_window_size()
		self.calculate_mini_screen()
		glViewport(0, 0, width, height)
		glMatrixMode(gl.GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, width, 0, height, -1, 1)
		glMatrixMode(gl.GL_MODELVIEW)
	
	def relative_coords_to_absolute(self, relative_x, relative_y):
		absolute_x = relative_x/self.scaled_foreground
		absolute_y = relative_y/self.scaled_foreground
		return (absolute_x, absolute_y)
	
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
		return self.relative_coords_to_absolute(relative_x, relative_y)

	def generic_coords_label(self, event, which, x, y):
		self.coords_conversion_labels[which].text = "%s x,y: %0.4f, %0.4f"%(event, x, y)

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
				Stars.BackgroundStar((1, 2), (200, 255, 255)),
				Stars.BackgroundStar((-5, 3), (255, 255, 200)),
				Stars.BackgroundStar((4, -1), (255, 200, 255)),
				Stars.BackgroundStar((2, -3), (255, 255, 255)),
				Stars.BackgroundStar((-4, 0), (255, 255, 215)),
				Stars.BackgroundStar((-2, -7), (255, 215, 255)),
				Stars.BackgroundStar((1, 7), (255, 255, 255)),
				Stars.BackgroundStar((-6, -5), (228, 255, 255)),
				Stars.BackgroundStar((2, -6), (255, 255, 228)),
				Stars.BackgroundStar((-8, 4), (255, 215, 255)),
			])

		galaxy_window = GalaxyWindow(data)

class DataContainer(object):
	"""A simple object to store all application data."""
	def __init__(self):
		True

if __name__ == "__main__":
	application = Application()
	pyglet.app.run()
