import pyglet

from globals import g
import fixed_size_object
import panes.galaxy

class Stars(object):
	pyglet_ordered_group = pyglet.graphics.OrderedGroup(2)
	sprites_batch = pyglet.graphics.Batch() 

	def __init__(self):
		self.stars = {}
		for physical_star in g.galaxy.stars:
			self.stars[physical_star.name] = Star(physical_star, Stars.sprites_batch)
	
	def draw(self):
		self.sprites_batch.draw()
	
	def set_scale(self, scale):
		for star_name, star_object in self.stars.iteritems():
			star_object.scale_coordinates(scale)

class Star(fixed_size_object.StaticImageObject):
	'The methods and attributes needed to display a star within the galaxy window.'

	# The base image is black and white
	image_file_name = 'star.png'

	# ...and will be colored using pyglet's sprite.color using these RGB values:
	colors = {
		'white': (255, 255, 255),
		'blue': (76, 177, 255),
		'green': (78, 255, 47),
		'yellow': (255, 255, 0),
		'orange': (255, 145, 0),
		'red': (220, 20, 60),
		'brown': (70, 22, 0),
	}

	pyglet_ordered_group = pyglet.graphics.OrderedGroup(2)
	pyglet_labels_ordered_group = pyglet.graphics.OrderedGroup(3)

	def __init__(self, physical_star, sprites_batch):
		self.physical_star = physical_star

		if not Star.colors.has_key(self.physical_star.type):
			raise DataError, 'unable to find color for star type: %s'%self.physical_star.type

		super(Star, self).__init__(self.physical_star.coordinates)
		self.coordinates = self.physical_star.coordinates

		self.sprite.color = Star.colors[self.physical_star.type]
		self.sprite.batch = sprites_batch

		self.label = pyglet.text.Label(self.physical_star.name,
			font_name='Arial', font_size=10,
			# x and y coordinates of label will immediately be recalculated, but are required to initialize the label
			x=0, y=0,
			anchor_x='center', anchor_y='top', 
			batch=sprites_batch, 
			group=self.pyglet_labels_ordered_group)

		marker_image = pyglet.resource.image('star_marker_animation.png')
		marker_image_seq = pyglet.image.ImageGrid(marker_image, 1, 24)
		for image in marker_image_seq:
			image.anchor_x = image.width // 2
			image.anchor_y = image.height // 2
		marker_animation = pyglet.image.Animation.from_image_sequence(marker_image_seq, 0.04)
		self.marker = pyglet.sprite.Sprite(marker_animation,
			x=self.sprite_coordinates[0], y=self.sprite_coordinates[1]
		)

		self.marker_visible = False
	
	def reset_marker(self):
		"The marker color might have been changed; reset it to its default state."
		self.marker.color = (255,255,255)

	def scale_coordinates(self, scaling_factor):
		"Set star's sprite and label coordinates based on a scaling factor."
		super(Star, self).scale_coordinates(scaling_factor)

		# center label under sprite
		self.label.x = self.sprite.x-self.scaled_sprite_origin[0]+int(self.sprite.width/2)
		self.label.y = self.sprite.y-self.scaled_sprite_origin[1]-1

		# recalculate marker
		self.marker.x = self.sprite.x
		self.marker.y = self.sprite.y
	
	def hide_marker(self):
		self.marker_visible = False
	
	def reveal_marker(self):
		self.marker_visible = True
