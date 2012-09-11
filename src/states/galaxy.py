import logging
logger = logging.getLogger(__name__)

from globals import g
import states
import views.galaxy
import views.galaxy.panes

class Galaxy(states.States):
	"""Interactions with the galaxy."""

	def __init__(self):
		logger.debug('instantiating state.Galaxy')

		self.map = views.galaxy.map.Galaxy(self)
		self.mini_map = views.galaxy.panes.mini_map.MiniMap(self)
		self.star_system = views.galaxy.panes.star_system.StarSystem(self)

		self.masks = views.galaxy.masks.Masks(self)

		self.markers = views.galaxy.markers.Markers(self)

		g.window.push_handlers(self)

	def load(self, attribs):
		"Load attributes that have been saved to disk."
		self.map.load(attribs['map'])
		self.star_system.load(attribs['star_system'])

	def save(self):
		"Return attributes that should be saved to disk."
		attribs = {}
		attribs['map'] = self.map.save()
		attribs['star_system'] = self.star_system.save()
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
		# to test/show pick masks instead, uncomment the following two lines:
		#self.masks.start_draw()
		#self.masks.finish_draw()

	def on_key_press(self, *args):
		self.markers.handle_key_press(*args)

	def on_key_release(self, *args):
		self.markers.handle_key_release(*args)

	def on_mouse_drag(self, *args):
		# allow any object to cancel the drag
		self.vetoed_drag = None

		self.star_system.handle_mouse_drag(*args)
		self.map.handle_mouse_drag(*args)
		self.mini_map.handle_mouse_drag(*args)
		self.masks.handle_mouse_drag(*args)
		self.markers.handle_mouse_drag(*args)

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
