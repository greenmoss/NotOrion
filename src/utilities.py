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

# lookup table for current or next-highest power of two
# for example, 2 is a power of 2, and thus matches exactly
# 3 is *not* a power of 2, so the next highest is a 4
global powers_of_2 
powers_of_2 = [ 
	1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384,32768,65536,131072
]
# lookup table for square roots of powers of 2
# this will be needed for finding the minimum dimension of squares
global powers_of_2_square_roots
powers_of_2_square_roots = {
	1: 1,     2: 2,     4: 2,       8: 3,       16: 4,      32: 6,
	64: 8,    128: 12,  256: 16,    512: 23,    1024: 32,   2048: 46,
	4096: 64, 8192: 91, 16384: 128, 32768: 182, 65536: 256, 131072: 363,
}

def random_dispersed_coordinates(bottom=-1000, left=-1000, top=1000, right=1000, amount=500, dispersion=1, seed=None):
	'within given min/max limits, generate a given number of coordinates, guaranteed to be a minimum distance apart'

	if top <= bottom:
		raise RangeException, 'top coordinate must be greater than bottom coordinate'
	if right <= left:
		raise RangeException, 'right coordinate must be greater than left coordinate'
	
	global powers_of_2
	if amount > powers_of_2[-1]:
		raise RangeException, 'amount may not exceed %d'%powers_of_2[-1]

	# passing in a seed is useful for testing, but likely nothing else
	random.seed(seed)

	rectangles = []
	minimum_length = dispersion+1
	print "minimum_length: %d"%minimum_length
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
	global nest_level
	indent = '%2d:'%nest_level
	for level in range(nest_level):
		indent += ' '
	sys.stdout.write(indent)
	print ("bottom, left, top, right: ", (bottom, left, top, right))
	sys.stdout.write(indent)
	print "coordinate_count: %d"%coordinate_count

	if coordinate_count == 0:
		raise Exception, "invalid coordinate_count: 0"

	if coordinate_count == 1:
		rectangles.append((bottom, left, top, right))
		return
	
	for sub_rectangle, sub_coordinate_count in randomly_split_rectangle(bottom, left, top, right, minimum_length, coordinate_count).iteritems():
		sys.stdout.write(indent)
		print ("sub_rectangle: ", sub_rectangle)
		nest_level += 1
		recurse_into_rectangle(
			sub_rectangle[0], sub_rectangle[1], sub_rectangle[2], sub_rectangle[3], 
			sub_coordinate_count, minimum_length, rectangles
		)
		nest_level -= 1

def randomly_split_rectangle(bottom, left, top, right, minimum_length, coordinate_count):
	'''partition a rectangle into two sub-rectangles
	such that each has sufficient area to hold "coordinate_count"
	with area also left over for margins/"minimum_length"'''
	minimum_area = minimum_length**2 

	global nest_level
	indent = '%2d:'%nest_level
	for level in range(nest_level):
		indent += ' '

	coordinate_count1 = int(math.ceil(coordinate_count/2)) 

	# randomly reassign odd remainder (if any) from first half to second half
	if random.randint(0,1) and (coordinate_count1 > 1) and (coordinate_count%2):
		coordinate_count1 -= 1

	coordinate_count2 = coordinate_count - coordinate_count1 

	sys.stdout.write(indent)
	print "coordinate_count1: %d; coordinate_count2: %d"%(coordinate_count1, coordinate_count2)

	# for each side of the split, what is the current or next-highest power of two?
	global powers_of_2

