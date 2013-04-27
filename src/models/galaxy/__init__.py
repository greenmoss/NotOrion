#! python -O
"""Known/visible space."""
from __future__ import division
import math
import random
import os
import jsonpickle
import logging
logger = logging.getLogger(__name__)

from globals import g
import utilities

import black_holes
import nebulae
import stars
import worm_holes
import orbitals

class Galaxy(object):

    # black holes and stars must be at least this many parsecs apart
    min_separation_parsecs = 10
    
    def __init__(self):
        logger.debug("instantiated Galaxy")

    def generate(self, config):
        'Generate objects in the galaxy'
        logger.debug("generating galaxy")

        # hold reference for orbitals
        self.orbitals = orbitals.Orbitals()

        self.generate_stars_and_black_holes(config)
        logger.debug("star count: %s", len(self.stars.list))
        logger.debug("planet count: %s", len(self.orbitals.planets))
        logger.debug("asteroid belt count: %s", len(self.orbitals.asteroid_belts))
        logger.debug("gas giant count: %s", len(self.orbitals.gas_giants))
        logger.debug("black hole count: %s", len(self.black_holes.list))

        # generate nebulae
        self.nebulae = nebulae.Nebulae(config.nebulae_count, config.limits)
        logger.debug("nebulae count: %s", len(self.nebulae.list))

        # generate worm holes
        self.worm_holes = worm_holes.WormHoles(config.worm_hole_count, self.stars)
        logger.debug("worm hole count: %s", len(self.worm_holes.list))

        self.derive_bounding_lines()
        self.normalize()
        self.derive_min_max_distances()

    def generate_stars_and_black_holes(self, config):
        # generate coordinates for stars AND black holes in one pass
        # since they may not overlap
        object_coordinates = utilities.random_dispersed_coordinates(
            config.limits[0], config.limits[1], config.limits[2], config.limits[3],
            amount=config.star_count, dispersion=config.dispersion
        )

        self.stars = stars.Stars(self.orbitals)
        self.black_holes = black_holes.BlackHoles()

        for coordinate in object_coordinates:
            object_type = utilities.choose_from_probability(config.object_pool)

            if object_type == 'black hole':
                self.black_holes.add(coordinate)

            else:
                # object_type is color
                self.stars.add(coordinate, object_type)

    def derive_min_max_distances(self):
        # derive max/min distances between all stars/black holes
        max_coords = (0, 0)
        self.max_distance = 0

        min_coords = ((self.right_bounding_x - self.left_bounding_x), (self.top_bounding_y - self.bottom_bounding_y))
        self.min_distance = math.sqrt(min_coords[0]**2 + min_coords[1]**2)

        for object1 in self.stars.list+self.black_holes.list:
            for object2 in self.stars.list+self.black_holes.list:
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
                    min_coords = coords
                    self.min_distance = distance
                if distance > self.max_distance:
                    max_coords = coords
                    self.max_distance = distance

        if self.min_distance < Galaxy.min_separation_parsecs:
            raise Exception, "at least two stars and/or black holes are not far enough apart"

    def normalize(self):
        'Force extreme stars/black holes to be equidistant from (0,0)'
        x_offset = (abs(self.right_bounding_x)-abs(self.left_bounding_x))/2
        y_offset = (abs(self.top_bounding_y)-abs(self.bottom_bounding_y))/2

        # recalculate all object coordinates
        for mass in self.stars.list + self.black_holes.list + self.nebulae.list:
            mass.coordinates = (mass.coordinates[0]-x_offset, mass.coordinates[1]-y_offset)

        # previously-calculated bounding lines are now incorrect, so recalculate
        self.derive_bounding_lines()

    def derive_bounding_lines(self):
        'Find bounding lines that contain all stars and black holes.'
        self.left_bounding_x, self.right_bounding_x, self.top_bounding_y, self.bottom_bounding_y = 0, 0, 0, 0
        for mass in self.stars.list + self.black_holes.list:
            if mass.coordinates[0] < self.left_bounding_x:
                self.left_bounding_x = mass.coordinates[0]
            elif mass.coordinates[0] > self.right_bounding_x:
                self.right_bounding_x = mass.coordinates[0]
            if mass.coordinates[1] < self.bottom_bounding_y:
                self.bottom_bounding_y = mass.coordinates[1]
            elif mass.coordinates[1] > self.top_bounding_y:
                self.top_bounding_y = mass.coordinates[1]
    
    def save(self):
        """Return all model data."""
        return self
