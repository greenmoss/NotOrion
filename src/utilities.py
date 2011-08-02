#! python -O
# a set of utilities, which should be useful without any associated objects
import random

class RangeException(Exception): pass

def random_dispersed_coordinates(bottom=-1000, left=-1000, top=1000, right=1000, amount=500, dispersion=1, seed=None, existing=None):
	'within given min/max limits, generate a given number of coordinates, guaranteed to be a minimum distance apart'

	if top <= bottom:
		raise RangeException, 'top coordinate must be greater than bottom coordinate'
	if right <= left:
		raise RangeException, 'right coordinate must be greater than left coordinate'

	# never allow retries to exceed the number of available placement coordinates
	# permissible retries starts with the full number of available coordinates
	# and decrements for every used coordinate
	# actually this is not an accurate way to define all remaining available coordinates
	# so we're sacrifice accuracy in favor of simplicity
	x_span = right-left+1
	y_span = top-bottom+1
	permissible_retries = x_span * y_span
	if (amount*dispersion) > permissible_retries:
		raise RangeException, 'given dispersed amount can not fit within given space'

	# passing in a seed is useful for testing, but likely nothing else
	random.seed(seed)

	object_coordinates = {}
	if existing:
		all_used_coordinates = existing
	else:
		all_used_coordinates = {}

	retry_vector = (random.randint(int(left/10), int(right/10)),random.randint(int(bottom/10), int(top/10)))
	for i in range(amount):
		random_coordinate = (random.randint(left, right), random.randint(bottom, top))
		first_coordinate = random_coordinate
		retries = 0
		while all_used_coordinates.has_key(random_coordinate):
			random_coordinate = [random_coordinate[0]+retry_vector[0], random_coordinate[1]+retry_vector[1]]
			if random_coordinate[0] > right:
				random_coordinate[0] -= x_span
			if random_coordinate[0] < left:
				random_coordinate[0] += x_span
			if random_coordinate[1] > top:
				random_coordinate[1] -= y_span
			if random_coordinate[1] < bottom:
				random_coordinate[1] += y_span
			random_coordinate = (random_coordinate[0], random_coordinate[1])
			if (random_coordinate == first_coordinate):
				if retries > permissible_retries:
					raise Exception, 'ran out of available placement coordinates'
				# retry with a different random vector
				retry_vector = (random.randint(int(left/10), int(right/10)),random.randint(int(bottom/10), int(top/10)))
		chosen = random_coordinate

		# disallow use of neighbors, out to dispersion distance
		for x in range(chosen[0]-dispersion+1,chosen[0]+dispersion):
			for y in range(chosen[1]-dispersion+1,chosen[1]+dispersion):
				if not all_used_coordinates.has_key((x,y)):
					all_used_coordinates[(x,y)] = True
					permissible_retries -= 1
		object_coordinates[chosen] = True

	return (object_coordinates.keys(), all_used_coordinates)
