from __future__ import division

import pyglet
from pyglet.gl import *

from globals import g

class MiniMap(object):
	# offset from right/bottom of window
	offset = 20
	# either width or height, whichever is larger
	size = 75

	def __init__(self, state):
		self.state = state
		map_height = g.galaxy.top_bounding_y - g.galaxy.bottom_bounding_y
		map_width = g.galaxy.right_bounding_x - g.galaxy.left_bounding_x
		ratio = map_height/map_width
		if map_width > map_height:
			self.width = MiniMap.size
			self.height = self.width*ratio
		else: #map_width <= map_height
			self.height = MiniMap.size
			self.width = self.height/ratio

		# ratio of galaxy coordinates to mini-map coordinates
		self.ratio = self.width/map_width

		# what we will be drawing
		self.bg_vertex_list = pyglet.graphics.vertex_list( 
			4, 'v2f',
			('c4B/static', ( # transparent black
				0, 0, 0, 220,
				0, 0, 0, 220,
				0, 0, 0, 220,
				0, 0, 0, 220,
				)
			)
		)
		self.borders_vertex_list = pyglet.graphics.vertex_list( 
			4, 'v2f',
			('c3B/static', ( # dark grey
				32, 32, 32,
				32, 32, 32,
				32, 32, 32,
				32, 32, 32,
				)
			)
		)
		self.active_area_vertex_list = pyglet.graphics.vertex_list( 
			4, 'v2f',
			('c3B/static', ( # light grey
				48, 48, 48,
				48, 48, 48,
				48, 48, 48,
				48, 48, 48,
				)
			)
		)

		self.derive_dimensions()

	# dimensions of mini map vary with scale and window size
	def derive_dimensions(self):
		# where are the map view coordinates on the playing field?
		main_map_view_right_top = self.state.window_to_map_view((g.window.width, g.window.height))
		main_map_view_left_bottom = self.state.window_to_map_view((0, 0))

		# hide the mini-map if the entire playing field is visible
		# the integer modifiers create a minimum margin around stars before showing the mini-map
		if (
			(main_map_view_right_top[0] >= g.galaxy.right_bounding_x+60) and
			(main_map_view_right_top[1] >= g.galaxy.top_bounding_y+20) and
			(main_map_view_left_bottom[0] <= g.galaxy.left_bounding_x-60) and
			(main_map_view_left_bottom[1] <= g.galaxy.bottom_bounding_y-40)
		):
			self.visible = False
			return

		self.corners = {
			'top':MiniMap.offset + self.height,
			'right':-MiniMap.offset + g.window.width,
			'bottom':MiniMap.offset,
			'left':-MiniMap.offset + g.window.width - self.width
		}

		center = (
			self.corners['right']-(self.corners['right']-self.corners['left'])/2.0,
			self.corners['top']-(self.corners['top']-self.corners['bottom'])/2.0,
		)

		# position of viewing area within playing field
		self.window_corners = {
			'top':center[1]+int(main_map_view_right_top[1]*self.ratio),
			'right':center[0]+int(main_map_view_right_top[0]*self.ratio),
			'bottom':center[1]+int(main_map_view_left_bottom[1]*self.ratio),
			'left':center[0]+int(main_map_view_left_bottom[0]*self.ratio),
		}

		# ensure window_corners do not fall outside corners
		if not(self.corners['bottom'] < self.window_corners['top'] < self.corners['top']):
			self.window_corners['top'] = self.corners['top']
		if not(self.corners['left'] < self.window_corners['right'] < self.corners['right']):
			self.window_corners['right'] = self.corners['right']
		if not(self.corners['top'] > self.window_corners['bottom'] > self.corners['bottom']):
			self.window_corners['bottom'] = self.corners['bottom']
		if not(self.corners['right'] > self.window_corners['left'] > self.corners['left']):
			self.window_corners['left'] = self.corners['left']

		# update all drawing vertices
		self.active_area_vertex_list.vertices = (
			self.window_corners['right'], self.window_corners['top'],
			self.window_corners['right'], self.window_corners['bottom'],
			self.window_corners['left'], self.window_corners['bottom'],
			self.window_corners['left'], self.window_corners['top'],
		)
		self.bg_vertex_list.vertices = (
			self.corners['right'], self.corners['top'],
			self.corners['right'], self.corners['bottom'],
			self.corners['left'], self.corners['bottom'],
			self.corners['left'], self.corners['top'],
		)
		self.borders_vertex_list.vertices = (
			self.corners['right'], self.corners['top'],
			self.corners['right'], self.corners['bottom'],
			self.corners['left'], self.corners['bottom'],
			self.corners['left'], self.corners['top'],
		)

		# after all mini map parameters are calculated, display the mini map
		self.visible = True

	def drawing_origin_to_lower_left(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0, g.window.width, 0, g.window.height)

		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
	
	def handle_draw(self):
		if not self.visible:
			return

		glPushMatrix()

		self.drawing_origin_to_lower_left()

		# translucent gray rectangle behind mini-map
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		self.bg_vertex_list.draw(pyglet.gl.GL_QUADS)

		# borders of mini-map
		self.borders_vertex_list.draw(pyglet.gl.GL_LINE_LOOP)

		# borders of mini-window within mini-map
		self.active_area_vertex_list.draw(pyglet.gl.GL_LINE_LOOP)

		glPopMatrix()
	
	def handle_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.derive_dimensions()

	def handle_mouse_scroll(self, x, y, scroll_x, scroll_y):
		self.derive_dimensions()

	def handle_resize(self, width, height):
		self.derive_dimensions()

