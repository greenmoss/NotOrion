from __future__ import division

import pyglet

from globals import g
import views.galaxy

class Stars(object):
	def __init__(self, map_view):
		self.map_view = map_view
		self.markers = {}
		self.visible_batch = pyglet.graphics.Batch()
		self.invisible_batch = pyglet.graphics.Batch()

		# configure marker image animation
		image = pyglet.resource.image('star_marker_animation.png')
		image_seq = pyglet.image.ImageGrid(image, 1, 24)
		for image in image_seq:
			image.anchor_x = image.width // 2
			image.anchor_y = image.height // 2
		animation = pyglet.image.Animation.from_image_sequence(image_seq, 0.04)

		for map_star_name, map_star_object in self.map_view.stars.iteritems():
			self.markers[map_star_name] = Marker(
				map_star_object, animation, self.visible_batch, self.invisible_batch
			)

		self.under_cursor = {}

	def set_coordinates(self):
		for star_name, map_object in self.under_cursor.iteritems():
			self.markers[star_name].hide()

	def set_over_objects(self, objects_under_cursor):
		under_cursor = {}

		for map_object in objects_under_cursor:
			if not type(map_object) == views.galaxy.map.objects.stars.Star:
				continue
			star_name = map_object.physical_star.name
			under_cursor[star_name] = map_object
			self.markers[star_name].show()

		for star_name, map_object in self.under_cursor.iteritems():
			if under_cursor.has_key(star_name):
				continue
			self.markers[star_name].hide()

		self.under_cursor = under_cursor
	
	def draw(self):
		self.visible_batch.draw()

class Marker(object):
	def __init__(self, map_object, animation, visible_batch, invisible_batch):
		self.map_object = map_object
		self.invisible_batch = invisible_batch
		self.visible_batch = visible_batch

		self.sprite = pyglet.sprite.Sprite(
			animation,
			self.map_object.sprite.x,
			self.map_object.sprite.y
		)

		self.hide()
	
	def show(self):
		self.visible = True
		self.set_coordinates()
		self.sprite.batch = self.visible_batch
	
	def hide(self):
		self.visible = False
		self.sprite.batch = self.invisible_batch
	
	def set_coordinates(self):
		if not self.visible:
			return
		self.sprite.x = self.map_object.sprite.x
		self.sprite.y = self.map_object.sprite.y
