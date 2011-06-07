#! python -O
from __future__ import division
from pyglet.gl import *
import pyglet
import Stars

class RangeException(Exception): pass
class MissingDataException(Exception): pass

class Window(pyglet.window.Window):
	'All methods that are attached to the galaxy window.'
	max_dimension = 5000
	min_dimension = 50
	# .01 more or less than 1.0 should be fast enough zoom speed
	zoom_speed = 1.01
	# empty margin around outermost foreground stars, in window pixels
	window_margin = 100
	# mini-map offset, from right/bottom
	mini_map_offset = 20
	# size of mini-map; depending on which is greater, this will either be width or height
	mini_map_size = 75

	def __init__(self, width=1024, height=768, data=None):
		if not (self.min_dimension < width < self.max_dimension) or not (self.min_dimension < height < self.max_dimension):
			raise RangeException, "width and height must be between 50 and 5000"
		super(Window, self).__init__(resizable=True, caption='Galaxy', width=width, height=height, visible=False)
		if data == None:
			raise MissingDataException, "missing param: data"
		else:
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
			pyglet.window.key.ESCAPE: lambda: self.close(),
			pyglet.window.key.Q: lambda: self.close(),
		}

		self.derive_from_window_dimensions(self.width, self.height)
		self.set_scale(self.maximum_scale)

		self.set_center((0, 0))

		self.set_visible()

	def derive_mini_map(self):
		# mini-map play area dimensions should only need to be calculated once
		if not hasattr(self, 'mini_map_width'):
			if self.stars_bounding_x > self.stars_bounding_y:
				self.mini_map_width = self.mini_map_size
				self.mini_map_height = self.stars_bounding_y/self.stars_bounding_x*self.mini_map_size
			else:
				self.mini_map_height = self.mini_map_size
				self.mini_map_width = self.stars_bounding_x/self.stars_bounding_y*self.mini_map_size
			# ratio of absolute coordinates to mini-map coordinates
			# *should* be the same for width/bounding_x as height/bounding_y
			self.mini_map_to_absolute = self.mini_map_width/(self.stars_bounding_x-(self.window_margin*2.0))/self.maximum_scale

		# where is the foreground window on the playing field?
		right_top = self.window_to_absolute((self.width, self.height))
		left_bottom = self.window_to_absolute((0, 0))

		# hide the mini-map if the entire playing field is visible
		if (
			(right_top[0] >= self.stars_bounding_x+self.window_margin) and
			(right_top[1] >= self.stars_bounding_y+self.window_margin) and
			(left_bottom[0] <= -self.stars_bounding_x-self.window_margin) and
			(left_bottom[1] <= -self.stars_bounding_y-self.window_margin)
		):
			self.mini_map_visible = False
			return
		else:
			self.mini_map_visible = True

		self.mini_map_corners = {
			'top':self.mini_map_offset+self.mini_map_height,
			'right':self.width-self.mini_map_offset,
			'bottom':self.mini_map_offset,
			'left':self.width-self.mini_map_offset-self.mini_map_width
		}

		mini_map_center = (
			self.mini_map_corners['right']-(self.mini_map_corners['right']-self.mini_map_corners['left'])/2,
			self.mini_map_corners['top']-(self.mini_map_corners['top']-self.mini_map_corners['bottom'])/2,
		)

		# position of viewing area within playing field
		self.mini_map_window_corners = {
			'top':mini_map_center[1]+(right_top[1]*self.mini_map_to_absolute),
			'right':mini_map_center[0]+(right_top[0]*self.mini_map_to_absolute),
			'bottom':mini_map_center[1]+(left_bottom[1]*self.mini_map_to_absolute),
			'left':mini_map_center[0]+(left_bottom[0]*self.mini_map_to_absolute),
		}

		# ensure mini_map_window_corners do not fall outside mini_map_corners
		for corner in ['top', 'right']:
			if self.mini_map_window_corners[corner] > self.mini_map_corners[corner]:
				self.mini_map_window_corners[corner] = self.mini_map_corners[corner]
		for corner in ['bottom', 'left']:
			if self.mini_map_window_corners[corner] < self.mini_map_corners[corner]:
				self.mini_map_window_corners[corner] = self.mini_map_corners[corner]

		# construct/update mini-map and mini-window vertex lists
		self.mini_map_black_bg_vertex_list = pyglet.graphics.vertex_list( 4,
			('v2f', (
				self.mini_map_corners['right'], self.mini_map_corners['top'],
				self.mini_map_corners['right'], self.mini_map_corners['bottom'],
				self.mini_map_corners['left'], self.mini_map_corners['bottom'],
				self.mini_map_corners['left'], self.mini_map_corners['top'],
				)
			),
			('c3B/static', (
				0, 0, 0,
				0, 0, 0,
				0, 0, 0,
				0, 0, 0,
				)
			)
		)
		self.mini_map_transparent_bg_vertex_list = pyglet.graphics.vertex_list( 4,
			('v2f', (
				self.mini_map_corners['right'], self.mini_map_corners['top'],
				self.mini_map_corners['right'], self.mini_map_corners['bottom'],
				self.mini_map_corners['left'], self.mini_map_corners['bottom'],
				self.mini_map_corners['left'], self.mini_map_corners['top'],
				)
			),
			('c4B/static', (
				0, 0, 0, 200,
				0, 0, 0, 200,
				0, 0, 0, 200,
				0, 0, 0, 200,
				)
			)
		)
		self.mini_map_borders_vertex_list = pyglet.graphics.vertex_list( 4,
			('v2f', (
				self.mini_map_corners['right'], self.mini_map_corners['top'],
				self.mini_map_corners['right'], self.mini_map_corners['bottom'],
				self.mini_map_corners['left'], self.mini_map_corners['bottom'],
				self.mini_map_corners['left'], self.mini_map_corners['top'],
				)
			),
			('c3B/static', (
				32, 32, 32,
				32, 32, 32,
				32, 32, 32,
				32, 32, 32,
				)
			)
		)
		self.mini_window_vertex_list = pyglet.graphics.vertex_list( 4,
			('v2f', (
				self.mini_map_window_corners['right'], self.mini_map_window_corners['top'],
				self.mini_map_window_corners['right'], self.mini_map_window_corners['bottom'],
				self.mini_map_window_corners['left'], self.mini_map_window_corners['bottom'],
				self.mini_map_window_corners['left'], self.mini_map_window_corners['top'],
				)
			),
			('c3B/static', (
				48, 48, 48,
				48, 48, 48,
				48, 48, 48,
				48, 48, 48,
				)
			)
		)
	
	def derive_from_window_dimensions(self, width, height):
		"Set attributes that are based on window dimensions."
		self.half_width = width/2
		self.half_height = height/2

		# Derive minimum and maximum scale, based on minimum and maximum distances between foreground stars.
		self.minimum_dimension = (width < height) and width or height
			
		self.minimum_scale = self.data.stars.min_distance/self.minimum_dimension*2.0
		self.maximum_scale = self.data.stars.max_distance/self.minimum_dimension
		# 35 is the minimum window distance between each star sprite
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

		# every time we update the center, the mini-map will change
		self.derive_mini_map()
	
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

	def absolute_to_window(self, coordinates):
		"Translate absolute foreground coordinates into a window coordinate, accounting for window center and scale."
		return(
			coordinates[0]/self.foreground_scale+self.half_width-self.absolute_center[0],
			coordinates[1]/self.foreground_scale+self.half_height-self.absolute_center[1]
			)

	def window_to_absolute(self, coordinates):
		"Translate a window coordinate into absolute foreground coordinates, accounting for window center and scale."
		return(
			(self.absolute_center[0]+coordinates[0]-self.half_width)*self.foreground_scale,
			(self.absolute_center[1]+coordinates[1]-self.half_height)*self.foreground_scale
			)

	def on_draw(self):
		glClearColor(0.0, 0.0, 0.0, 0)
		self.clear()

		# origin is center of window
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(-self.half_width, self.half_width, -self.half_height, self.half_height)
		glMatrixMode(GL_MODELVIEW)

		# draw the background stars
		self.data.stars.background_vertex_list.draw(pyglet.gl.GL_POINTS)

		# if we're showing the mini-map, black out background stars under mini-map
		if self.mini_map_visible:
			# origin is lower-left of window
			glMatrixMode(GL_PROJECTION)
			glLoadIdentity()
			gluOrtho2D(0, self.width, 0, self.height)
			glMatrixMode(GL_MODELVIEW)

			# black-filled rectangle behind mini-map
			self.mini_map_black_bg_vertex_list.draw(pyglet.gl.GL_QUADS)

			# change back to origin at center of window
			glMatrixMode(GL_PROJECTION)
			glLoadIdentity()
			gluOrtho2D(-self.half_width, self.half_width, -self.half_height, self.half_height)
			glMatrixMode(GL_MODELVIEW)

		# set the center of the viewing area
		gluLookAt(
			self.absolute_center[0], self.absolute_center[1], 0.0,
			self.absolute_center[0], self.absolute_center[1], -100.0,
			0.0, 1.0, 0.0)

		# draw the foreground stars and other objects
		self.data.stars.draw_scaled(self.foreground_scale)

		# for HUD objects, set 2D view with origin at lower left
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, self.width, 0, self.height)
		glMatrixMode(GL_MODELVIEW)

		# reset identity stack
		glLoadIdentity()

		# if we're showing the mini-map, draw it
		if self.mini_map_visible:
			# translucent gray rectangle behind mini-map
			glEnable(GL_BLEND)
			glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
			self.mini_map_transparent_bg_vertex_list.draw(pyglet.gl.GL_QUADS)

			# borders of mini-map
			self.mini_map_borders_vertex_list.draw(pyglet.gl.GL_LINE_LOOP)

			# borders of mini-window within mini-map
			self.mini_window_vertex_list.draw(pyglet.gl.GL_LINE_LOOP)

	def on_key_press(self, symbol, modifiers):
		handler = self.key_handlers.get(symbol, lambda: None)
		handler()
	
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.set_center((self.absolute_center[0] - dx, self.absolute_center[1] - dy))

	def on_mouse_press(self, x, y, button, modifiers):
		pass

	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		prescale_absolute_mouse = self.window_to_absolute((x,y))

		self.set_scale(self.foreground_scale*(self.zoom_speed**scroll_y))

		postscale_absolute_mouse = self.window_to_absolute((x,y))

		# scale the prescale mouse according to the *new* foreground scale
		prescale_mouse = (prescale_absolute_mouse[0]/self.foreground_scale, prescale_absolute_mouse[1]/self.foreground_scale)
		postscale_mouse = (postscale_absolute_mouse[0]/self.foreground_scale, postscale_absolute_mouse[1]/self.foreground_scale)

		self.set_center(
			(
				prescale_mouse[0]-postscale_mouse[0]+self.absolute_center[0], 
				prescale_mouse[1]-postscale_mouse[1]+self.absolute_center[1]
			)
		)
	
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

# doesn't make sense to call this standalone, so no __main__
