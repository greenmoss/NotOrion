#! python -O
from globals import g

import masses

class Nebula(masses.Mass):
	"""A nebula. These interact with other objects, eg ships by slowing movement. They also look pretty on the screen."""

	# all lobe colors in one nebula center on either red, green, or blue in the color wheel:
	lobe_colors = {
		'red': ['pink', 'yellow'],
		'green': ['cyan', 'yellow'],
		'blue': ['cyan', 'pink']
	}

	# load all available lobe image files
	lobe_image_files = {}
	for primary in lobe_colors.keys():
		for secondary in lobe_colors[primary]:
			for sprite_number in [1,2]:
				id = '%s_%s_%d'%(primary, secondary, sprite_number)
				lobe_image_files[id] = '%s_%s_nebula_%d.png'%(primary, secondary ,sprite_number)
	max_offset = 200
	min_scale = 0.25
	max_scale = 4.0
	min_lobes = 1
	max_lobes = 6

	def __init__(self, coordinates, color, lobes):
		if (len(lobes) > self.max_lobes) or (len(lobes) < self.min_lobes):
			raise RangeException, "number of lobes must be between 1 and 6"
		if not self.lobe_colors.has_key(color):
			raise DataError, "invalid primary color: %s"%color

		super(Nebula, self).__init__(coordinates)
		self.primary_color = color
		self.lobes = []
		for lobe in lobes:
			lobe_info = {}
			if (lobe[0] > 1) or (lobe[0] < 0):
				raise RangeException, "lobe secondary color must be between 0 and 1"
			lobe_info['secondary'] = self.lobe_colors[color][lobe[0]]

			if (lobe[1] > 2) or (lobe[1] < 1):
				raise RangeException, "lobe sprite identifier must be between 1 and 2"
			lobe_info['image_id'] = lobe[1]

			if (lobe[2][0] > self.max_offset) or (lobe[2][0] < -self.max_offset) or (lobe[2][1] > self.max_offset) or (lobe[2][1] < -self.max_offset):
				raise RangeException, "lobe x and y coordinates must fall between %d and %d"%(self.max_offset, -self.max_offset)
			lobe_info['coordinates'] = lobe[2]

			if (lobe[3] > 360) or (lobe[3] < 0):
				raise RangeException, "lobe rotation must be between 0 and 360"
			lobe_info['rotation'] = lobe[3]

			if (lobe[4] > self.max_scale) or (lobe[4] < self.min_scale):
				raise RangeException, "lobe scale must fall between %0.2f and %0.2f"%(self.min_scale, self.max_scale)
			lobe_info['scale'] = lobe[4]

			lobe_info['rendered_scale'] = 1.0
			lobe_info['rendered_coordinates'] = (0,0)

			self.lobes.append(lobe_info)
