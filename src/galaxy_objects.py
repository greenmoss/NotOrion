from __future__ import division
import pyglet
from pyglet.gl import *
import math
import struct # for pack/unpack operations on byte representations of images

class MissingDataException(Exception): pass
class DataError(Exception): pass
class RangeException(Exception): pass

class SpriteMasksGroup(pyglet.graphics.Group):
	def set_state(self):
		glDisable(GL_BLEND)

	def unset_state(self):
		glEnable(GL_BLEND)

class All(object):
	"""All galaxy objects are referenced from this object."""
	sprites_batch1 = pyglet.graphics.Batch()
	# because we have to draw raw GL objects in between sprite, create multiple batch layers
	sprites_batch2 = pyglet.graphics.Batch()
	#render_groups = {}
	# python equivalent of ruby's each_with_index?
	#for group_name in ['nebulae', 'black_holes', 'stars', 'labels']:
	#	render_groups
	nebulae_group = pyglet.graphics.OrderedGroup(0)
	black_holes_group = pyglet.graphics.OrderedGroup(1)
	stars_group = pyglet.graphics.OrderedGroup(2)
	labels_group = pyglet.graphics.OrderedGroup(3)

	# masks, for color picking
	sprite_masks_batch = pyglet.graphics.Batch()
	sprite_masks_group = SpriteMasksGroup()
	# ensure mask bitmaps are only calculated once per bitmap path
	mask_bitmaps = {}

	min_foreground_separation = 10

	def __init__(self, named_stars, background_stars, black_holes=[], nebulae=[], worm_holes=[]):
		if len(background_stars) < 1:
			raise MissingDataException, "background_stars must have at least one element"
		self.background_stars = background_stars

		if len(named_stars) < 2:
			raise MissingDataException, "named_stars must have at least two elements"

		self.named_stars = named_stars
		self.black_holes = black_holes
		self.nebulae = nebulae

		self.scalable_objects = self.named_stars+self.black_holes

		self.derive_bounding_lines()
		self.normalize()

		# find max/min distances between scalable objects
		self.max_coords = (0, 0)
		self.max_distance = 0
		self.min_coords = ((self.right_bounding_x - self.left_bounding_x), (self.top_bounding_y - self.bottom_bounding_y))
		self.min_distance = math.sqrt(self.min_coords[0]**2 + self.min_coords[1]**2)
		for scalable1 in self.scalable_objects:
			for scalable2 in self.scalable_objects:
				if scalable1 == scalable2:
					continue
				max_x = scalable1.coordinates[0]
				min_x = scalable2.coordinates[0]
				if scalable2.coordinates[0] > scalable1.coordinates[0]:
					max_x = scalable2.coordinates[0]
					min_x = scalable1.coordinates[0]
				max_y = scalable1.coordinates[1]
				min_y = scalable2.coordinates[1]
				if scalable2.coordinates[1] > scalable1.coordinates[1]:
					max_y = scalable2.coordinates[1]
					min_y = scalable1.coordinates[1]
				coords = ((max_x - min_x), (max_y - min_y))
				distance = math.sqrt(coords[0]**2 + coords[1]**2)
				if distance < self.min_distance:
					self.min_coords = coords
					self.min_distance = distance
				if distance > self.max_distance:
					self.max_coords = coords
					self.max_distance = distance
		if self.min_distance < self.min_foreground_separation:
			raise DataError, "at least two foreground objects are not far enough apart"

		# ensure nebulae don't overlap
		min_nebula_distance = Nebula.max_offset * 2
		for nebula1 in self.nebulae:
			for nebula2 in self.nebulae:
				if nebula1 == nebula2:
					continue
				offset_from_zero = (abs(nebula1.coordinates[0] - nebula2.coordinates[0]), abs(nebula1.coordinates[1] - nebula2.coordinates[1]))
				distance = math.sqrt(offset_from_zero[0]**2 + offset_from_zero[1]**2)
				if distance < min_nebula_distance:
					raise DataError, "at least two nebulae are not far enough apart"

		# create vertex/color list for all background stars
		# will be invoked as background_vertex_list.draw(pyglet.gl.GL_POINTS)
		self.background_star_vertices = []
		self.background_star_colors = []
		for background_star in self.background_stars:
			[self.background_star_vertices.append(vertex) for vertex in background_star.coordinates]
			[self.background_star_colors.append(vertex) for vertex in background_star.color]

		self.constitute_background_star_vertices()

		# create worm holes
		self.worm_holes = []
		for endpoint_stars in worm_holes:
			endpoint1 = endpoint_stars[0]
			endpoint2 = endpoint_stars[1]
			if (endpoint1 < 0) or (endpoint1 > len(self.named_stars)-1) or (endpoint2 < 0) or (endpoint2 > len(self.named_stars)-1):
				raise RangeException, "both ends of wormhole must be within list of existing stars"
			self.worm_holes.append(WormHole(self.named_stars[endpoint1], self.named_stars[endpoint2]))

		self.scaling_factor = None

		self.assign_pick_colors()

	def assign_pick_colors(self):
		'For color mouse picking, assign a unique color to each pickable object'
		red,green,blue = 255,255,255

		# store backreferences (eg color to object) here
		self.color_picks = {}

		# stars
		for star in self.named_stars:
			star.sprite_image_mask.color = (red,green,blue)
			self.color_picks[(red,green,blue)] = star
			(red,green,blue) = self.get_next_mask_color(red,green,blue)

		# black holes (currently unpickable)
		for black_hole in self.black_holes:
			black_hole.sprite_image_mask.color = (red,green,blue)
			self.color_picks[(red,green,blue)] = black_hole
			(red,green,blue) = self.get_next_mask_color(red,green,blue)

		# worm holes
		for worm_hole in self.worm_holes:
			worm_hole.mask_vertex_list.colors = [red,green,blue,red,green,blue]
			self.color_picks[(red,green,blue)] = worm_hole
			(red,green,blue) = self.get_next_mask_color(red,green,blue)

	def get_next_mask_color(self, red, green, blue):
		'Decrement through mask colors, always returning one less than was given'
		red -= 1
		# "wrap" red, then green, then blue
		if red < 0:
			red = 255
			green -= 1
		if green < 0:
			green = 255
			blue -= 1
		if blue < 0:
			# this gives us potentially millions of object colors
			# with that many objects, this game would have already encountered other issues
			# so it is very unlikely we will ever hit this condition
			raise RangeException, "ran out of available ID colors"

		return (red,green,blue)

	def constitute_background_star_vertices(self):
		self.background_vertex_list = pyglet.graphics.vertex_list(
			len(self.background_stars),
			('v3i/static', self.background_star_vertices),
			('c3B/static', self.background_star_colors)
		)
	
	def rescale(self, scaling_factor):
		"Recalculate scales if necessary"
		if not (self.scaling_factor == scaling_factor):
			self.scaling_factor = scaling_factor
			for star in self.named_stars:
				star.scale_coordinates(scaling_factor)
			for black_hole in self.black_holes:
				black_hole.scale_coordinates(scaling_factor)
			for nebula in self.nebulae:
				nebula.scale_coordinates_and_size(scaling_factor)
			for worm_hole in self.worm_holes:
				worm_hole.scale_coordinates()

	def draw(self, scaling_factor):
		"Draw all galaxy objects"
		self.rescale(scaling_factor)

		self.sprites_batch1.draw()
		for worm_hole in self.worm_holes:
			worm_hole.vertex_list.draw(pyglet.gl.GL_LINES)

		for star in self.named_stars:
			if star.marker_visible:
				star.marker.draw()

		self.sprites_batch2.draw()
	
	def draw_masks(self, scaling_factor):
		"Draw all galaxy object masks"
		self.rescale(scaling_factor)

		for worm_hole in self.worm_holes:
			worm_hole.mask_vertex_list.draw(pyglet.gl.GL_LINES)
		self.sprite_masks_batch.draw()

	def normalize(self):
		'Force extreme foreground objects to be equidistant from (0,0)'
		x_offset = (abs(self.right_bounding_x)-abs(self.left_bounding_x))/2
		y_offset = (abs(self.top_bounding_y)-abs(self.bottom_bounding_y))/2

		# recalculate all object coordinates
		for scalable in self.scalable_objects + self.nebulae:
			scalable.coordinates = (scalable.coordinates[0]-x_offset, scalable.coordinates[1]-y_offset)

		# previously-caculated bounding lines are now incorrect, so recalculate
		self.derive_bounding_lines()

	def derive_bounding_lines(self):
		'Find bounding lines that contain all scalable objects.'
		self.left_bounding_x, self.right_bounding_x, self.top_bounding_y, self.bottom_bounding_y = 0, 0, 0, 0
		for scalable in self.scalable_objects:
			if scalable.coordinates[0] < self.left_bounding_x:
				self.left_bounding_x = scalable.coordinates[0]
			elif scalable.coordinates[0] > self.right_bounding_x:
				self.right_bounding_x = scalable.coordinates[0]
			if scalable.coordinates[1] < self.bottom_bounding_y:
				self.bottom_bounding_y = scalable.coordinates[1]
			elif scalable.coordinates[1] > self.top_bounding_y:
				self.top_bounding_y = scalable.coordinates[1]
	
	def animate(self, dt):
		'Perform animations.'
		# 360 * dt / 20 == 18 * dt
		black_hole_rotation_delta = 18.*dt
		for black_hole in self.black_holes:
			black_hole.sprite.rotation -= black_hole_rotation_delta
			black_hole.sprite_image_mask.rotation = black_hole.sprite.rotation
	
	def __getstate__(self):
		"Exclude unpicklable attributes"
		out_dict = self.__dict__.copy()
		del out_dict['background_vertex_list']
		return(out_dict)
	
	def __setstate__(self, dict):
		"Reconstitute unpicklable attributes"
		self.__dict__.update(dict)
		self.constitute_background_star_vertices()
		self.assign_pick_colors()

