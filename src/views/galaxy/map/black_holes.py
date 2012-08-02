import pyglet

from globals import g
import fixed_size_object

class BlackHoles(object):
	pyglet_ordered_group = pyglet.graphics.OrderedGroup(3)
	sprites_batch = pyglet.graphics.Batch() 

	def __init__(self):
		self.black_holes = {}
		for black_hole in g.galaxy.black_holes:
			self.black_holes[black_hole] = BlackHole(black_hole, BlackHoles.sprites_batch)
	
	def draw(self):
		self.sprites_batch.draw()
	
	def set_scale(self, scale):
		for black_hole_ref, black_hole_object in self.black_holes.iteritems():
			black_hole_object.scale_coordinates(scale)

class BlackHole(fixed_size_object.AnimatedObject):
	'The methods and attributes needed to display a black hole within the galaxy window.'

	image_file_name = 'black_hole_animation.png'

	def __init__(self, black_hole, sprites_batch):
		self.physical_black_hole = black_hole

		super(BlackHole, self).__init__(self.physical_black_hole.coordinates)
		self.coordinates = self.physical_black_hole.coordinates

		self.sprite.batch = sprites_batch

	def scale_coordinates(self, scaling_factor):
		"Set black hole's sprite coordinates based on a scaling factor."
		super(BlackHole, self).scale_coordinates(scaling_factor)
