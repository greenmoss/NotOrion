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
		self.worm_holes = worm_holes.WormHoles()
	
	def animate(self, dt):
		'Do any/all animations.'

		# markers for items under mouse
		if not(self.objects_under_cursor == self.highlight_objects):
			# new set of animations
			self.highlight_objects = self.objects_under_cursor

	def fix_mouse_in_window(self):
		"""_mouse_in_window is built in, so normally it wouldn't be a good idea to override it
		but since it reports "False" on startup even though the cursor is in the window, we'll
		cheat/fix/workaround"""
		g.window._mouse_in_window = True

	def set_over_objects(self, x, y):
		"Set objects that are under the cursor, and show/hide relevant markers"
		objects_under_cursor = []
		return
		detected_objects = self.state.detect_map_mouseover_objects(x,y)
		if len(detected_objects) > 0:
			# maximally-seen object is first
			for object in sorted(detected_objects, key=detected_objects.get, reverse=True):
				if type(object) == galaxy_objects.ForegroundStar:
					objects_under_cursor.append(object)
				elif type(object) == galaxy_objects.WormHole:
					objects_under_cursor.append(object)
				else: # black hole
					detected_objects.pop(object)

		if not(objects_under_cursor == self.objects_under_cursor):
			for object in self.objects_under_cursor:
				if not detected_objects.has_key(object):
					object.hide_marker()
			for object in objects_under_cursor:
				object.reveal_marker()
			self.objects_under_cursor = objects_under_cursor

	def handle_draw(self):
		# the draw for color-picking and mask detection requires that we reset the drawing area
		self.state.map.set_drawing_matrices()
		#glLoadIdentity()
		#glMatrixMode(GL_MODELVIEW)
		self.state.map.set_drawing_to_foreground()

		self.stars.draw()

		glLoadIdentity()

	def handle_key_press(self, symbol, modifiers):
		if not symbol == pyglet.window.key.LSHIFT:
			return
			#self.set_info(True)

	def handle_key_release(self, symbol, modifiers):
		if not symbol == pyglet.window.key.LSHIFT:
			return
			#self.set_info(False)

	def handle_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.stars.set_coordinates()

	def handle_mouse_motion(self, x, y, dx, dy):
		#self.fix_mouse_in_window()

		self.objects_under_cursor = self.state.masks.detected_objects('map')
		self.stars.set_over_objects(self.objects_under_cursor)
		self.worm_holes.set_over_objects(self.objects_under_cursor)

	def handle_mouse_scroll(self, x, y, scroll_x, scroll_y):
		self.stars.set_coordinates()
		# range markers must be recalculated
		#self.concentric_markers = None
	
	def handle_resize(self, width, height):
		self.stars.set_coordinates()
		# range markers must be recalculated
		#self.concentric_markers = None
