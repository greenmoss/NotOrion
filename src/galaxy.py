#! python -O
from __future__ import division
from pyglet.gl import *
import pyglet
import galaxy_objects
import utilities
import itertools
import math
import logging

class RangeException(Exception): pass
class MissingDataException(Exception): pass

class WindowState(object):
	"A collection of attributes necessary for saving and restoring window state"
	def __init__(self):
		self.width = None
		self.height = None
		self.absolute_center = None
		self.foreground_scale = None

class WindowContainer(object):
	"Non-pyglet game logic and additional attributes for the galaxy window."

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
	# are we hovering over one or more objects?
	over_objects = []
	# which objects are being highlighted?
	highlight_objects = []

	# range marker attributes
	showing_ranges = False
	initiated_range_state = False
	concentric_range_markers = None
	range_circles_vertex_lists = []
	range_origin_star = None
	range_origin_coordinate = None
	range_marker_color = (25,128,25)
	range_cursor_label_batch = pyglet.graphics.Batch()
	# not sure if adding our own local attribute is a good idea?
	range_cursor_label_batch.visible = False
	range_cursor_label = pyglet.text.Label(
		"",
		x=0,
		y=0,
		anchor_x='center',
		anchor_y='bottom',
		color=(range_marker_color[0], range_marker_color[1], range_marker_color[2], 255),
		font_size=10,
		batch=range_cursor_label_batch
	)
	# shaded box behind cursor label, to make it easier to read
	range_cursor_label_box = pyglet.graphics.vertex_list( 4,
		('v2f', ( 0, 0,   0, 0,   0, 0,   0, 0,)),
		('c4B/static', (
			0, 0, 0, 200,
			0, 0, 0, 200,
			0, 0, 0, 200,
			0, 0, 0, 200,
			)
		)
	)
	range_line_vertex_list = pyglet.graphics.vertex_list( 2,
		('v2f', ( 0, 0,  0, 0 ) ),
		('c3B/static', range_marker_color*2)
	)
	# while we were marking ranges, which end stars were marked?
	range_marked_end_stars = {}

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
		self.window = Window(data, container=self, width=width, height=height)

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

		self.derive_from_window_dimensions(self.window.width, self.window.height)
		if self.data.galaxy_window_state.foreground_scale:
			self.set_scale(self.data.galaxy_window_state.foreground_scale)
		else:
			self.set_scale(self.maximum_scale)

		if self.data.galaxy_window_state.absolute_center:
			self.set_center(self.data.galaxy_window_state.absolute_center)
		else:
			self.set_center((0, 0))

		pyglet.clock.schedule_interval(self.animate, 1/60.)

		self.window.set_visible()
	
	def animate(self, dt):
		'Do any/all animations.'
		self.data.galaxy_objects.animate(dt)

		# markers for items under mouse
		if not(self.over_objects == self.highlight_objects):
			# new set of animations
			self.highlight_objects = self.over_objects

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

	def capture_range_state(self):
		"capture initial state for context-sensitive range markings"
		self.range_origin_coordinate = self.window_to_absolute((self.window._mouse_x, self.window._mouse_y))

		# do we have an origin star?
		self.range_origin_star = None
		for object in self.over_objects:
			# should be hovering over a star
			if type(object) is not galaxy_objects.ForegroundStar:
				continue
			self.range_origin_star = object
			self.range_origin_coordinate = self.range_origin_star.coordinates
			break

		# completed initial state of range iteration
		self.initiated_range_state = True
	
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
		right_top = self.window_to_absolute((self.window.width, self.window.height))
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

		self.mini_map_corners = {
			'top':self.mini_map_offset+self.mini_map_height,
			'right':self.window.width-self.mini_map_offset,
			'bottom':self.mini_map_offset,
			'left':self.window.width-self.mini_map_offset-self.mini_map_width
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

		# after all mini map parameters are calculated, display the mini map
		self.mini_map_visible = True
	
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
		absolute_position = self.window_to_absolute((x,y))
		absolute_position = (int(absolute_position[0]/self.foreground_scale),int(absolute_position[1]/self.foreground_scale))

		length = (radius*2)+1
		area = length * length
		read_x = absolute_position[0]-radius+translate_x
		read_y = absolute_position[1]-radius+translate_y
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
			logging.debug( "pixel colors" )
			for row in range(length-1, -1, -1):
				begin = row*length
				end = begin + length
				logging.debug( colors[begin:end] )

			# maximally-seen object is first
			for object in sorted(detected_objects, key=detected_objects.get, reverse=True):
				if type(object) == galaxy_objects.ForegroundStar:
					logging.debug( "star: %s; x,y: %s"%(object.name, object.coordinates) )
				elif type(object) == galaxy_objects.WormHole:
					logging.debug( "worm hole: %s to %s"%(object.endpoints[0].name, object.endpoints[1].name) )

		glPopMatrix()

		return detected_objects

	def fix_mouse_in_window(self):
		"""_mouse_in_window is built in, so normally it wouldn't be a good idea to override it
		but since it reports "False" on startup even though the cursor is in the window, we'll
		cheat/fix/workaround"""
		self.window._mouse_in_window = True

	def reset_range_circles(self):
		"remove range circle vertices"
		self.concentric_range_markers = None
		# must manually delete old vertex lists, or we get (video?) memory leak
		for vertex_list in self.range_circles_vertex_lists:
			vertex_list.delete()
		self.range_circles_vertex_lists = []

	def reset_range_state(self):
		# reset all end star marker colors
		for end_star in self.range_marked_end_stars.keys():
			end_star.reset_marker()
			end_star.hide_marker()
		self.range_marked_ends_stars = {}

		# reset origin star marker color
		if self.range_origin_star:
			self.range_origin_star.reset_marker()
			self.range_origin_star.hide_marker()
			self.range_marked_end_stars[self.range_origin_star] = True
			self.range_origin_star = None

		# reveal marker again if we are over a re-marked star
		for object in self.over_objects:
			if self.range_marked_end_stars.has_key(object):
				object.reveal_marker()

		self.range_marked_end_stars = {}

		self.range_origin_coordinate = None

		self.reset_range_circles()

		self.range_cursor_label_batch.visible = False

		# set initial state for *next* range iteration
		self.initiated_range_state = False

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

	def set_over_objects(self, x, y):
		"Set objects that are under the cursor, and show/hide relevant markers"
		over_objects = []
		detected_objects = self.detect_mouseover_objects(x,y)
		if len(detected_objects) > 0:
			# maximally-seen object is first
			for object in sorted(detected_objects, key=detected_objects.get, reverse=True):
				if type(object) == galaxy_objects.ForegroundStar:
					over_objects.append(object)
				elif type(object) == galaxy_objects.WormHole:
					over_objects.append(object)
				else: # black hole
					detected_objects.pop(object)

		if not(over_objects == self.over_objects):
			for object in self.over_objects:
				if not detected_objects.has_key(object):
					object.hide_marker()
			for object in over_objects:
				object.reveal_marker()
			self.over_objects = over_objects
	
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

	def set_range_circles(self, x, y):
		"calculate vertices for successive range circle markers"

		# Set logarithmically-scaled concentric circles showing range in parsecs from given x, y
		if not self.concentric_range_markers:
			self.concentric_range_markers = []

			# how many parsecs from corner to corner?
			right_top = self.window_to_absolute((self.window.width, self.window.height))
			left_bottom = self.window_to_absolute((0, 0))
			height_parsecs = (right_top[1]-left_bottom[1])/100
			width_parsecs = (right_top[0]-left_bottom[0])/100
			parsecs = math.sqrt(height_parsecs**2 + width_parsecs**2)

			# length of each parsec in window coordinates?
			coords_per_parsec = parsecs/100*self.foreground_scale

			# range marker steps, in parsecs, of appropriate size for screen size and scale
			marker_steps = filter( 
				lambda length: 
					length <= parsecs, 
					[1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128, 160, 192, 256, 320, 384, 512]
			)

			logging.debug( "in set_range_circles, parsecs: %s, steps: %s"%(parsecs, marker_steps) )
			previous_radius = 0
			previous_difference = 0
			for step in marker_steps:
				absolute_radius = step*100
				length = absolute_radius / self.foreground_scale
				difference = length - previous_radius
				# exclude radii of circles that would be too close to the previous radius
				if difference < 30:
					continue
				# ensure difference to previous circle always increases or remains the same
				if difference < previous_difference:
					continue
				previous_radius = length
				previous_difference = difference
				logging.debug( "step: %s, absolute_radius: %s, length: %s"%(step, absolute_radius, length) )

				self.concentric_range_markers.append( utilities.circle_vertices(length) )

		self.range_circles_vertex_lists = []
		for circle_vertices in self.concentric_range_markers:
			positioned_circle_vertices = []
			for vertex in circle_vertices:
				positioned_circle_vertices.append( (vertex[0]+x, vertex[1]+y) )
			self.range_circles_vertex_lists.append( 
				pyglet.graphics.vertex_list( 
					len(circle_vertices),
					( 'v2f',        tuple(itertools.chain(*positioned_circle_vertices)) ),
					( 'c3B/static', self.range_marker_color*len(circle_vertices) )
				)
			)

	def set_range_info(self, showing_ranges = True, debug = False):
		self.showing_ranges = showing_ranges

		if showing_ranges is False:
			self.reset_range_state()
			return

		# do not attempt to set any range info unless our mouse cursor is within the window
		if self.window._mouse_in_window is False:
			return

		if self.initiated_range_state is False:
			self.capture_range_state()

		end_coordinate = self.window_to_absolute((self.window._mouse_x, self.window._mouse_y))
		end_star = None

		# snap to star
		for object in self.over_objects:
			# it should be a star
			if type(object) is not galaxy_objects.ForegroundStar:
				continue

			# it should not be the origin star
			if object is self.range_origin_star:
				continue

			end_star = object
			end_coordinate = object.coordinates
			break

		# determine distance from origin to end
		distance = math.sqrt(
			abs(self.range_origin_coordinate[0]-end_coordinate[0])**2 +
			abs(self.range_origin_coordinate[1]-end_coordinate[1])**2
		)
		screen_distance = distance/self.foreground_scale

		if debug:
			if self.range_origin_star:
				logging.debug( "from %s: %s"%(self.range_origin_star.name, self.range_origin_star.coordinates) )
			if end_star:
				logging.debug( "to %s: %s"%(end_star.name, end_star.coordinates) )
			logging.debug( "distance: %0.2f; screen_distance: %0.2f"%(distance, screen_distance) )
		
		if screen_distance > 10:
			label_parsecs_float = round(distance/100, 1)
			label_distance = label_parsecs_float if label_parsecs_float < 1 else int(label_parsecs_float)
			label_unit = 'parsec' if label_distance is 1 else 'parsecs'
			self.range_cursor_label.text = "%s %s"%(label_distance, label_unit)

			end_coordinates = (self.window._mouse_x, self.window._mouse_y)
			if end_star:
				end_star_window_coordinates = self.absolute_to_window(end_star.coordinates)
				label_x = end_star_window_coordinates[0]
				label_y = end_star_window_coordinates[1]+8
				end_coordinates = end_star_window_coordinates
				end_star.marker.color = self.range_marker_color
				self.range_marked_end_stars[end_star] = True
			else:
				label_x = self.window._mouse_x
				label_y = self.window._mouse_y+5
			self.range_cursor_label.x = label_x
			self.range_cursor_label.y = label_y

			label_box_top = label_y + self.range_cursor_label.content_height
			label_box_bottom = label_y
			label_box_right = label_x + (self.range_cursor_label.content_width/2)
			label_box_left = label_x - (self.range_cursor_label.content_width/2)
			self.range_cursor_label_box.vertices = [
				label_box_right, label_box_bottom,
				label_box_right, label_box_top,
				label_box_left, label_box_top,
				label_box_left, label_box_bottom
			]

			range_origin_window_coordinates = self.absolute_to_window(self.range_origin_coordinate)
			self.range_line_vertex_list.vertices = [
				range_origin_window_coordinates[0], range_origin_window_coordinates[1],
				end_coordinates[0], end_coordinates[1]
			]

			self.range_cursor_label_batch.visible = True
		else:
			self.range_cursor_label_batch.visible = False

		if self.range_origin_star:
			self.range_origin_star.marker.color = self.range_marker_color
			self.range_origin_star.reveal_marker()

			window_range_origin = self.absolute_to_window(self.range_origin_star.coordinates)
			self.set_range_circles(window_range_origin[0], window_range_origin[1])

class Window(pyglet.window.Window):
	'Pyglet methods for the galaxy window.'

	def __init__(self, data, container=None, width=1024, height=768):
		super(Window, self).__init__(
			resizable=True, caption='Galaxy', width=width, height=height, visible=False
		)
		
		self.data = data

		# non-pyglet window attributes
		if not isinstance(container, WindowContainer):
			raise MissingDataException, "parameter container must be an instance of WindowContainer"
		self.container = container

		# which keys are pressed currently?
		self.keys = pyglet.window.key.KeyStateHandler()
		self.push_handlers(self.keys)

	def on_draw(self):
		glClearColor(0.0, 0.0, 0.0, 0)
		self.clear()

		# origin is center of window
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(-self.container.half_width, self.container.half_width, -self.container.half_height, self.container.half_height)
		glMatrixMode(GL_MODELVIEW)

		# draw the background stars
		self.data.galaxy_objects.background_vertex_list.draw(pyglet.gl.GL_POINTS)

		# if we're showing the mini-map, black out background stars under mini-map
		if self.container.mini_map_visible:
			# origin is lower-left of window
			glMatrixMode(GL_PROJECTION)
			glLoadIdentity()
			gluOrtho2D(0, self.width, 0, self.height)
			glMatrixMode(GL_MODELVIEW)

			# black-filled rectangle behind mini-map
			self.container.mini_map_black_bg_vertex_list.draw(pyglet.gl.GL_QUADS)

			# change back to origin at center of window
			glMatrixMode(GL_PROJECTION)
			glLoadIdentity()
			gluOrtho2D(-self.container.half_width, self.container.half_width, -self.container.half_height, self.container.half_height)
			glMatrixMode(GL_MODELVIEW)

		# set the center of the viewing area
		gluLookAt(
			self.container.absolute_center[0], self.container.absolute_center[1], 0.0,
			self.container.absolute_center[0], self.container.absolute_center[1], -100.0,
			0.0, 1.0, 0.0)

		# draw the foreground galaxy objects
		self.data.galaxy_objects.draw(self.container.foreground_scale)

		# for HUD objects, set 2D view with origin at lower left
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, self.width, 0, self.height)
		glMatrixMode(GL_MODELVIEW)

		# reset identity stack
		glLoadIdentity()

		# if we're showing range circles, draw them
		if len(self.container.range_circles_vertex_lists) > 0:
			glPushAttrib(GL_ENABLE_BIT)
			glEnable(GL_LINE_STIPPLE)
			glLineStipple(1, 0x1111)
			for vertex_list in self.container.range_circles_vertex_lists:
				vertex_list.draw(pyglet.gl.GL_LINE_LOOP)
			glPopAttrib()

		# if we're showing cursor range line and label, draw them
		if self.container.range_cursor_label_batch.visible:

			glPushAttrib(GL_ENABLE_BIT)
			glEnable(GL_LINE_STIPPLE)
			glLineStipple(1, 0x1111)
			self.container.range_line_vertex_list.draw(pyglet.gl.GL_LINES)
			glPopAttrib()

			glPushAttrib(GL_ENABLE_BIT)
			glEnable(GL_BLEND)
			glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
			self.container.range_cursor_label_box.draw(pyglet.gl.GL_QUADS)
			glPopAttrib()

			self.container.range_cursor_label_batch.draw()

		# if we're showing the mini-map, draw it
		if self.container.mini_map_visible:
			# translucent gray rectangle behind mini-map
			glEnable(GL_BLEND)
			glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
			self.container.mini_map_transparent_bg_vertex_list.draw(pyglet.gl.GL_QUADS)

			# borders of mini-map
			self.container.mini_map_borders_vertex_list.draw(pyglet.gl.GL_LINE_LOOP)

			# borders of mini-window within mini-map
			self.container.mini_window_vertex_list.draw(pyglet.gl.GL_LINE_LOOP)

	def on_key_press(self, symbol, modifiers):
		key_handlers = {
			pyglet.window.key.ESCAPE: lambda: self.close(),
			pyglet.window.key.Q: lambda: self.close(),
		}
		handler = key_handlers.get(symbol, lambda: None)
		handler()

		# everything else, not handled by key_handlers
		if symbol == pyglet.window.key.LSHIFT:
			self.container.set_range_info()

	def on_key_release(self, symbol, modifiers):
		if symbol == pyglet.window.key.LSHIFT:
			self.container.set_range_info(False)
	
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.container.set_center((self.container.absolute_center[0] - dx, self.container.absolute_center[1] - dy))

	def on_mouse_motion(self, x, y, dx, dy):
		self.container.fix_mouse_in_window()

		self.container.set_over_objects(x,y)
		if self.container.showing_ranges is True:
			self.container.set_range_info()

	def on_mouse_press(self, x, y, button, modifiers):
		detected_objects = self.container.detect_mouseover_objects(x,y,debug=True)

	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		prescale_absolute_mouse = self.container.window_to_absolute((x,y))

		self.container.reset_range_state()

		self.container.set_scale(self.container.foreground_scale*(self.container.zoom_speed**scroll_y))

		# range markers must be recalculated
		self.container.concentric_range_markers = None

		postscale_absolute_mouse = self.container.window_to_absolute((x,y))

		# scale the prescale mouse according to the *new* foreground scale
		prescale_mouse = (prescale_absolute_mouse[0]/self.container.foreground_scale, prescale_absolute_mouse[1]/self.container.foreground_scale)
		postscale_mouse = (postscale_absolute_mouse[0]/self.container.foreground_scale, postscale_absolute_mouse[1]/self.container.foreground_scale)

		self.container.set_center(
			(
				prescale_mouse[0]-postscale_mouse[0]+self.container.absolute_center[0], 
				prescale_mouse[1]-postscale_mouse[1]+self.container.absolute_center[1]
			)
		)
	
	def on_resize(self, width, height):
		# ensure resized window size falls within acceptable limits
		if width < self.container.min_dimension:
			self.width = self.container.min_dimension
			width = self.container.min_dimension
		if height < self.container.min_dimension:
			self.height = self.container.min_dimension
			height = self.container.min_dimension
		if width > self.container.max_dimension:
			self.width = self.container.max_dimension
			width = self.container.max_dimension
		if height > self.container.max_dimension:
			self.height = self.container.max_dimension
			height = self.container.max_dimension

		# reset openGL attributes to match new window dimensions
		glViewport(0, 0, width, height)
		glMatrixMode(gl.GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, width, 0, height, -1, 1)
		glMatrixMode(gl.GL_MODELVIEW)

		self.container.derive_from_window_dimensions(width, height)

		# window resize changes min/max scale, so ensure we are still within scale bounds
		self.container.set_scale(self.container.foreground_scale)

		# ensure center is still in a valid position
		self.container.set_center((self.container.absolute_center[0], self.container.absolute_center[1]))

		# range markers must be recalculated
		self.container.concentric_range_markers = None

		self.container.data.galaxy_window_state.width = width
		self.container.data.galaxy_window_state.height = height

# doesn't make sense to call this standalone, so no __main__