class BackgroundStar(All):
	'A simplified star for the background, to be drawn only as a point source'

	def __init__(self, coordinates, color):
		self.coordinates = (coordinates[0], coordinates[1], 0)
		self.color = color
	
	def __getstate__(self):
		"This is required to allow All to be pickled"
		self.__dict__

class ForegroundObject(All):
	'All foreground objects that appear in the galaxy window, eg stars, black holes, and nebulae.'

	# all will need to load images from pyglet's resource path
	pyglet.resource.path = ['../images']
	pyglet.resource.reindex()

	def __init__(self, coordinates):
		if not (-10000 < coordinates[0] < 10000) or not (-10000 < coordinates[1] < 10000):
			raise RangeException, "coordinates must be between -10000 and 10000"

		self.coordinates = coordinates
	
	def __getstate__(self):
		"This is required to allow All to be pickled"
		self.__dict__

class ScaledForegroundObject(ForegroundObject):
	'All foreground objects that maintain a constant size across rescales, eg stars and black holes.'

	def __init__(self, coordinates, image_file, group):
		super(ScaledForegroundObject, self).__init__(coordinates)
		self.group = group

		self.image_file = image_file
		self.group = group
		self.coordinates = coordinates

		self.sprite_coordinates = self.coordinates
		self.constitute_scaled_foreground_sprite()

		self.scaled_sprite_origin = (int(self.sprite_origin[0]*self.sprite.scale), int(self.sprite_origin[1]*self.sprite.scale))

	def constitute_scaled_foreground_sprite(self):
		'sprites must be reconstituted after pickling'
		image = pyglet.resource.image(self.image_file)
		self.sprite = pyglet.sprite.Sprite(image,
			x=self.sprite_coordinates[0], y=self.sprite_coordinates[1]
		)
		self.sprite_origin = (int(image.width/2), int(image.height/2))
		self.sprite.image.anchor_x = self.sprite_origin[0]
		self.sprite.image.anchor_y = self.sprite_origin[1]
		self.sprite.batch = self.sprites_batch2
		self.sprite.group = self.group

		if self.mask_bitmaps.has_key(self.image_file):
			# reuse existing bitmap
			mask = self.mask_bitmaps[image_file]

		else:
			# generate new bitmap
			mask = pyglet.image.create(image.width, image.height)
			image_data = image.get_image_data()
			pixel_bytes = image_data.get_data('RGBA', image_data.width * 4)
			mask_bytes = ''
			for position in range(int(len(pixel_bytes)/4)):
				bytes = struct.unpack_from('4c', pixel_bytes, 4*position)

				# alpha channel is partially opaque, set alpha to 255
				if ord(bytes[3]) > 0:
					mask_bytes += '\xff\xff\xff\xff'

				# alpha channel is fully transparent, set alpha to 0
				else:
					mask_bytes += '\xff\xff\xff\x00'
			mask.image_data.set_data('RGBA', image_data.width * 4, mask_bytes)

		self.sprite_image_mask = pyglet.sprite.Sprite(mask.texture,
			x=self.sprite_coordinates[0], y=self.sprite_coordinates[1]
		)
		self.sprite_image_mask.image.anchor_x = self.sprite_origin[0]
		self.sprite_image_mask.image.anchor_y = self.sprite_origin[1]
		self.sprite_image_mask.batch = self.sprite_masks_batch
		self.sprite_image_mask.group = self.sprite_masks_group

	def scale_coordinates(self, scaling_factor):
		"Set object's sprite coordinates based on a scaling factor."
		self.sprite_coordinates = (int(self.coordinates[0]/scaling_factor), int(self.coordinates[1]/scaling_factor))
		self.sprite.x = self.sprite_coordinates[0]
		self.sprite.y = self.sprite_coordinates[1]
		self.sprite_image_mask.x = self.sprite_coordinates[0]
		self.sprite_image_mask.y = self.sprite_coordinates[1]
	
	def __getstate__(self):
		"Exclude unpicklable attributes"
		out_dict = self.__dict__.copy()
		del out_dict['sprite']
		del out_dict['sprite_image_mask']
		return(out_dict)
	
	def __setstate__(self, dict):
		"Reconstitute unpicklable attributes"
		self.__dict__.update(dict)
		self.constitute_scaled_foreground_sprite()

