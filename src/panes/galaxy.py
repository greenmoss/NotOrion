#! /usr/bin/env python -O
from __future__ import division
import os
import random

import pyglet
from pyglet.gl import *

from globals import g
import panes
import utilities

class Galaxy(panes.Panes):

	def __init__(self, state):
		g.logging.debug('instantiating panes.Galaxy')

		self.state = state

		self.derive_from_window_dimensions()
		self.generate_background_vertex_list()
	
	def generate_background_vertex_list(self):
		"""Generate a reusable vertex/color list of all background stars.  It
		will be invoked as background_vertex_list.draw(pyglet.gl.GL_POINTS).  """

		background_star_vertices = []
		background_star_colors = []

		# randomly generate background stars
		for coordinate in utilities.random_dispersed_coordinates(amount=8000, dispersion=3):
			[background_star_vertices.append(component) for component in coordinate]

			color = []
			for index in range(0,3):
				color.append(64)
			# allow one or two of the bytes to be less, which allows slight coloration
			color[random.randint(0,2)] = random.randint(32,64)
			color[random.randint(0,2)] = random.randint(32,64)

			[background_star_colors.append(component) for component in color]

		self.background_vertex_list = pyglet.graphics.vertex_list(
			8000,
			('v2i/static', background_star_vertices),
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

	# all pyglet.window handlers
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
	
	def on_resize(self, width, height):
		# reset openGL attributes to match new window dimensions
		glViewport(0, 0, width, height)
		glMatrixMode(gl.GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, width, 0, height, -1, 1)
		glMatrixMode(gl.GL_MODELVIEW)

		self.derive_from_window_dimensions()

		"""
		# window resize changes min/max scale, so ensure we are still within scale bounds
		self.container.set_scale(self.container.foreground_scale)

		# ensure center is still in a valid position
		self.container.set_center((self.container.absolute_center[0], self.container.absolute_center[1]))

		# range markers must be recalculated
		self.container.concentric_range_markers = None

		self.container.data.galaxy_window_state.width = width
		self.container.data.galaxy_window_state.height = height
		"""
