#! python -O
# a set of utilities that should be useful without any associated objects
from __future__ import division
import random
import sys
import math

class RangeException(Exception): pass

# lookup table for current or next-highest/lowest power of two
# for example, 2 is a power of 2, and thus matches
# 3 is *not* a power of 2, so the next highest is a 4, and the next lowest is 2
global POWERS_OF_2 
POWERS_OF_2 = [ 
	1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384,32768,65536,131072
]

def random_dispersed_coordinates(bottom=-1000, left=-1000, top=1000, right=1000, amount=500, dispersion=1, seed=None, debug=False):
	'within given min/max limits, generate a given number of coordinates, guaranteed to be a minimum distance apart'

	if top <= bottom:
		raise RangeException, 'top coordinate must be greater than bottom coordinate'
	if right <= left:
		raise RangeException, 'right coordinate must be greater than left coordinate'
	
	global POWERS_OF_2
	if amount > POWERS_OF_2[-1]:
		raise RangeException, 'amount may not exceed %d'%POWERS_OF_2[-1]

	# passing in a seed is useful for testing, but likely nothing else
	random.seed(seed)

	rectangles = []
	minimum_length = dispersion+1
	recurse_into_rectangle(bottom, left, top, right, amount, minimum_length, rectangles, debug=debug)
	(margin, remainder) = divmod(dispersion, 2)
	tr_margin = margin+remainder
	bl_margin = margin
	object_coordinates = []
	for rectangle in rectangles:
		bottom_bound = rectangle[0]+bl_margin
		left_bound = rectangle[1]+bl_margin
		top_bound = rectangle[2]-tr_margin
		right_bound = rectangle[3]-tr_margin
		x_coord = random.randint(left_bound, right_bound)
		y_coord = random.randint(bottom_bound, top_bound)
		object_coordinates.append( (x_coord, y_coord) )

	return object_coordinates

def recurse_into_rectangle(bottom, left, top, right, coordinate_count, minimum_length, rectangles, seed=None, debug=False):
	'''recursively split a rectangle into subrectangles
	allow sufficient area within each subrectangle for the specified minimum_length
		if each coordinate has margin 1, the minimum_length is 2, and the area is 4
			a margin of 2 has minimum_length 3 and area 9, etc
	continue dividing/recursing until each rectangle contains exactly one coordinate'''
	if minimum_length < 1:
		raise RangeException, "minimum_length must be >=1"
	if coordinate_count == 0:
		raise RangeException, "invalid coordinate_count: 0"

	if coordinate_count == 1:
		rectangles.append((bottom, left, top, right))
		return
	
	for sub_rectangle, sub_coordinate_count in randomly_split_rectangle(bottom, left, top, right, minimum_length, coordinate_count, seed, debug).iteritems():
		recurse_into_rectangle(
			sub_rectangle[0], sub_rectangle[1], sub_rectangle[2], sub_rectangle[3], 
			sub_coordinate_count, minimum_length, rectangles, seed
		)

