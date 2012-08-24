import pyglet
from pyglet.gl import *

from globals import g
import stars
import worm_holes
import ranges

class Markers(object):
	"""Range markers and indicators visible within the galaxy main map."""

	def __init__(self, state):
		self.state = state
		self.objects_under_cursor = []
		self.stars = stars.Stars(self.state.map.stars)
		self.worm_holes = worm_holes.WormHoles(self.state.map.worm_holes, self.stars)
		self.ranges = ranges.Ranges(self.state, self.stars)
	
	def animate(self, dt):
		'Do any/all animations.'

		# markers for items under mouse
		if not(self.objects_under_cursor == self.highlight_objects):
			# new set of animations
			self.highlight_objects = self.objects_under_cursor

	def handle_draw(self):
		# drawing during color-picking and mask detection requires a drawing area reset
		self.state.map.set_drawing_matrices()
		self.state.map.set_drawing_to_foreground()

		self.stars.draw()
		self.ranges.draw()

	def handle_key_press(self, *args):
		self.ranges.handle_key_press(*args)

	def handle_key_release(self, *args):
		self.ranges.handle_key_release(*args)

	def handle_mouse_drag(self, *args):
		if self.state.vetoed_drag:
			return
		self.stars.handle_mouse_drag(*args)
		self.worm_holes.handle_mouse_drag(*args)
		self.ranges.handle_mouse_drag(*args)

	def handle_mouse_motion(self, *args):
		self.objects_under_cursor = self.state.masks.detected_objects('map')
		self.stars.set_over_objects(self.objects_under_cursor)
		self.worm_holes.set_over_objects(self.objects_under_cursor)

		self.ranges.handle_mouse_motion(*args)

	def handle_mouse_scroll(self, *args):
		self.stars.handle_mouse_scroll(*args)
		self.worm_holes.handle_mouse_scroll(*args)
		self.ranges.handle_mouse_scroll(*args)
	
	def handle_resize(self, *args):
		self.stars.handle_resize(*args)
		self.worm_holes.handle_resize(*args)
		self.ranges.handle_resize(*args)
