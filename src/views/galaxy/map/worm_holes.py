import logging
logger = logging.getLogger(__name__)

import pyglet

from globals import g

class WormHoles(object):

	def __init__(self, star_views):
		self.star_views = star_views
		self.worm_holes = []

		for worm_hole_model in g.galaxy.worm_holes:
			self.worm_holes.append( 
				WormHole(
					self.star_views.stars[worm_hole_model.star1.name],
					self.star_views.stars[worm_hole_model.star2.name]
				)
			)
	
	def draw(self):
		for worm_hole in self.worm_holes:
			worm_hole.vertex_list.draw(pyglet.gl.GL_LINES)
	
	def set_scale(self, scale):
		for worm_hole in self.worm_holes:
			worm_hole.set_endpoints()

class WormHole(object):
	color = (0,0,250)

	def __init__(self, star1_view, star2_view):
		self.star1_view = star1_view
		self.star2_view = star2_view
		self.vertex_list = pyglet.graphics.vertex_list(
			2, 'v2f', 
			('c3B/static', WormHole.color*2)
		)
		self.endpoint1_vertices_list = []
		self.endpoint2_vertices_list = []
	
	def __repr__(self):
		return "map view: %s <-> %s"%(self.star1_view.physical_star.name,self.star2_view.physical_star.name)
	
	def set_endpoints(self):
		self.endpoint1_vertices_list = [
			self.star1_view.sprite.x,
			self.star1_view.sprite.y
		]
		#logger.debug("map endpoint1 vertices: %s", self.endpoint1_vertices_list)
		self.endpoint2_vertices_list = [
			self.star2_view.sprite.x,
			self.star2_view.sprite.y
		]
		self.vertex_list.vertices = \
			self.endpoint1_vertices_list + self.endpoint2_vertices_list