def randomly_split_rectangle(bottom, left, top, right, minimum_length, coordinate_count, seed=None, debug=False):
	'''partition a rectangle into two sub-rectangles
	such that each has sufficient area to hold "coordinate_count"
	with area also left over for margins/"minimum_length"'''

	# passing in a seed is useful for testing, but likely nothing else
	random.seed(seed)

	minimum_area = minimum_length**2 

	coordinate_count1 = int(math.ceil(coordinate_count/2)) 

	# randomly reassign odd remainder (if any) from first half to second half
	if random.randint(0,1) and (coordinate_count1 > 1) and (coordinate_count%2):
		coordinate_count1 -= 1

	coordinate_count2 = coordinate_count - coordinate_count1 

	global POWERS_OF_2

	x_span = right-left+1
	x_chunks = int(x_span/minimum_length)
	x_remainder = x_span-(x_chunks*minimum_length)

	y_span = top-bottom+1 
	y_chunks = int(y_span/minimum_length)
	y_remainder = y_span-(y_chunks*minimum_length)

	# split vertically
	if x_span > y_span:
		y_chunks_power_of_2 = 1
		for power in POWERS_OF_2:
			if power > y_chunks:
				break
			y_chunks_power_of_2 = power

		minimum_left_x_chunks = int(math.ceil(coordinate_count1/y_chunks_power_of_2))
		for power in POWERS_OF_2:
			if power >= minimum_left_x_chunks:
				minimum_left_x_chunks = power
				break

		minimum_right_x_chunks = int(math.ceil(coordinate_count2/y_chunks_power_of_2))
		for power in POWERS_OF_2:
			if power >= minimum_right_x_chunks:
				minimum_right_x_chunks = power
				break

		remaining_x_chunks = x_chunks-minimum_left_x_chunks-minimum_right_x_chunks

		if remaining_x_chunks < 0:
			raise RangeException, 'insufficient area to hold coordinates of given minimum width'

		# would eventually be nice to actually use "random", like this:
		#random_x_chunk_offset = remaining_x_chunks and random.randint(0, remaining_x_chunks-1) 
		# but first we'd have to find out how many additional chunks *minimum* are required 
		# to make the random distribution actually look random
		# then try not to go below this amount
		# this would also allow a new parameter "gappiness" to control the permitted range 
		# offset between "half" and "minimum"
		# for simpicity's sake, we'll say "random" actually returns "half"
		random_x_chunk_offset = remaining_x_chunks and int(math.floor((remaining_x_chunks-1)/2))
		random_x_remainder_offset = random.randint(0, x_remainder)

		split_left = left + (minimum_left_x_chunks+random_x_chunk_offset)*minimum_length + random_x_remainder_offset - 1
		split_right = split_left + 1

		part_counts = {
			(bottom, left,        top, split_left): coordinate_count1,
			(bottom, split_right, top, right     ): coordinate_count2,
		}

	# split horizontally
	else:
		x_chunks_power_of_2 = 1
		for power in POWERS_OF_2:
			if power > x_chunks:
				break
			x_chunks_power_of_2 = power

		minimum_bottom_y_chunks = int(math.ceil(coordinate_count1/x_chunks_power_of_2))
		for power in POWERS_OF_2:
			if power >= minimum_bottom_y_chunks:
				minimum_bottom_y_chunks = power
				break

		minimum_top_y_chunks = int(math.ceil(coordinate_count2/x_chunks_power_of_2))
		for power in POWERS_OF_2:
			if power >= minimum_top_y_chunks:
				minimum_top_y_chunks = power
				break

		remaining_y_chunks = y_chunks-minimum_bottom_y_chunks-minimum_top_y_chunks

		if remaining_y_chunks < 0:
			raise RangeException, 'insufficient area to hold coordinates of given minimum height'

		# would eventually be nice to actually use "random", like this:
		#random_y_chunk_offset = remaining_y_chunks and random.randint(0, remaining_y_chunks-1) 
		# see note above about random_x_chunk_offset 
		random_y_chunk_offset = remaining_y_chunks and int(math.floor((remaining_y_chunks-1)/2))
		random_y_remainder_offset = random.randint(0, y_remainder)

		split_bottom = bottom + (minimum_bottom_y_chunks+random_y_chunk_offset)*minimum_length + random_y_remainder_offset - 1
		split_top = split_bottom + 1

		part_counts = {
			(bottom,    left, split_bottom, right): coordinate_count1,
			(split_top, left, top,          right): coordinate_count2,
		}

	return part_counts

def circle_vertices(radius):
	"""
	Calculate vertices sufficient to approximate a circle, centered around 0,0
	algorithm copied from https://sites.google.com/site/swinesmallpygletexamples/immediate-circle
	"""
	vertices = []
	iterations = int(2*radius*math.pi)
	sin = math.sin(2*math.pi / iterations)
	cos = math.cos(2*math.pi / iterations)
	dx, dy = radius, 0
	for i in range(iterations+1):
		vertices.append((round(dx,4), round(dy,4)))
		dx, dy = (dx*cos + dy*sin), (dy*cos - dx*sin)
	return vertices
