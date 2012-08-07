import logging
logger = logging.getLogger(__name__)

import pyglet
from pyglet.gl import *

from globals import g
import circles
import labels
import lines

class Ranges(object):
	color = (25,128,25)

	def __init__(self, state, marker_stars):
		self.state = state
		self.marker_stars = marker_stars
		self.origin_coordinates = None
		self.target_coordinates = None
		self.line = lines.Line(self)
	
	def draw(self):
		if self.origin_coordinates is None:
			return
		self.line.draw()

	def hide(self):
		self.origin_coordinates = None
		self.line.hide()

	def window_to_map_view(self, coordinates):
		foreground_coordinates = self.state.window_to_map_view(
			(coordinates[0], coordinates[1])
		)
		return (foreground_coordinates[0]/self.state.map.scale, foreground_coordinates[1]/self.state.map.scale)
	
	def handle_key_press(self, symbol, modifiers):
		if not symbol == pyglet.window.key.LSHIFT:
			return
		self.line.show(self.window_to_map_view((g.window._mouse_x, g.window._mouse_y)))

	def handle_key_release(self, symbol, modifiers):
		if not symbol == pyglet.window.key.LSHIFT:
			return
		self.hide()

	def handle_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.hide()

	def handle_mouse_motion(self, x, y, dx, dy):
		self.line.move_target(self.window_to_map_view((x, y)))
	
	def handle_mouse_scroll(self, x, y, scroll_x, scroll_y):
		self.hide()
	
	def handle_resize(self, width, height):
		self.hide()
