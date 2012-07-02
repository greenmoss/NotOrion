import pyglet

from globals import g
import star

class Stars(object):
	pyglet_ordered_group = pyglet.graphics.OrderedGroup(2)
	sprites_batch = pyglet.graphics.Batch() 

	def __init__(self):
		self.stars = {}
		for physical_star in g.galaxy.stars:
			self.stars[physical_star.name] = star.Star(physical_star, Stars.sprites_batch)
	
	def draw(self):
		self.sprites_batch.draw()
	
	def set_scale(self, scale):
		for star_name, star_object in self.stars.iteritems():
			star_object.scale_coordinates(scale)
