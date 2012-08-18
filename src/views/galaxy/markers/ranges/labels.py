import logging
logger = logging.getLogger(__name__)

import pyglet
from pyglet.gl import *

import views.galaxy.markers.ranges

class Label(object):
	batch = pyglet.graphics.Batch()
	# do not show the label if our marker line is shorter than this:
	minimum_distance = 25
	box_color = (0,0,0,200)

	def __init__(self, ranges):
		self.ranges = ranges
		self.color = views.galaxy.markers.ranges.Ranges.color
		self.hide()
		self.pyglet_label= pyglet.text.Label(
			"",
			x=0,
			y=0,
			anchor_x='center',
			anchor_y='bottom',
			color=(self.color[0], self.color[1], self.color[2], 255),
			font_size=10,
			batch=Label.batch
		)

		# shaded masking box behind cursor label, to make text easier to read
		self.mask_vertex_list = pyglet.graphics.vertex_list( 4,
			'v2f',
			('c4B/static', Label.box_color*4)
		)
	
	def draw(self):
		if not self.visible:
			return

		glPushAttrib(GL_ENABLE_BIT)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		self.mask_vertex_list.draw(pyglet.gl.GL_QUADS)
		glPopAttrib()

		self.batch.draw()
	
	def hide(self):
		self.visible = False
	
	def show(self):
		self.visible = True
	
	def set_label(self, x, y):
		distance = self.ranges.model_distance()
		parsecs_float = round(distance/100, 1)
		distance = parsecs_float if parsecs_float < 1 else int(parsecs_float)
		unit = 'parsec' if distance is 1 else 'parsecs'

		self.pyglet_label.x = x
		self.pyglet_label.y = y + 2 # raise the label further above the cursor
		self.pyglet_label.text = "%s %s"%(distance, unit)
	
	def set_box(self):
		box_top = self.pyglet_label.y + self.pyglet_label.content_height
		box_bottom = self.pyglet_label.y
		box_right = self.pyglet_label.x + (self.pyglet_label.content_width/2)
		box_left = self.pyglet_label.x - (self.pyglet_label.content_width/2)
		self.mask_vertex_list.vertices = [
			box_right, box_bottom,
			box_right, box_top,
			box_left, box_top,
			box_left, box_bottom
		]

	def move(self, x, y):
		self.hide()

		window_distance = self.ranges.window_distance()
		if not window_distance:
			return
		if window_distance < Label.minimum_distance:
			return

		self.set_label(x, y)
		self.set_box()

		self.show()
