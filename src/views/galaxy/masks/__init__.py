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
		self.state.map.start_draw()

		self.state.map.drawing_to_center_of_viewing_area()

		# draw the foreground object masks
		self.stars.handle_draw()
		self.worm_holes.handle_draw()

	def finish_draw(self):
		self.state.map.finish_draw()
		glPopMatrix()
	
	def detect_mouseover_objects(self, x, y, radius=2, debug=True):
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
		detected_objects = {}
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
			if not detected_objects.has_key(detected_object):
				detected_objects[detected_object] = 0
			detected_objects[detected_object] += 1
			colors.append( color )

		if debug:
			for row in range(length-1, -1, -1):
				begin = row*length
				end = begin + length

			# maximally-seen object is first
			for object in sorted(detected_objects, key=detected_objects.get, reverse=True):
				g.logging.debug( "object type: %s; ref: %s", type(object), object )

		self.finish_draw()

		return detected_objects

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
