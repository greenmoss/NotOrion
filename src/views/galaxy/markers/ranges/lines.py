import logging
logger = logging.getLogger(__name__)
import math

import pyglet
from pyglet.gl import *

from globals import g
import views.galaxy.markers.ranges

class Line(object):
	def __init__(self, ranges):
		self.ranges = ranges
		self.color = views.galaxy.markers.ranges.Ranges.color

		self.vertex_list = pyglet.graphics.vertex_list( 2,
			('v2f', ( 0, 0,  0, 0 ) ),
			('c3B/static', self.color*2)
		)

		self.from_star = EndPointStar()
		self.to_star = EndPointStar()
	
	def detect_star(self):
		if len(self.ranges.marker_stars.under_cursor) > 1:
			raise Exception, "not sure how to handle more than one origin marker star"

		if len(self.ranges.marker_stars.under_cursor) == 0:
			return None

		# should only be 1 now, right?
		detected_ref = self.ranges.marker_stars.under_cursor.keys()[0]
		return self.ranges.marker_stars.markers[detected_ref]

	def draw(self):
		# stippled
		glPushAttrib(GL_ENABLE_BIT)
		glEnable(GL_LINE_STIPPLE)
		glLineStipple(1, 0x1111)
		self.vertex_list.draw(pyglet.gl.GL_LINES)
		glPopAttrib()
		# star marker, if any, is drawn elsewhere
		
	def hide(self):
		self.from_star.hide()
		self.to_star.hide()
	
	def move_target(self, target_coordinates):
		if self.ranges.origin_coordinates is None:
			return

		snap_coordinates = self.snap_to_target_star(target_coordinates)
		if snap_coordinates:
			target_coordinates = snap_coordinates

		self.vertex_list.vertices = [
			self.ranges.origin_coordinates[0],
			self.ranges.origin_coordinates[1],
			target_coordinates[0],
			target_coordinates[1]
		]

		return target_coordinates
	
	def snap_to_target_star(self, target_coordinates):
		target_star = self.detect_star()

		if target_star is None:
			self.to_star.hide()
			return

		if self.from_star.active and (self.from_star.marker_star == target_star):
			return

		self.to_star.show(target_star)
		snap_coordinates = (
			self.to_star.marker_star.sprite.x,
			self.to_star.marker_star.sprite.y
		)
		return snap_coordinates
	
	def show(self, origin_coordinates):
		origin_star = self.detect_star()
		snap_coordinates = origin_coordinates

		if origin_star is not None:
			self.from_star.show(origin_star)
			# snap origin to sprite
			snap_coordinates = (origin_star.sprite.x,origin_star.sprite.y)

		self.vertex_list.vertices = snap_coordinates*2
		return snap_coordinates

class EndPointStar(object):
	def __init__(self):
		self.star_marker_color_priority = 3
		self.marker_star = None
		self.active = False
		self.color = views.galaxy.markers.ranges.Ranges.color
		
	def hide(self):
		if self.marker_star is None:
			return
		self.marker_star.hide(self)
		self.marker_star = None
		self.active = False
	
	def show(self, marker_star):
		self.marker_star = marker_star
		self.marker_star.show(self)
		self.active = True
