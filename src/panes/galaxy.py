#! /usr/bin/env python -O
from __future__ import division
import os

import pyglet
from pyglet.gl import *

from globals import g
import panes

class Galaxy(panes.Panes):

	def __init__(self, state):
		g.logging.debug('instantiating panes.Galaxy')

		self.state = state

		super(Galaxy, self).__init__()

		self.derive_from_window_dimensions()
		self.generate_background_vertex_list()

	def on_draw(self):
		glClearColor(0.0, 0.0, 0.0, 0)
		g.window.clear()

		# origin is center of window
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(-self.half_width, self.half_width, -self.half_height, self.half_height)
		glMatrixMode(GL_MODELVIEW)

		# draw the background stars
		self.background_vertex_list.draw(pyglet.gl.GL_POINTS)
	
	def generate_background_vertex_list(self):
		"""Generate a reusable vertex/color list of all background stars.  It
		will be invoked as background_vertex_list.draw(pyglet.gl.GL_POINTS).  """
		background_star_vertices = []
		background_star_colors = []
		for background_star in g.galaxy.background_stars:
			[background_star_vertices.append(vertex) for vertex in background_star.coordinates]
			[background_star_colors.append(vertex) for vertex in background_star.color]
		self.background_vertex_list = pyglet.graphics.vertex_list(
			len(g.galaxy.background_stars),
			('v3i/static', background_star_vertices),
			('c3B/static', background_star_colors)
		)
	
	def derive_from_window_dimensions(self):
		"Set attributes that are based on window dimensions."
		self.half_width = g.window.width/2
		self.half_height = g.window.height/2

		# Derive minimum and maximum scale, based on minimum and maximum distances between foreground galaxy objects.
		self.minimum_dimension = (g.window.width < g.window.height) and g.window.width or g.window.height
		return
			
		self.minimum_scale = self.data.galaxy_objects.min_distance/self.minimum_dimension*5.0
		self.maximum_scale = self.data.galaxy_objects.max_distance/self.minimum_dimension
		# restrict zooming out to the minimum distance between foreground sprites
		if(self.data.galaxy_objects.min_distance/self.maximum_scale < self.minimum_foreground_separation):
			self.maximum_scale = self.data.galaxy_objects.min_distance/self.minimum_foreground_separation
		if self.minimum_scale > self.maximum_scale:
			self.maximum_scale = self.minimum_scale
