#! python -O
"""All physical objects within the galaxy."""
from __future__ import division
import random

from globals import g
import utilities
import galaxy.background_star

class Galaxy(object):
	
	def __init__(self):
		g.logging.debug("instantiated Galaxy")
		self.background_stars = []

	def generate(self, foreground_limits, foreground_dispersion, foreground_object_count, worm_hole_count=0, nebulae_count=0, object_pool=None):
		'Generate foreground/background stars, black holes, and nebulae'
		g.logging.debug("generating galaxy")

		# randomly generate background stars
		for coordinate in utilities.random_dispersed_coordinates(amount=8000, dispersion=3):
			color = []
			for index in range(0,3):
				color.append(64)
			# allow one or two of the bytes to be less, which allows slight coloration
			color[random.randint(0,2)] = random.randint(32,64)
			color[random.randint(0,2)] = random.randint(32,64)
			self.background_stars.append(
				galaxy.background_star.BackgroundStar(coordinate, color),
			)
		return

		# generate coordinates for foreground stars AND black holes in one pass
		# since they may not overlap
		object_coordinates = utilities.random_dispersed_coordinates(
			foreground_limits[0], foreground_limits[1], foreground_limits[2], foreground_limits[3],
			amount=foreground_object_count, dispersion=foreground_dispersion
		)

		available_star_names = []
		with open(os.path.join(self.data.paths['resources_dir'], 'star_names.txt')) as star_names_file:
			for line in star_names_file:
				available_star_names.append(line.rstrip())

		foreground_stars = []
		black_holes = []

		# randomly generate foreground stars
		if object_pool == None:
			object_pool = {}
			# better to convert list to dict some other, more elegant way?
			for color in galaxy_objects.ForegroundStar.colors.keys():
				object_pool[color] = 1
		# mash all the objects together for randomization purposes
		object_list = []
		for name, freq in object_pool.iteritems():
			object_list += [name]*freq

		for coordinate in object_coordinates:
			object = object_list[random.randint(0, len(object_list)-1)]

			if object == 'black hole':
				black_holes.append(
					galaxy_objects.BlackHole(coordinate)
				)

			else:
				foreground_stars.append(
					galaxy_objects.ForegroundStar(
						coordinate, 
						available_star_names.pop(random.randint(0, len(available_star_names)-1)), 
						object
					),
				)

		# generate nebulae
		nebulae = []
		nebula_colors = galaxy_objects.Nebula.lobe_colors.keys()
		nebula_color_index = random.randint(0, len(nebula_colors)-1)
		nebula_offset = 80
		min_lobes = 3
		max_lobes = galaxy_objects.Nebula.max_lobes

		# minimize repeated lobe secondary/sprite combinations
		nebula_secondary_sprite_permutations = [
			(0, 1), (0, 2), (1, 1), (1, 2)
		]
		nebula_permutations_index = random.randint(0,3)

		if nebulae_count:
			for coordinate in utilities.random_dispersed_coordinates(
				foreground_limits[0], foreground_limits[1], foreground_limits[2], foreground_limits[3],
				amount=nebulae_count,
				dispersion=galaxy_objects.Nebula.max_offset*2
			):
				color = nebula_colors[nebula_color_index]
				# cycle through all nebula colors
				nebula_color_index -= 1
				if nebula_color_index < 0:
					nebula_color_index = len(nebula_colors)-1

				lobe_count = random.randint(min_lobes, max_lobes)
				lobes = []
				for lobe_coordinate in utilities.random_dispersed_coordinates(
					-nebula_offset, -nebula_offset, nebula_offset, nebula_offset,
					amount = lobe_count,
					dispersion = 15
				):
					# cycle through all lobe secondary/sprite combinations
					secondary_sprite = nebula_secondary_sprite_permutations[nebula_permutations_index]
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
				nebulae.append( galaxy_objects.Nebula(coordinate, color, lobes) )

		# generate worm holes
		star_indexes = range(len(foreground_stars))
		worm_holes = []
		for repeat in range(worm_hole_count):
			index1 = star_indexes.pop(random.randint(0, len(star_indexes)-1))
			index2 = star_indexes.pop(random.randint(0, len(star_indexes)-1))
			worm_holes.append((index1, index2))

		self.data.galaxy_objects = galaxy_objects.All(
			foreground_stars,
			background_stars,
			black_holes,
			nebulae,
			worm_holes
		)