class ForegroundStar(ScaledForegroundObject):
	'A named star and all its properties.'
	# this is B/W, and will be colored using pyglet's sprite.color
	image_file = 'star.png'

	colors = {
		'white': (255, 255, 255),
		'blue': (76, 177, 255),
		'green': (78, 255, 47),
		'yellow': (255, 255, 0),
		'orange': (255, 145, 0),
		'red': (220, 20, 60),
		'brown': (70, 22, 0),
	}

	def __init__(self, coordinates, name, type='yellow'):
		if (len(name) > 18) or (len(name) < 2):
			raise RangeException, "name must be 2 to 18 characters long"
		self.name = name

		if not self.colors.has_key(type):
			raise DataError, 'unknown star type: %s'%type
		self.type = type

		super(ForegroundStar, self).__init__(coordinates, self.image_file, self.stars_group)

		self.label_coordinates = self.sprite_coordinates
		self.constitute_foreground_star_and_decorations()

		self.worm_hole = None

	def constitute_foreground_star_and_decorations(self):
		'Allow these to be repickled'
		self.sprite.color = self.colors[self.type]

		self.label = pyglet.text.Label(self.name,
			font_name='Arial', font_size=10,
			# x and y will immediately be recalculated, but are required to initialize the label
			x=self.label_coordinates[0], y=self.label_coordinates[1],
			anchor_x='center', anchor_y='top', 
			batch=self.sprites_batch2, group=self.labels_group)

		marker_image = pyglet.resource.image('star_marker_animation.png')
		marker_image_seq = pyglet.image.ImageGrid(marker_image, 1, 24)
		for image in marker_image_seq:
			image.anchor_x = image.width // 2
			image.anchor_y = image.height // 2
		marker_animation = pyglet.image.Animation.from_image_sequence(marker_image_seq, 0.04)
		self.marker = pyglet.sprite.Sprite(marker_animation,
			x=self.sprite_coordinates[0], y=self.sprite_coordinates[1]
		)

		self.marker_visible = False

	def scale_coordinates(self, scaling_factor):
		"Set star's sprite and label coordinates based on a scaling factor."
		super(ForegroundStar, self).scale_coordinates(scaling_factor)

		# center label under sprite
		self.label_coordinates = (
			self.sprite.x-self.scaled_sprite_origin[0]+int(self.sprite.width/2),
			self.sprite.y-self.scaled_sprite_origin[1]-1
		)
		self.label.x = self.label_coordinates[0]
		self.label.y = self.label_coordinates[1]

		# recalculate marker
		self.marker.x = self.sprite.x
		self.marker.y = self.sprite.y
	
	def hide_marker(self):
		self.marker_visible = False
	
	def reveal_marker(self):
		self.marker_visible = True
	
	def __getstate__(self):
		"Exclude unpicklable attributes"
		out_dict = super(ForegroundStar, self).__getstate__()
		del out_dict['label']
		del out_dict['marker']
		return(out_dict)
	
	def __setstate__(self, dict):
		"Reconstitute unpicklable attributes"
		super(ForegroundStar, self).__setstate__(dict)
		self.constitute_foreground_star_and_decorations()

