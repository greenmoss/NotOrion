from __future__ import division
import math
import logging
logger = logging.getLogger(__name__)
import itertools

import pyglet
from pyglet.gl import *

from globals import g
import utilities
import views.galaxy.markers.ranges

class Circles(object):
	def __init__(self, ranges):
		self.ranges = ranges
		#self.concentric_markers = None
		self.circles = []
	
	def draw(self):
		glPushAttrib(GL_ENABLE_BIT)
		glEnable(GL_LINE_STIPPLE)
		glLineStipple(1, 0x1111)
		for circle in self.circles:
			circle.vertex_list.draw(pyglet.gl.GL_LINE_LOOP)
		glPopAttrib()

	def hide(self):
		# must manually delete old vertex lists, or we get (video?) memory leak
		for circle in self.circles:
			circle.vertex_list.delete()
		self.circles = []

	def generate(self, x, y):
		"""Set logarithmically-scaled concentric circles
		
		showing range in parsecs from given x, y"""

		# always reset in case we have old range circle markers
		# otherwise we will get a memory leak
		self.hide()

		# how many parsecs from corner to corner?
		right_top = self.ranges.state.map_coordinate((g.window.width, g.window.height), 'default_window')
		left_bottom = self.ranges.state.map_coordinate((0, 0), 'default_window')

		height_parsecs = (right_top.as_model().y-left_bottom.as_model().y)/100
		width_parsecs = (right_top.as_model().x-left_bottom.as_model().x)/100
		parsecs_to_corner = math.sqrt(height_parsecs**2 + width_parsecs**2)
		
		# length of each parsec in window coordinates?
		one_parsec_begin = self.ranges.state.map_coordinate((0, 0), 'model').as_default_window().x
		one_parsec_end = self.ranges.state.map_coordinate((100, 0), 'model').as_default_window().x
		window_length_one_parsec = one_parsec_end - one_parsec_begin

		# range marker steps, in parsecs, of appropriate size for screen size and scale
		marker_steps = filter( 
			lambda length: 
				length <= parsecs_to_corner, 
				[1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128, 160, 192, 256, 320, 384, 512]
		)

		previous_radius = 0
		previous_difference = 0
		for step in marker_steps:
			length = window_length_one_parsec * step
			difference = length - previous_radius
			# exclude radii of circles that would be too close to the previous radius
			if difference < 30:
				continue
			# ensure difference to previous circle always increases or remains the same
			if difference < previous_difference:
				continue
			previous_radius = length
			previous_difference = difference

			self.circles.append( Circle(length, x, y) )

class Circle(object):
	def __init__(self, radius, x, y):
		vertices = utilities.circle_vertices(radius)
		positioned_vertices = []
		for vertex in vertices:
			positioned_vertices.append((vertex[0] + x, vertex[1] + y))
		self.vertex_list = pyglet.graphics.vertex_list( 
			len(vertices),
			( 'v2f',        tuple(itertools.chain(*positioned_vertices)) ),
			( 'c3B/static', views.galaxy.markers.ranges.Ranges.color*len(vertices) )
		)
