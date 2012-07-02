import random

import pyglet
from pyglet.gl import *

import utilities
from globals import g

class BackgroundStars(object):

	def __init__(self):
		self.generate_background_vertex_list()
		#g.window.push_handlers(self)

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

	def draw(self):
		# draw the background stars
		self.background_vertex_list.draw(pyglet.gl.GL_POINTS)
