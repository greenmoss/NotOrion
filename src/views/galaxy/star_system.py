from __future__ import division
import logging
logger = logging.getLogger(__name__)

import pyglet
from pyglet.gl import *

from globals import g
import pane
import views.galaxy.map.stars

class StarSystem(pane.Pane):
	"""A small window showing a star system."""
	height = 325
	width = 300

	background_color = (0, 0, 0) # black
	border_color = (32, 32, 32) # dark grey
	minimum_border_offset = 10 # window should be no closer to edge than this
	
	def __init__(self, state):
		self.state = state
		self.star = None
		self.half_height = int(StarSystem.height/2)
		self.half_width = int(StarSystem.width/2)

		self.bg_vertex_list = pyglet.graphics.vertex_list( 
			4, 'v2f',
			('c3B/static', StarSystem.background_color*4)
		)
		self.border_vertex_list = pyglet.graphics.vertex_list( 
			4, 'v2f',
			('c3B/static', StarSystem.border_color*4)
		)

	def derive_dimensions(self):
		star_map_coordinate = self.state.map_coordinate(self.star.coordinates, 'model').as_default_window()

		offset_x = star_map_coordinate.x
		offset_y = star_map_coordinate.y

		top = offset_y + self.half_height
		right = offset_x + self.half_width
		bottom = offset_y - self.half_height
		left = offset_x - self.half_width

		max_top = g.window.height - StarSystem.minimum_border_offset
		max_right = g.window.width - StarSystem.minimum_border_offset
		min_bottom = StarSystem.minimum_border_offset
		min_left = StarSystem.minimum_border_offset

		if top > max_top:
			difference = top - max_top
			top = top - difference
			bottom = bottom - difference

		if right > max_right:
			difference = right - max_right
			right = right - difference
			left = left - difference

		if bottom < min_bottom:
			difference = min_bottom - bottom
			top = top + difference
			bottom = bottom + difference

		if left < min_left:
			difference = min_left - left
			right = right + difference
			left = left + difference

		self.bg_vertex_list.vertices = (
			right, top,
			right, bottom,
			left, bottom,
			left, top,
		)
		self.border_vertex_list.vertices = (
			right, top,
			right, bottom,
			left, bottom,
			left, top,
		)
	
	def hide(self):
		self.star = None
		self.visible = False
	
	def show(self, star):
		self.star = star
		self.derive_dimensions()
		self.visible = True
	
	def handle_draw(self):
		if not self.visible:
			return

		self.drawing_origin_to_lower_left()
		self.bg_vertex_list.draw(pyglet.gl.GL_QUADS)
		self.border_vertex_list.draw(pyglet.gl.GL_LINE_LOOP)
	
	def handle_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.hide()
	
	def handle_mouse_press(self, x, y, button, modifiers):
		if not pyglet.window.mouse.LEFT:
			return

		objects_under_cursor = self.state.masks.detected_objects('map')
		if len(objects_under_cursor) == 0:
			self.hide()
			return

		map_star = None
		for map_object in objects_under_cursor:
			if type(map_object) is not views.galaxy.map.stars.Star:
				continue
			map_star = map_object
		if map_star is None:
			self.hide()
			return

		self.show(map_star.physical_star)

	def handle_mouse_scroll(self, x, y, scroll_x, scroll_y):
		self.hide()

	def handle_resize(self, width, height):
		self.hide()
