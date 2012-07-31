import sys

import pyglet
from pyglet.gl import *

from globals import g
import views
import stars
import worm_holes

class Masks(views.View):
	"""Generate object image masks for color picking."""

	def __init__(self, state):
		self.state = state

		# store backreferences (eg color to object) here
		self.color_picks = {}
		self.detected_object_frequency = {}

		# red, green, blue byte values for masks
		self.current_color = (255,255,255)

		self.stars = stars.Stars(self.state.map.stars)
		self.set_colors(self.stars)

		self.worm_holes = worm_holes.WormHoles(self.state.map.worm_holes)
		self.set_colors(self.worm_holes)
	
	def set_colors(self, masks_object):

		# For color mouse picking, assign a unique color to each mask
		for mask in masks_object.masks:
			mask.set_color(self.current_color)
			self.color_picks[self.current_color] = mask
			self.get_next_mask_color()

	def get_next_mask_color(self):
		'Decrement through mask colors, always returning one less than was given'
		(red,green,blue) = self.current_color

		# decrement red, then greeen, then blue
		red -= 1
		if red < 0:
			red = 255
			green -= 1

		if green < 0:
			green = 255
			blue -= 1

		if blue < 0:
			# this gives us potentially millions of object colors
			# with that many objects, this game would have already encountered other issues
			# so it is very unlikely we will ever hit this condition
			raise RangeException, "ran out of available ID colors"

		self.current_color = (red,green,blue)
	
	def start_draw(self):
		glPushMatrix()
		g.window.clear()

		self.state.map.set_drawing_matrices()
		self.state.map.set_drawing_to_foreground()

		# draw the foreground object masks
		self.stars.handle_draw()
		self.worm_holes.handle_draw()

	def finish_draw(self):
		glLoadIdentity()
		glPopMatrix()
	
	def detect_mouseover_objects(self, x, y, radius=2):
		'Given a mouse x/y position, detect any objects at/around this position'
		self.start_draw()

		length = (radius*2)+1
		area = length * length
		pixel_data_length = 4 * area # 4, one for each byte: R, G, B, A
		ctypes_buffer=(GLubyte * pixel_data_length)()
		glReadBuffer(GL_BACK)
		glReadPixels(x,y,length,length,GL_RGBA,GL_UNSIGNED_BYTE,ctypes_buffer)

		# find object(s) under the cursor
		colors = []
		bytes = []
		self.detected_object_frequency = {}
		for byte_position in range(area):
			ctypes_position = byte_position*4

			alpha = ctypes_buffer[ctypes_position+3]
			if alpha < 255:
				colors.append( (0, 0, 0) )
				continue

			color = (
				ctypes_buffer[ctypes_position], #red
				ctypes_buffer[ctypes_position+1], #green
				ctypes_buffer[ctypes_position+2], #blue
			)
			detected_object = self.color_picks[color]
			if not self.detected_object_frequency.has_key(detected_object):
				self.detected_object_frequency[detected_object] = 0
			self.detected_object_frequency[detected_object] += 1
			colors.append( color )

		self.finish_draw()
	
	def detected_objects(self, type=None):
		"""Return map objects that were detected under the mouse, if any. Optionally, request only masks of a certain type."""
		map_objects = []
		# first objects were "the most" under the mouse
		for mask_object in sorted(
			self.detected_object_frequency, key=self.detected_object_frequency.get, reverse=True
		):
			if (type is not None) and not ((mask_object.type) == type):
				continue
			map_objects.append(mask_object.map_object)
		return map_objects

	def set_center(self):
		self.stars.set_center()
		self.worm_holes.set_center()

	def set_scale(self):
		self.stars.set_scale()
		self.worm_holes.set_scale()

	def handle_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.set_center()

	def handle_mouse_motion(self, x, y, dx, dy):
		self.detect_mouseover_objects(x, y)
	
	def handle_mouse_scroll(self, x, y, scroll_x, scroll_y):
		self.set_scale()
		self.set_center()
	
	def handle_resize(self, width, height):
		self.set_scale()
		self.set_center()
