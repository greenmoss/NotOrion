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

		self.star_system = views.galaxy.star_system.StarSystem(self)

		g.window.push_handlers(self)

	def load(self, attribs):
		"Load attributes that have been saved to disk."
		self.map.load(attribs['map'])

	def save(self):
		"Return attributes that should be saved to disk."
		attribs = {}
		attribs['map'] = self.map.save()
		return attribs
	
	def map_coordinate(self, coordinates, type):
		"""A coordinate within the map view.

		This is used to determine coordinate transformation calculations."""
		return self.map.coordinate(coordinates, type)

	def on_draw(self, *args):
		self.map.handle_draw(*args)
		self.markers.handle_draw(*args)
		self.mini_map.handle_draw(*args)
		self.star_system.handle_draw(*args)

	def on_key_press(self, *args):
		self.markers.handle_key_press(*args)

	def on_key_release(self, *args):
		self.markers.handle_key_release(*args)

	def on_mouse_drag(self, *args):
		self.map.handle_mouse_drag(*args)
		self.mini_map.handle_mouse_drag(*args)
		self.masks.handle_mouse_drag(*args)
		self.markers.handle_mouse_drag(*args)
		self.star_system.handle_mouse_drag(*args)

	def on_mouse_press(self, *args):
		self.star_system.handle_mouse_press(*args)

	def on_mouse_motion(self, *args):
		self.masks.handle_mouse_motion(*args)
		self.markers.handle_mouse_motion(*args)

	def on_mouse_scroll(self, *args):
		self.map.handle_mouse_scroll(*args)
		self.mini_map.handle_mouse_scroll(*args)
		self.masks.handle_mouse_scroll(*args)
		self.markers.handle_mouse_scroll(*args)
		self.star_system.handle_mouse_scroll(*args)

	def on_resize(self, *args):
		self.map.handle_resize(*args)
		self.mini_map.handle_resize(*args)
		self.masks.handle_resize(*args)
		self.markers.handle_resize(*args)
		self.star_system.handle_resize(*args)
