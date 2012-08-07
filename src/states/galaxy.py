import logging
logger = logging.getLogger(__name__)

from globals import g
import states
import views.galaxy

class Galaxy(states.States):
	"""Interactions with the galaxy."""

	def __init__(self):
		logger.debug('instantiating state.Galaxy')

		self.map = views.galaxy.map.Galaxy(self)
		self.mini_map = views.galaxy.mini_map.MiniMap(self)

		self.masks = views.galaxy.masks.Masks(self)

		self.markers = views.galaxy.markers.Markers(self)

		g.window.push_handlers(self)

	def map_view_to_window(self, coordinates):
		"Translate map view coordinate into window coordinate, accounting for view center and scale."
		return self.map.view_to_window(coordinates)

	def window_to_map_view(self, coordinates):
		"Translate window coordinate into map view coordinate, accounting for view center and scale."
		return self.map.window_to_view(coordinates)

	def on_draw(self, *args):
		self.map.handle_draw(*args)
		self.markers.handle_draw(*args)
		self.mini_map.handle_draw(*args)

	def on_key_press(self, *args):
		self.markers.handle_key_press(*args)

	def on_key_release(self, *args):
		self.markers.handle_key_release(*args)

	def on_mouse_drag(self, *args):
		self.map.handle_mouse_drag(*args)
		self.mini_map.handle_mouse_drag(*args)
		self.masks.handle_mouse_drag(*args)
		self.markers.handle_mouse_drag(*args)

	def on_mouse_motion(self, *args):
		self.masks.handle_mouse_motion(*args)
		self.markers.handle_mouse_motion(*args)

	def on_mouse_scroll(self, *args):
		self.map.handle_mouse_scroll(*args)
		self.mini_map.handle_mouse_scroll(*args)
		self.masks.handle_mouse_scroll(*args)
		self.markers.handle_mouse_scroll(*args)

	def on_resize(self, *args):
		self.map.handle_resize(*args)
		self.mini_map.handle_resize(*args)
		self.masks.handle_resize(*args)
		self.markers.handle_resize(*args)
