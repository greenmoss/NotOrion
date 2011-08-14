#! python -O
# a set of utilities, which should be useful without any associated objects
from __future__ import division
import random
import math
import sys
import math

class RangeException(Exception): pass

global nest_level
nest_level = 0

def random_dispersed_coordinates(bottom=-1000, left=-1000, top=1000, right=1000, amount=500, dispersion=1, seed=None):
	'within given min/max limits, generate a given number of coordinates, guaranteed to be a minimum distance apart'

	if top <= bottom:
		raise RangeException, 'top coordinate must be greater than bottom coordinate'
	if right <= left:
		raise RangeException, 'right coordinate must be greater than left coordinate'

	# passing in a seed is useful for testing, but likely nothing else
	random.seed(seed)

	rectangles = []
	minimum_length = dispersion+1
	recurse_into_rectangle(bottom, left, top, right, amount, minimum_length, rectangles)
	print len(rectangles)

	object_coordinates = []
	#return object_coordinates

def recurse_into_rectangle(bottom, left, top, right, coordinate_count, minimum_length, rectangles):
	'''recursively split a rectangle into subrectangles
	allow sufficient area within each subrectangle for the specified minimum_length
		if each coordinate has margin 1, the minimum_length is 2, and the area is 4
			a margin of 2 has minimum_length 3 and area 9, etc
	continue dividing/recursing until each rectangle contains exactly one coordinate'''

	if coordinate_count == 0:
		raise Exception, "invalid coordinate_count: 0"

	if coordinate_count == 1:
		rectangles.append((bottom, left, top, right))
		return
	
	for sub_rectangle, sub_coordinate_count in randomly_split_rectangle(bottom, left, top, right, minimum_length, coordinate_count).iteritems():
		recurse_into_rectangle(
			sub_rectangle[0], sub_rectangle[1], sub_rectangle[2], sub_rectangle[3], 
			sub_coordinate_count, minimum_length, rectangles
		)

def randomly_split_rectangle(bottom, left, top, right, minimum_length, coordinate_count):
	'''partition a rectangle into two sub-rectangles
	such that each has sufficient area to hold "coordinate_count"
	with area also left over for margins/"minimum_length"'''
	minimum_area = minimum_length**2 
	coordinate_count1 = int(math.ceil(coordinate_count/2)) 

	# randomly reassign odd remainder (if any) from first half to second half
	if random.randint(0,1) and (coordinate_count1 > 1) and (coordinate_count%2):
		coordinate_count1 -= 1

	coordinate_count2 = coordinate_count - coordinate_count1 
	minimum_split_area1 = coordinate_count1*minimum_area 
	minimum_split_area2 = coordinate_count2*minimum_area 

	x_span = right-left+1 
	x_chunks = int(x_span/minimum_length)
	x_remainder = x_span-(x_chunks*minimum_length)

	y_span = top-bottom+1 
	y_chunks = int(y_span/minimum_length)
	y_remainder = y_span-(y_chunks*minimum_length)

	chunk_area = x_chunks*y_chunks

	split_rectangles = []

	# split vertically
	if x_span > y_span:
		minimum_left_x_chunks = int(math.ceil(coordinate_count1/y_chunks))
		minimum_right_x_chunks = int(math.ceil(coordinate_count2/y_chunks))
		remaining_x_chunks = x_chunks-minimum_left_x_chunks-minimum_right_x_chunks

		if remaining_x_chunks < 0:
			raise Exception, 'insufficient area to hold coordinates of given minimum width'

		random_x_chunk_offset = random.randint(0, remaining_x_chunks) 
		random_x_remainder_offset = random.randint(0, x_remainder)

		split_left = left + (minimum_left_x_chunks+random_x_chunk_offset)*minimum_length + random_x_remainder_offset
		split_right = split_left + 1

		part_counts = {
			(bottom, left,        top, split_left): coordinate_count1,
			(bottom, split_right, top, right     ): coordinate_count2,
		}

	# split horizontally
	else:
		minimum_bottom_y_chunks = int(math.ceil(coordinate_count1/x_chunks))
		minimum_top_y_chunks = int(math.ceil(coordinate_count2/x_chunks))
		remaining_y_chunks = y_chunks-minimum_bottom_y_chunks-minimum_top_y_chunks

		if remaining_y_chunks < 0:
			raise Exception, 'insufficient area to hold coordinates of given minimum height'

		random_y_chunk_offset = random.randint(0, remaining_y_chunks) 
		random_y_remainder_offset = random.randint(0, y_remainder)

		split_bottom = bottom + (minimum_bottom_y_chunks+random_y_chunk_offset)*minimum_length + random_y_remainder_offset
		split_top = split_bottom + 1

		part_counts = {
			(bottom,    left, split_bottom, right): coordinate_count1,
			(split_top, left, top,          right): coordinate_count2,
		}

	return part_counts
