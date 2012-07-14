import pyglet

from globals import g

class WormHoles(object):
	def __init__(self, star_views):
		self.worm_hole_vertex_lists = {}
		self.star_views = star_views

		for worm_hole_model in g.galaxy.worm_holes:
			self.worm_hole_vertex_lists[worm_hole_model] = pyglet.graphics.vertex_list(
				2, 'v2f', 
				('c3B/static', 
					(
						0,0,96,
						0,0,96
					)
				)
			)
	
	def draw(self):
		for worm_hole_vertex_list in self.worm_hole_vertex_lists.values():
			worm_hole_vertex_list.draw(pyglet.gl.GL_LINES)
	
	def set_scale(self, scale):
		for worm_hole_ref, worm_hole_vertex_list in self.worm_hole_vertex_lists.iteritems():
			worm_hole_vertex_list.vertices = [
				self.star_views.stars[worm_hole_ref.star1.name].sprite.x,
				self.star_views.stars[worm_hole_ref.star1.name].sprite.y,
				self.star_views.stars[worm_hole_ref.star2.name].sprite.x,
				self.star_views.stars[worm_hole_ref.star2.name].sprite.y
			]
