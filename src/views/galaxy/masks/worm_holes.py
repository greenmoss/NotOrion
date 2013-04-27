import logging
logger = logging.getLogger(__name__)

import pyglet

from globals import g

class WormHoles(object):
    """Masks for all map worm hole objects."""

    def __init__(self, map_worm_holes):
        logger.debug('binding mask worm_holes to map_worm_holes')
        self.map_worm_holes = map_worm_holes
        self.masks = []

        for map_worm_hole in map_worm_holes.worm_holes:
            self.masks.append( Mask(map_worm_hole) )

    def handle_draw(self):
        for mask in self.masks:
            mask.vertex_list.draw(pyglet.gl.GL_LINES)
    
    def set_center(self):
        for mask in self.masks:
            mask.set_vertices()

    def set_scale(self):
        for mask in self.masks:
            mask.set_vertices()

class Mask(object):
    def __init__(self, map_object):
        self.source_object = map_object
        self.type = 'map'
        self.vertex_list = pyglet.graphics.vertex_list( 2, 'v2f', 'c3B' )
    
    def __repr__(self):
        return "%s <-> %s"%(
            self.source_object.star1_view.physical_star.name,
            self.source_object.star2_view.physical_star.name
        )

    def set_color(self, color):
        self.color = color
        self.vertex_list.colors = color * 2
    
    def set_vertices(self):
        endpoint1_vertices = list(self.source_object.endpoint1_vertices_list)
        endpoint2_vertices = list(self.source_object.endpoint2_vertices_list)
        self.vertex_list.vertices = endpoint1_vertices + endpoint2_vertices