#	count1_power_of_2 = 1
#	count1_previous_power_of_2 = 1
#	for power in powers_of_2:
#		if coordinate_count1 > power:
#			count1_previous_power_of_2 = power
#			continue
#		count1_power_of_2 = power
#		break
#	sys.stdout.write(indent)
#	print "count1_power_of_2: %d; count1_previous_power_of_2: %d"%(count1_power_of_2, count1_previous_power_of_2)
#
#	count2_power_of_2 = 1
#	count2_previous_power_of_2 = 1
#	for power in powers_of_2:
#		if coordinate_count2 > power:
#			count2_previous_power_of_2 = power
#			continue
#		count2_power_of_2 = power
#		break
#	sys.stdout.write(indent)
#	print "count2_power_of_2: %d; count2_previous_power_of_2: %d"%(count2_power_of_2, count2_previous_power_of_2)

	x_span = right-left+1
	x_chunks = int(x_span/minimum_length)
	x_remainder = x_span-(x_chunks*minimum_length)

	y_span = top-bottom+1 
	y_chunks = int(y_span/minimum_length)
	y_remainder = y_span-(y_chunks*minimum_length)

	sys.stdout.write(indent)
	print "x_span: %d; x_chunks: %d; x_remainder: %d"%(x_span, x_chunks, x_remainder)
	sys.stdout.write(indent)
	print "y_span: %d; y_chunks: %d; y_remainder: %d"%(y_span, y_chunks, y_remainder)

	# split vertically
	if x_span > y_span:
		y_chunks_power_of_2 = 1
		for power in powers_of_2:
			if power > y_chunks:
				break
			y_chunks_power_of_2 = power
		sys.stdout.write(indent)
		print "y_chunks_power_of_2: %d"%(y_chunks_power_of_2)

		minimum_left_x_chunks = int(math.ceil(coordinate_count1/y_chunks_power_of_2))
		sys.stdout.write(indent)
		print "minimum_left_x_chunks: %d"%(minimum_left_x_chunks)
		for power in powers_of_2:
			if power >= minimum_left_x_chunks:
				minimum_left_x_chunks = power
				break

		minimum_right_x_chunks = int(math.ceil(coordinate_count2/y_chunks_power_of_2))
		sys.stdout.write(indent)
		print "minimum_right_x_chunks: %d"%(minimum_right_x_chunks)
		for power in powers_of_2:
			if power >= minimum_right_x_chunks:
				minimum_right_x_chunks = power
				break

		remaining_x_chunks = x_chunks-minimum_left_x_chunks-minimum_right_x_chunks
		sys.stdout.write(indent)
		print "minimum_left_x_chunks: %d; minimum_right_x_chunks: %d; remaining_x_chunks: %d"%(minimum_left_x_chunks, minimum_right_x_chunks, remaining_x_chunks)

		if remaining_x_chunks < 0:
			raise Exception, 'insufficient area to hold coordinates of given minimum width'

		random_x_chunk_offset = remaining_x_chunks and random.randint(0, remaining_x_chunks-1) 
		#random_x_chunk_offset = remaining_x_chunks and int(math.ceil(remaining_x_chunks/2))
		random_x_remainder_offset = random.randint(0, x_remainder)
		sys.stdout.write(indent)
		print "random_x_chunk_offset: %d; random_x_remainder_offset: %d"%(random_x_chunk_offset, random_x_remainder_offset)

		split_left = left + (minimum_left_x_chunks+random_x_chunk_offset)*minimum_length + random_x_remainder_offset - 1
		split_right = split_left + 1
		sys.stdout.write(indent)
		print "split_left: %d; split_right: %d"%(split_left, split_right)

		part_counts = {
			(bottom, left,        top, split_left): coordinate_count1,
			(bottom, split_right, top, right     ): coordinate_count2,
		}

	# split horizontally
	else:
		x_chunks_power_of_2 = 1
		for power in powers_of_2:
			if power > x_chunks:
				break
			x_chunks_power_of_2 = power
		sys.stdout.write(indent)
		print "x_chunks_power_of_2: %d"%(x_chunks_power_of_2)

		minimum_bottom_y_chunks = int(math.ceil(coordinate_count1/x_chunks_power_of_2))
		sys.stdout.write(indent)
		print "minimum_bottom_y_chunks: %d"%(minimum_bottom_y_chunks)
		for power in powers_of_2:
			if power >= minimum_bottom_y_chunks:
				minimum_bottom_y_chunks = power
				break

		minimum_top_y_chunks = int(math.ceil(coordinate_count2/x_chunks_power_of_2))
		sys.stdout.write(indent)
		print "minimum_top_y_chunks: %d"%(minimum_top_y_chunks)
		for power in powers_of_2:
			if power >= minimum_top_y_chunks:
				minimum_top_y_chunks = power
				break

		remaining_y_chunks = y_chunks-minimum_bottom_y_chunks-minimum_top_y_chunks
		sys.stdout.write(indent)
		print "minimum_bottom_y_chunks: %d; minimum_top_y_chunks: %d; remaining_y_chunks: %d"%(minimum_bottom_y_chunks, minimum_top_y_chunks, remaining_y_chunks)

		if remaining_y_chunks < 0:
			raise Exception, 'insufficient area to hold coordinates of given minimum height'

		random_y_chunk_offset = remaining_y_chunks and random.randint(0, remaining_y_chunks-1) 
		#random_y_chunk_offset = remaining_y_chunks and int(math.ceil(remaining_y_chunks/2))
		random_y_remainder_offset = random.randint(0, y_remainder)
		sys.stdout.write(indent)
		print "random_y_chunk_offset: %d; random_y_remainder_offset: %d"%(random_y_chunk_offset, random_y_remainder_offset)

		split_bottom = bottom + (minimum_bottom_y_chunks+random_y_chunk_offset)*minimum_length + random_y_remainder_offset - 1
		split_top = split_bottom + 1
		sys.stdout.write(indent)
		print "split_bottom: %d; split_top: %d"%(split_bottom, split_top)

		part_counts = {
			(bottom,    left, split_bottom, right): coordinate_count1,
			(split_top, left, top,          right): coordinate_count2,
		}

	return part_counts
