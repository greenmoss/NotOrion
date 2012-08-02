import random

import stars

def generate(amount, stars):
	star_indexes = range(len(stars))
	worm_holes = []
	for repeat in range(amount):
		index1 = star_indexes.pop(random.randint(0, len(star_indexes)-1))
		index2 = star_indexes.pop(random.randint(0, len(star_indexes)-1))

		worm_holes.append(WormHole(stars[index1], stars[index2]))
	return worm_holes

class WormHole(object):
	"""Wormholes are a special class of object; they have no mass and can not exist independently of their endpoint stars."""

	def __init__(self, star1, star2):
		if not isinstance(star1, stars.Star) or not isinstance(star2, stars.Star):
			raise DataError, "both ends of wormholes must be stars"

		if star1.worm_hole or star2.worm_hole:
			raise DataError, "wormhole endpoint stars may only be used once"

		self.endpoints = (star1, star2)
		star1.worm_hole = self
		star2.worm_hole = self

		self.star1 = star1
		self.star2 = star2