class BlackHole(ScaledForegroundObject):
	image_file = 'black_hole.png'

	def __init__(self, coordinates, initial_rotation=0):
		super(BlackHole, self).__init__(coordinates, self.image_file, self.black_holes_group)
		self.initial_rotation = initial_rotation
		self.sprite.rotation = self.initial_rotation
		self.sprite.scale = 0.1
		self.sprite_image_mask.rotation = self.initial_rotation
		self.sprite_image_mask.scale = 0.1
	
	def __setstate__(self, dict):
		"Reconstitute unpicklable attributes"
		super(BlackHole, self).__setstate__(dict)
		self.sprite.rotation = self.initial_rotation
		self.sprite.scale = 0.1
		self.sprite_image_mask.rotation = self.initial_rotation

class Nebula(ForegroundObject):
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

			self.constitute_lobe_sprite(lobe_info)

			self.lobes.append(lobe_info)

	def constitute_lobe_sprite(self, lobe):
		'Allow these to be repickled'
		image_id = '%s_%s_%d'%(self.primary_color, lobe['secondary'], lobe['image_id'])
		image = pyglet.resource.image(
			self.lobe_image_files[image_id]
		)
		lobe['sprite'] = pyglet.sprite.Sprite(
			image,
			# initial coordinates will never be used
			x=lobe['rendered_coordinates'][0], y=lobe['rendered_coordinates'][1]
		)
		lobe['sprite_origin'] = (image.width/2, image.height/2)
		lobe['sprite'].image.anchor_x = lobe['sprite_origin'][0]
		lobe['sprite'].image.anchor_y = lobe['sprite_origin'][1]
		lobe['sprite'].rotation = lobe['rotation']
		lobe['sprite'].batch = self.sprites_batch1
		lobe['sprite'].group = self.nebulae_group
		lobe['sprite'].scale = lobe['rendered_scale']

	def scale_coordinates_and_size(self, scaling_factor):
		"Set each lobe's coordinates and size based on a scaling factor."
		for lobe in self.lobes:
			lobe['rendered_coordinates'] = (
				(self.coordinates[0]+lobe['coordinates'][0])/scaling_factor,
				(self.coordinates[1]+lobe['coordinates'][1])/scaling_factor
			)
			lobe['rendered_scale'] = 1/scaling_factor*lobe['scale']
			lobe['sprite'].x = lobe['rendered_coordinates'][0]
			lobe['sprite'].y = lobe['rendered_coordinates'][1]
			lobe['sprite'].scale = lobe['rendered_scale']
	
	def __getstate__(self):
		"Exclude unpicklable attributes"
		out_dict = self.__dict__.copy()
		for lobe in out_dict['lobes']:
			del lobe['sprite']
		return(out_dict)
	
	def __setstate__(self, dict):
		"Reconstitute unpicklable attributes"
		self.__dict__.update(dict)
		for lobe in self.lobes:
			self.constitute_lobe_sprite(lobe)

