#! python -O
"""Known/visible space."""
from __future__ import division
import math
import random
import os

from globals import g
import utilities
import masses.star as star
import masses.black_hole as black_hole
import masses.nebula as nebula

class Galaxy(object):

	# black holes and stars must be at least this many parsecs apart
	min_separation_parsecs = 10
	
	def __init__(self):
		g.logging.debug("instantiated Galaxy")

	def generate(self, edges, dispersion, object_amount, worm_hole_amount=0, nebulae_amount=0, object_pool=None):
		'Generate stars, black holes, nebulae, worm holes'
		g.logging.debug("generating galaxy")

		# generate coordinates for stars AND black holes in one pass
		# since they may not overlap
		object_coordinates = utilities.random_dispersed_coordinates(
			edges[0], edges[1], edges[2], edges[3],
			amount=object_amount, dispersion=dispersion
		)

		self.stars = []
		self.black_holes = []

		# randomly generate stars
		if object_pool == None:
			object_pool = {}
			# better to convert list to dict some other, more elegant way?
			for color in masses.Star.colors:
				object_pool[color] = 1
		# mash all the objects together for randomization purposes
		object_types = []
		for name, freq in object_pool.iteritems():
			object_types += [name]*freq

		for coordinate in object_coordinates:
			object_type = object_types[random.randint(0, len(object_types)-1)]

			if object_type == 'black hole':
				self.black_holes.append(
					black_hole.BlackHole(coordinate)
				)

			else:
				self.stars.append(
					star.Star(
						coordinate, 
						star.Star.available_names.pop(random.randint(0, len(star.Star.available_names)-1)), 
						object_type
					),
				)

		# generate nebulae
		self.nebulae = []
		nebula_colors = nebula.Nebula.lobe_colors.keys()
		nebula_color_index = random.randint(0, len(nebula_colors)-1)
		nebula_offset = 80
		min_lobes = 3
		max_lobes = nebula.Nebula.max_lobes

		# minimize repeated lobe secondary/image combinations
		nebula_secondary_image_permutations = [
			(0, 1), (0, 2), (1, 1), (1, 2)
		]
		nebula_permutations_index = random.randint(0,3)

		if nebulae_amount:
			for coordinate in utilities.random_dispersed_coordinates(
				edges[0], edges[1], edges[2], edges[3],
				amount=nebulae_amount,
				dispersion=nebula.Nebula.max_offset*2
			):
				color = nebula_colors[nebula_color_index]
				# cycle through all nebula colors
				nebula_color_index -= 1
				if nebula_color_index < 0:
					nebula_color_index = len(nebula_colors)-1

				lobe_amount = random.randint(min_lobes, max_lobes)
				lobes = []
				for lobe_coordinate in utilities.random_dispersed_coordinates(
					-nebula_offset, -nebula_offset, nebula_offset, nebula_offset,
					amount = lobe_amount,
					dispersion = 15
				):
					# cycle through all lobe secondary/image combinations
					secondary_image = nebula_secondary_image_permutations[nebula_permutations_index]
					nebula_permutations_index -= 1
					if nebula_permutations_index < 0:
						nebula_permutations_index = 3

					lobes.append(
						(
							random.randint(0,1),
							random.randint(1,2),
							lobe_coordinate,
							random.randint(0,359),
							# use exponentiation to ensure floats less than 1.0 are as common as floats greater than 1.0
							10**random.uniform(-0.3, 0.3)
						)
					)
				self.nebulae.append( nebula.Nebula(coordinate, color, lobes) )

		# ensure nebulae don't overlap
		min_nebula_distance = nebula.Nebula.max_offset * 2
		for nebula1 in self.nebulae:
			for nebula2 in self.nebulae:
				if nebula1 == nebula2:
					continue
				offset_from_zero = (abs(nebula1.coordinates[0] - nebula2.coordinates[0]), abs(nebula1.coordinates[1] - nebula2.coordinates[1]))
				distance = math.sqrt(offset_from_zero[0]**2 + offset_from_zero[1]**2)
				if distance < min_nebula_distance:
					raise DataError, "at least two nebulae are not far enough apart"

		# generate worm holes
		star_indexes = range(len(self.stars))
		self.worm_holes = []
		for repeat in range(worm_hole_amount):
			index1 = star_indexes.pop(random.randint(0, len(star_indexes)-1))
			index2 = star_indexes.pop(random.randint(0, len(star_indexes)-1))

			endpoint1 = endpoint_stars[index1]
			endpoint2 = endpoint_stars[index2]
			if (endpoint1 < 0) or (endpoint1 > len(self.stars)-1) or (endpoint2 < 0) or (endpoint2 > len(self.stars)-1):
				raise RangeException, "both ends of wormhole must be within list of existing stars"
			self.worm_holes.append(WormHole(self.stars[endpoint1], self.stars[endpoint2]))

		self.derive_bounding_lines()
		self.normalize()

		# find max/min distances between all stars/black holes
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

		# previously-caculated bounding lines are now incorrect, so recalculate
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

class WormHole(object):
	"""Wormholes are a special class of object; they have no mass and can not exist independently of their endpoint stars."""

	def __init__(self, star1, star2):
		if not isinstance(star1, star.Star) or not isinstance(star2, star.Star):
			raise DataError, "both ends of wormholes must be stars"

		if star1.worm_hole or star2.worm_hole:
			raise DataError, "wormhole endpoint stars may only be used once"

		self.endpoints = (star1, star2)
		star1.worm_hole = self
		star2.worm_hole = self

		self.star1 = star1
		self.star2 = star2
