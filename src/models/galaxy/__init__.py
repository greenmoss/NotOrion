#! python -O
"""Known/visible space."""
from __future__ import division
import math
import random
import os

from globals import g
import utilities

import black_holes
import masses
import nebulae
import stars
import worm_holes

class Galaxy(object):

	# black holes and stars must be at least this many parsecs apart
	min_separation_parsecs = 10
	
	def __init__(self):
		g.logging.debug("instantiated Galaxy")

	def generate(self, edges, dispersion, object_amount, object_pool, worm_hole_amount, nebulae_amount):
		'Generate objects in the galaxy'
		g.logging.debug("generating galaxy")

		self.generate_stars_and_black_holes(edges, dispersion, object_amount, object_pool)
		g.logging.debug("star count: %s", len(self.stars))
		g.logging.debug("black hole count: %s", len(self.black_holes))

		# generate nebulae
		self.nebulae = nebulae.generate(nebulae_amount, edges)
		g.logging.debug("nebulae count: %s", len(self.nebulae))

		# generate worm holes
		self.worm_holes = worm_holes.generate(worm_hole_amount, self.stars)
		g.logging.debug("worm hole count: %s", len(self.worm_holes))

		self.derive_bounding_lines()
		self.normalize()
		self.derive_min_max_distances()

	def generate_stars_and_black_holes(self, edges, dispersion, object_amount, object_pool):
		# generate coordinates for stars AND black holes in one pass
		# since they may not overlap
		object_coordinates = utilities.random_dispersed_coordinates(
			edges[0], edges[1], edges[2], edges[3],
			amount=object_amount, dispersion=dispersion
		)

		self.stars = []
		self.black_holes = []

		# mash all the objects together for randomization purposes
		object_types = []
		for name, freq in object_pool.iteritems():
			object_types += [name]*freq

		for coordinate in object_coordinates:
			object_type = object_types[random.randint(0, len(object_types)-1)]

			if object_type == 'black hole':
				self.black_holes.append(
					black_holes.BlackHole(coordinate)
				)

			else:
				self.stars.append(
					stars.Star(
						coordinate, 
						stars.Star.available_names.pop(
							random.randint(0, len(stars.Star.available_names)-1)
						), 
						object_type
					),
				)

	def derive_min_max_distances(self):
		# derive max/min distances between all stars/black holes
		self.max_coords = (0, 0)
		self.max_distance = 0
		self.min_coords = ((self.right_bounding_x - self.left_bounding_x), (self.top_bounding_y - self.bottom_bounding_y))
		self.min_distance = math.sqrt(self.min_coords[0]**2 + self.min_coords[1]**2)
		for object1 in self.stars+self.black_holes:
			for object2 in self.stars+self.black_holes:
				if object1 == object2:
					continue
				max_x = object1.coordinates[0]
				min_x = object2.coordinates[0]
				if object2.coordinates[0] > object1.coordinates[0]:
					max_x = object2.coordinates[0]
					min_x = object1.coordinates[0]
				max_y = object1.coordinates[1]
				min_y = object2.coordinates[1]
				if object2.coordinates[1] > object1.coordinates[1]:
					max_y = object2.coordinates[1]
					min_y = object1.coordinates[1]
				coords = ((max_x - min_x), (max_y - min_y))
				distance = math.sqrt(coords[0]**2 + coords[1]**2)
				if distance < self.min_distance:
					self.min_coords = coords
					self.min_distance = distance
				if distance > self.max_distance:
					self.max_coords = coords
					self.max_distance = distance
		if self.min_distance < Galaxy.min_separation_parsecs:
			raise DataError, "at least two stars and/or black holes are not far enough apart"

	def normalize(self):
		'Force extreme stars/black holes to be equidistant from (0,0)'
		x_offset = (abs(self.right_bounding_x)-abs(self.left_bounding_x))/2
		y_offset = (abs(self.top_bounding_y)-abs(self.bottom_bounding_y))/2

		# recalculate all object coordinates
		for mass in self.stars + self.black_holes + self.nebulae:
			mass.coordinates = (mass.coordinates[0]-x_offset, mass.coordinates[1]-y_offset)

		# previously-calculated bounding lines are now incorrect, so recalculate
		self.derive_bounding_lines()

	def derive_bounding_lines(self):
		'Find bounding lines that contain all stars and black holes.'
		self.left_bounding_x, self.right_bounding_x, self.top_bounding_y, self.bottom_bounding_y = 0, 0, 0, 0
		for mass in self.stars + self.black_holes:
			if mass.coordinates[0] < self.left_bounding_x:
				self.left_bounding_x = mass.coordinates[0]
			elif mass.coordinates[0] > self.right_bounding_x:
				self.right_bounding_x = mass.coordinates[0]
			if mass.coordinates[1] < self.bottom_bounding_y:
				self.bottom_bounding_y = mass.coordinates[1]
			elif mass.coordinates[1] > self.top_bounding_y:
				self.top_bounding_y = mass.coordinates[1]
