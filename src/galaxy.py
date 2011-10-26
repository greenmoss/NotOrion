#! python -O
from __future__ import division
from pyglet.gl import *
import pyglet
import galaxy_objects

class RangeException(Exception): pass
class MissingDataException(Exception): pass

class WindowState(object):
	"A collection of attributes necessary for saving and restoring window state"
	def __init__(self):
		self.width = None
		self.height = None
		self.absolute_center = None
		self.foreground_scale = None

class Window(pyglet.window.Window):
	'All methods that are attached to the galaxy window.'
	max_dimension = 5000
	min_dimension = 400
	# .01 more or less than 1.0 should be fast enough zoom speed
	zoom_speed = 1.01
	# mini-map offset, from right/bottom
	mini_map_offset = 20
	# size of mini-map; depending on which is greater, this will either be width or height
	mini_map_size = 75
	# minimum distance between foreground stars/black holes
	minimum_foreground_separation = 10

	def __init__(self, data, width=1024, height=768):
		self.data = data
		if not hasattr(self.data, 'galaxy_window_state'):
			raise MissingDataException, "self.data must have attribute galaxy_window_state"
		if not isinstance(self.data.galaxy_window_state, WindowState):
			raise MissingDataException, "self.data.galaxy_window_state must be an instance of WindowState"
		if self.data.galaxy_window_state.width and self.data.galaxy_window_state.height:
			width = self.data.galaxy_window_state.width
			height = self.data.galaxy_window_state.height

		if not (self.min_dimension <= width <= self.max_dimension) or not (self.min_dimension <= height <= self.max_dimension):
			raise RangeException, "width and height must be between 400 and 5000"
		super(Window, self).__init__(resizable=True, caption='Galaxy', width=width, height=height, visible=False)

		# MUST have galaxy_objects
		if not hasattr(self.data, 'galaxy_objects'):
			raise MissingDataException, "self.data must have attribute galaxy_objects"
		if not isinstance(self.data.galaxy_objects, galaxy_objects.All):
			raise MissingDataException, "self.data.galaxy_objects must be an instance of galaxy_objects.All"
		self.foreground_bounding_y = self.data.galaxy_objects.top_bounding_y
		if -self.data.galaxy_objects.bottom_bounding_y > self.data.galaxy_objects.top_bounding_y:
			self.foreground_bounding_y = -self.data.galaxy_objects.bottom_bounding_y
		self.foreground_bounding_x = self.data.galaxy_objects.right_bounding_x
		if -self.data.galaxy_objects.left_bounding_x > self.data.galaxy_objects.right_bounding_x:
			self.foreground_bounding_x = -self.data.galaxy_objects.left_bounding_x

		self.clock_display = pyglet.clock.ClockDisplay()

		self.key_handlers = {
			pyglet.window.key.ESCAPE: lambda: self.close(),
			pyglet.window.key.Q: lambda: self.close(),
		}

		self.derive_from_window_dimensions(self.width, self.height)
		if self.data.galaxy_window_state.foreground_scale:
			self.set_scale(self.data.galaxy_window_state.foreground_scale)
		else:
			self.set_scale(self.maximum_scale)

		if self.data.galaxy_window_state.absolute_center:
			self.set_center(self.data.galaxy_window_state.absolute_center)
		else:
			self.set_center((0, 0))

		pyglet.clock.schedule_interval(self.animate, 1/60.)

		self.set_visible()

	def derive_mini_map(self):
		# mini-map play area dimensions should only need to be calculated once
		if not hasattr(self, 'mini_map_width'):
			map_height = self.foreground_bounding_y
			map_width = self.foreground_bounding_x
			ratio = map_height/map_width
			if map_width > map_height:
				self.mini_map_width = self.mini_map_size
				self.mini_map_height = self.mini_map_width*ratio
			else: #map_width <= map_height
				self.mini_map_height = self.mini_map_size
				self.mini_map_width = self.mini_map_height/ratio
			# ratio of absolute coordinates to mini-map coordinates
			# cached as a property of self
			self.mini_map_ratio = self.mini_map_width/map_width

		# where is the foreground window on the playing field?
		right_top = self.window_to_absolute((self.width, self.height))
		left_bottom = self.window_to_absolute((0, 0))

		# hide the mini-map if the entire playing field is visible
		# the integer modifiers ensure the mini-map becomes visible whenever a portion of a star or its label moves offscreen
		if (
			(right_top[0] >= self.foreground_bounding_x+60) and
			(right_top[1] >= self.foreground_bounding_y+20) and
			(left_bottom[0] <= -self.foreground_bounding_x-60) and
			(left_bottom[1] <= -self.foreground_bounding_y-40)
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
			self.mini_map_corners['right']-(self.mini_map_corners['right']-self.mini_map_corners['left'])/2.0,
			self.mini_map_corners['top']-(self.mini_map_corners['top']-self.mini_map_corners['bottom'])/2.0,
		)

		# position of viewing area within playing field
		self.mini_map_window_corners = {
			'top':mini_map_center[1]+int((right_top[1])*self.mini_map_ratio/2.0),
			'right':mini_map_center[0]+int((right_top[0])*self.mini_map_ratio/2.0),
			'bottom':mini_map_center[1]+int((left_bottom[1])*self.mini_map_ratio/2.0),
			'left':mini_map_center[0]+int((left_bottom[0])*self.mini_map_ratio/2.0),
		}

		# ensure mini_map_window_corners do not fall outside mini_map_corners
		if not(self.mini_map_corners['bottom'] < self.mini_map_window_corners['top'] < self.mini_map_corners['top']):
			self.mini_map_window_corners['top'] = self.mini_map_corners['top']
		if not(self.mini_map_corners['left'] < self.mini_map_window_corners['right'] < self.mini_map_corners['right']):
			self.mini_map_window_corners['right'] = self.mini_map_corners['right']
		if not(self.mini_map_corners['top'] > self.mini_map_window_corners['bottom'] > self.mini_map_corners['bottom']):
			self.mini_map_window_corners['bottom'] = self.mini_map_corners['bottom']
		if not(self.mini_map_corners['right'] > self.mini_map_window_corners['left'] > self.mini_map_corners['left']):
			self.mini_map_window_corners['left'] = self.mini_map_corners['left']

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

		# Derive minimum and maximum scale, based on minimum and maximum distances between foreground galaxy objects.
		self.minimum_dimension = (width < height) and width or height
			
		self.minimum_scale = self.data.galaxy_objects.min_distance/self.minimum_dimension*5.0
		self.maximum_scale = self.data.galaxy_objects.max_distance/self.minimum_dimension
		# restrict zooming out to the minimum distance between foreground sprites
		if(self.data.galaxy_objects.min_distance/self.maximum_scale < self.minimum_foreground_separation):
			self.maximum_scale = self.data.galaxy_objects.min_distance/self.minimum_foreground_separation
		if self.minimum_scale > self.maximum_scale:
			self.maximum_scale = self.minimum_scale
	
	def detect_mouseover_objects(self, x, y, radius=2, debug=False):
		'Given a mouse x/y position, detect any objects at/around this position'
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glLoadIdentity()

		glPushMatrix()

		# in normal rendered scene, we use gluLookAt
		# but this won't work with back buffer
		# so instead we'll use glTranslated
		translate_x = int(self.half_width - self.absolute_center[0] - 1)
		translate_y = int(self.half_height - self.absolute_center[1] - 1)
		glTranslated(translate_x,translate_y,0)

		# draw the foreground object masks
		self.data.galaxy_objects.draw_masks(self.foreground_scale)

		# convert click coordinates into absolute coordinates
		absolute_click = self.window_to_absolute((x,y))
		absolute_click = (int(absolute_click[0]/self.foreground_scale),int(absolute_click[1]/self.foreground_scale))

		length = (radius*2)+1
		area = length * length
		read_x = absolute_click[0]-radius+translate_x
		read_y = absolute_click[1]-radius+translate_y
		pixel_data_length = 4 * area # 4, one for each byte: R, G, B, A
		ctypes_buffer=(GLubyte * pixel_data_length)()
		glReadBuffer(GL_BACK)
		glReadPixels(read_x,read_y,length,length,GL_RGBA,GL_UNSIGNED_BYTE,ctypes_buffer)

		# find object(s) under the cursor
		colors = []
		bytes = []
		detected_objects = {}
		for byte_position in range(area):
			ctypes_position = byte_position*4

			alpha = ctypes_buffer[ctypes_position+3]
			if alpha < 255:
				colors.append( (0, 0, 0) )
				continue

			color = (
				ctypes_buffer[ctypes_position], #red
				ctypes_buffer[ctypes_position+1], #green
				ctypes_buffer[ctypes_position+2], #blue
			)
			detected_object = self.data.galaxy_objects.color_picks[color]
			if not detected_objects.has_key(detected_object):
				detected_objects[detected_object] = 0
			detected_objects[detected_object] += 1
			colors.append( color )

		if debug:
			print "pixel colors"
			for row in range(length-1, -1, -1):
				begin = row*length
				end = begin + length
				print colors[begin:end]

			# maximally-seen object is first
			for object in sorted(detected_objects, key=detected_objects.get, reverse=True):
				if type(object) == galaxy_objects.ForegroundStar:
					print "star: %s"%object.name
				elif type(object) == galaxy_objects.WormHole:
					print "worm hole: %s to %s"%(object.endpoints[0].name, object.endpoints[1].name)
				# maybe some day we'll also allow black holes to be picked

		glPopMatrix()

		return detected_objects

	def set_center(self, coordinates):
		"Set the window center, for rendering foreground objects."
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
		self.data.galaxy_window_state.absolute_center = self.absolute_center

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

		# the integer modifiers ensure all stars and labels remain visible at the limits of the pan area
		self.center_limits = {
			'top':self.foreground_bounding_y/foreground_scale+110-self.half_height,
			'right':self.foreground_bounding_x/foreground_scale+140-self.half_width,
			'bottom':-self.foreground_bounding_y/foreground_scale-120+self.half_height,
			'left':-self.foreground_bounding_x/foreground_scale-140+self.half_width,
		}
		if self.center_limits['top'] < self.center_limits['bottom']:
			self.center_limits['top'] = 0
			self.center_limits['bottom'] = 0
		if self.center_limits['right'] < self.center_limits['left']:
			self.center_limits['right'] = 0
			self.center_limits['left'] = 0

		self.foreground_scale = foreground_scale
		self.data.galaxy_window_state.foreground_scale = self.foreground_scale

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
		self.data.galaxy_objects.background_vertex_list.draw(pyglet.gl.GL_POINTS)

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

		# draw the foreground galaxy objects
		self.data.galaxy_objects.draw(self.foreground_scale)

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

	def on_mouse_motion(self, x, y, dx, dy):
		detected_objects = self.detect_mouseover_objects(x,y)
		if len(detected_objects) > 0:
			# maximally-seen object is first
			for object in sorted(detected_objects, key=detected_objects.get, reverse=True):
				if type(object) == galaxy_objects.ForegroundStar:
					print "star: %s"%object.name
				elif type(object) == galaxy_objects.WormHole:
					print "worm hole: %s to %s"%(object.endpoints[0].name, object.endpoints[1].name)

	def on_mouse_press(self, x, y, button, modifiers):
		detected_objects = self.detect_mouseover_objects(x,y,debug=True)

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
		# ensure resized window size falls within acceptable limits
		if width < self.min_dimension:
			self.width = self.min_dimension
			width = self.min_dimension
		if height < self.min_dimension:
			self.height = self.min_dimension
			height = self.min_dimension
		if width > self.max_dimension:
			self.width = self.max_dimension
			width = self.max_dimension
		if height > self.max_dimension:
			self.height = self.max_dimension
			height = self.max_dimension

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

		self.data.galaxy_window_state.width = width
		self.data.galaxy_window_state.height = height
	
	def animate(self, dt):
		'Do any/all animations.'
		self.data.galaxy_objects.animate(dt)

# doesn't make sense to call this standalone, so no __main__
