from __future__ import division
import math

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

		self.line = lines.Line(self)
		self.label = labels.Label(self)

		self.origin_coordinates = None
		self.target_coordinates = None
	
	def draw(self):
		if self.origin_coordinates is None:
			return
		self.line.draw()
		self.label.draw()

	def hide(self):
		self.origin_coordinates = None
		self.target_coordinates = None
		self.label.hide()
		self.line.hide()
	
	def model_distance(self):
		if (self.origin_coordinates is None) or (self.target_coordinates is None):
			return
		origin = self.state.map_coordinate(self.origin_coordinates, 'foreground')
		origin_model = origin.as_model()
		target = self.state.map_coordinate(self.target_coordinates, 'foreground')
		target_model = target.as_model()
		return math.sqrt(
			abs(origin_model.x - target_model.x)**2 +
			abs(origin_model.y - target_model.y)**2
		)
	
	def window_distance(self):
		if (self.origin_coordinates is None) or (self.target_coordinates is None):
			return
		origin = self.state.map_coordinate(self.origin_coordinates, 'foreground')
		origin_window = origin.as_default_window()
		target = self.state.map_coordinate(self.target_coordinates, 'foreground')
		target_window = target.as_default_window()
		return math.sqrt(
			abs(origin_window.x - target_window.x)**2 +
			abs(origin_window.y - target_window.y)**2
		)
	
	def handle_key_press(self, symbol, modifiers):
		if not symbol == pyglet.window.key.LSHIFT:
			return
		coordinate = self.state.map_coordinate((g.window._mouse_x, g.window._mouse_y), 'default_window')
		self.origin_coordinates = coordinate.as_foreground().as_tuple()

		snap_coordinates = self.line.show(self.origin_coordinates)
		if snap_coordinates:
			self.origin_coordinates = snap_coordinates

	def handle_key_release(self, symbol, modifiers):
		if not symbol == pyglet.window.key.LSHIFT:
			return
		self.hide()

	def handle_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.hide()

	def handle_mouse_motion(self, x, y, dx, dy):
		coordinate = self.state.map_coordinate((x, y), 'default_window')
		self.target_coordinates = coordinate.as_foreground().as_tuple()

		snap_coordinates = self.line.move_target(self.target_coordinates)
		if snap_coordinates:
			self.target_coordinates = snap_coordinates

		self.label.move(self.target_coordinates[0],self.target_coordinates[1])
	
	def handle_mouse_scroll(self, x, y, scroll_x, scroll_y):
		self.hide()
	
	def handle_resize(self, width, height):
		self.hide()
