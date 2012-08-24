import struct
import logging
logger = logging.getLogger(__name__)

import pyglet

from globals import g

class Stars(object):
	"""Masks for all map star objects."""

	def __init__(self, map_view):
		logger.debug('binding mask stars to map_view')
		self.map_view = map_view
		self.masks = []
		self.sprites_batch = pyglet.graphics.Batch()

		# stars on map share the same sprite, so retrieve any star from the map
		source_sprite = self.map_view.stars.values()[0].sprite
		self.mask_image = self.generate_sprite_image_mask(source_sprite)

		for map_star_name, map_star_object in self.map_view.stars.iteritems():
			self.masks.append( Mask(map_star_object, self.mask_image, self.sprites_batch) )

	def generate_sprite_image_mask(self, source_sprite):
		mask = pyglet.image.create(source_sprite.image.width, source_sprite.image.height)
		image_data = source_sprite.image.get_image_data()
		pixel_bytes = image_data.get_data('RGBA', image_data.width * 4)
		mask_bytes = ''
		for position in range(int(len(pixel_bytes)/4)):
			bytes = struct.unpack_from('4c', pixel_bytes, 4*position)

			# alpha channel is mostly opaque, set alpha to 255
			if ord(bytes[3]) > 127:
				mask_bytes += '\xff\xff\xff\xff'

			# alpha channel is fully transparent, set alpha to 0
			else:
				mask_bytes += '\xff\xff\xff\x00'
		mask.image_data.set_data('RGBA', image_data.width * 4, mask_bytes)
		return mask
	
	def handle_draw(self):
		self.sprites_batch.draw()
	
	def set_center(self):
		for mask in self.masks:
			mask.set_coordinates()

	def set_scale(self):
		for mask in self.masks:
			mask.set_coordinates()

class Mask(object):
	def __init__(self, map_object, mask_image, sprites_batch):
		self.source_object = map_object
		self.type = 'map'

		self.sprite = pyglet.sprite.Sprite(
			mask_image.texture,
			self.source_object.coordinates[0],
			self.source_object.coordinates[1],
			batch = sprites_batch
		)
		self.sprite.image.anchor_x = self.source_object.sprite.image.anchor_x
		self.sprite.image.anchor_y = self.source_object.sprite.image.anchor_y
	
	def __repr__(self):
		return self.source_object.physical_star.name
	
	def set_color(self, color):
		self.color = color
		self.sprite.color = color
	
	def set_coordinates(self):
		self.sprite.x = self.source_object.sprite.x
		self.sprite.y = self.source_object.sprite.y
