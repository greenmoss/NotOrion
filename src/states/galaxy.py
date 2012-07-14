#! /usr/bin/env python -O
from __future__ import division

from globals import g
import states
import views.galaxy.map
import views.galaxy.mini_map

class Galaxy(states.States):
	"""Interactions with the galaxy."""

	def __init__(self):
		g.logging.debug('instantiating state.Galaxy')
		self.map = views.galaxy.map.Galaxy(self)
		self.mini_map = views.galaxy.mini_map.MiniMap(self)

		g.window.push_handlers(self)

	def map_view_to_window(self, coordinates):
		"Translate map view coordinate into window coordinate, accounting for view center and scale."
		return self.map.view_to_window(coordinates)

	def window_to_map_view(self, coordinates):
		"Translate window coordinate into map view coordinate, accounting for view center and scale."
		return self.map.window_to_view(coordinates)

	def on_draw(self):
		self.map.handle_draw()
		self.mini_map.handle_draw()

	def on_mouse_drag(self, *args):
		self.map.handle_mouse_drag(*args)
		self.mini_map.handle_mouse_drag(*args)

	def on_mouse_scroll(self, *args):
		self.map.handle_mouse_scroll(*args)
		self.mini_map.handle_mouse_scroll(*args)

	def on_resize(self, *args):
		self.map.handle_resize(*args)
		self.mini_map.handle_resize(*args)
