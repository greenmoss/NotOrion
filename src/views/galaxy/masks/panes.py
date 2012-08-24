import logging
logger = logging.getLogger(__name__)

import pyglet
from pyglet.gl import *

class Panes(object):
	"""Masks for all panes within the galaxy window."""

	def __init__(self, mask_state):
		logger.debug('binding mask panes')
		self.state = mask_state.state
		self.masks = []
		self.masks.append(StarSystem(self.state.star_system))
	
	def handle_draw(self):
		for mask in self.masks:
			mask.handle_draw()

class Mask(object):

	def __init__(self):
		self.type = 'pane'
		self.vertex_list = pyglet.graphics.vertex_list( 4, 'v2f', 'c3B' )
	
	def set_color(self, color):
		self.vertex_list.colors = color*4

class StarSystem(Mask):
	def __init__(self, star_system_view):
		self.source_object = star_system_view
		super(StarSystem, self).__init__()
	
	def handle_draw(self):
		if not self.source_object.visible:
			return
		corners = self.source_object.corners
		self.vertex_list.vertices = (
			corners['left'], corners['top'],
			corners['right'], corners['top'],
			corners['right'], corners['bottom'],
			corners['left'], corners['bottom']
		)
		self.source_object.drawing_origin_to_lower_left()
		self.vertex_list.draw(pyglet.gl.GL_QUADS)
