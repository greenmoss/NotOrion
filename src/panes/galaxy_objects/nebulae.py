import pyglet

from globals import g

class Nebulae(object):
	pyglet_sprites_batch = pyglet.graphics.Batch() 

	def __init__(self):
		self.nebulae = []
		for nebula in g.galaxy.nebulae:
			self.nebulae.append( Nebula(nebula, Nebulae.pyglet_sprites_batch) )
	
	def draw(self):
		self.pyglet_sprites_batch.draw()
	
	def set_scale(self, scale):
		for nebula in self.nebulae:
			nebula.scale_coordinates_and_size(scale)

class Nebula(object):

	def __init__(self, model, pyglet_sprites_batch):
		self.nebula_model = model
		self.pyglet_sprites_batch = pyglet_sprites_batch
		self.create_lobe_sprites()

	def create_lobe_sprites(self):
		self.lobe_sprites = {}
		for lobe_model in self.nebula_model.lobes:
			image = lobe_model.pyglet_image_resource
			sprite = pyglet.sprite.Sprite(
				image,
				# initial coordinates will never be used
				x=0, y=0
			)
			sprite_origin = (image.width/2, image.height/2)
			sprite.image.anchor_x = sprite_origin[0]
			sprite.image.anchor_y = sprite_origin[1]
			sprite.rotation = lobe_model.rotation
			sprite.batch = self.pyglet_sprites_batch
			sprite.scale = lobe_model.scale
			self.lobe_sprites[lobe_model] = sprite

	def scale_coordinates_and_size(self, scaling_factor):
		"Set each lobe's coordinates and size based on a scaling factor."
		for lobe_model, lobe_sprite in self.lobe_sprites.iteritems():
			lobe_sprite.x = (self.nebula_model.coordinates[0] + lobe_model.coordinates[0])/scaling_factor
			lobe_sprite.y = (self.nebula_model.coordinates[1] + lobe_model.coordinates[1])/scaling_factor
			lobe_sprite.scale = 1/scaling_factor*lobe_model.scale