class WormHole(All):
	'Worm holes; one maximum to any given star'

	def __init__(self, star1, star2):
		if not isinstance(star1, ForegroundStar) or not isinstance(star2, ForegroundStar):
			raise DataError, "both ends of wormholes must be foreground stars"

		if star1.worm_hole or star2.worm_hole:
			raise DataError, "wormhole endpoint stars may only be used once"

		self.endpoints = (star1, star2)
		star1.worm_hole = self
		star2.worm_hole = self

		self.vertices = [
			self.endpoints[0].sprite.x, self.endpoints[0].sprite.y,
			self.endpoints[1].sprite.x, self.endpoints[1].sprite.y
		]
		self.constitute_worm_hole_vertices()

		self.star1 = star1
		self.star2 = star2

	def constitute_worm_hole_vertices(self):
		'Allow these to be repickled'
		self.vertex_list = pyglet.graphics.vertex_list(
			2, 'v2f', 
			('c3B/static', 
				(
					0,0,96,
					0,0,96
				)
			)
		)
		self.vertex_list.vertices = self.vertices

		self.mask_vertex_list = pyglet.graphics.vertex_list(
			2, 'v2f', 'c3B'
		)
		self.mask_vertex_list.vertices = self.vertices

	def scale_coordinates(self):
		'When stars scale, their position changes, so update the wormhole vertex list'
		self.vertices = [
			self.endpoints[0].sprite.x, self.endpoints[0].sprite.y,
			self.endpoints[1].sprite.x, self.endpoints[1].sprite.y
		]
		self.vertex_list.vertices = self.vertices
		self.mask_vertex_list.vertices = self.vertices
	
	def hide_marker(self):
		self.star1.marker_visible = False
		self.star2.marker_visible = False
	
	def reveal_marker(self):
		self.star1.marker_visible = True
		self.star2.marker_visible = True
	
	def __getstate__(self):
		"Exclude unpicklable attributes"
		out_dict = self.__dict__.copy()
		del out_dict['vertex_list']
		del out_dict['mask_vertex_list']
		return(out_dict)
	
	def __setstate__(self, dict):
		"Reconstitute unpicklable attributes"
		self.__dict__.update(dict)
		self.constitute_worm_hole_vertices()

# doesn't make sense to call this standalone, so no __main__
