from __future__ import division
import math
import sys
import logging
logger = logging.getLogger(__name__)

import pyglet
from pyglet.gl import *

from globals import g
import views
import stars
import worm_holes
import panes

class Masks(views.View):
	"""Generate object image masks for color picking."""

	def __init__(self, state):
		self.state = state

		# store backreferences (eg color to object) here
		self.color_picks = {}
		self.detected_object_frequency = {}

		self.current_color_id = 0

		self.stars = stars.Stars(self.state.map.stars)
		self.worm_holes = worm_holes.WormHoles(self.state.map.worm_holes)
		self.panes = panes.Panes(self)

		self.set_colors()
	
	def set_colors(self):
		"""For color mouse picking, assign a unique color to each mask"""
		
		for mask_object in [self.stars, self.worm_holes, self.panes]:

			for mask in mask_object.masks:
				mask_color = self.get_next_mask_color()
				mask.set_color(mask_color)
				self.color_picks[mask_color] = mask

	def get_next_mask_color(self):
		'''Returns a color derived from self.current_color_id.
		
		The complex derivation method ensures colors are easily distinguishable 
		when viewing by a human.'''
		# not sure what S, I, H, and Z are supposed to signify
		S = 1. / (1 + int((self.current_color_id+1) / 40.))
		I = 0.5
	
		H = self.current_color_id * 39
		H += 180
		H = H % 360

		Z = 1 + int(H/120)
		if (H >= 120) and (H < 240): 
			H -= 120
		elif H >= 240: 
			H -= 240
	
		angle = float( (H * 9. / 6.) - 90.)
		color1 = int(S * (0.5+I) * 255)
		color2 = int(S * math.cos(angle * -0.01745) * 255)
		color3 = int(S * (0.5-I) * 255)
	
		if H > 60:
			temp = color1
			color1 = color2
			color2 = temp
	
		color = (0,0,0)
		if Z == 1: 
			color = (color1,color2,color3)
		elif Z == 2: 
			color = (color3,color1,color2)
		elif Z == 3: 
			color = (color2,color3,color1)

		self.current_color_id += 1
		return color
	
	def start_draw(self):
		glPushMatrix()
		g.window.clear()

		self.state.map.set_drawing_matrices()
		self.state.map.set_drawing_to_foreground()

		# draw the foreground object masks
		self.stars.handle_draw()
		self.worm_holes.handle_draw()
		self.panes.handle_draw()

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
		"""Return objects that were detected under the mouse, if any. 
		
		Optionally, request only masks of a certain type."""

		objects = []

		# first objects were "the most" under the mouse
		for mask_object in sorted(
			self.detected_object_frequency, key=self.detected_object_frequency.get, reverse=True
		):
			if (type is not None) and not ((mask_object.type) == type):
				continue
			objects.append(mask_object.source_object)

		return objects

	def set_center(self):
		self.stars.set_center()
		self.worm_holes.set_center()

	def set_scale(self):
		self.stars.set_scale()
		self.worm_holes.set_scale()

	def handle_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		if self.state.vetoed_drag:
			return
		self.set_center()

	def handle_mouse_motion(self, x, y, dx, dy):
		self.detect_mouseover_objects(x, y)
	
	def handle_mouse_scroll(self, x, y, scroll_x, scroll_y):
		self.set_scale()
		self.set_center()
	
	def handle_resize(self, width, height):
		self.set_scale()
		self.set_center()
