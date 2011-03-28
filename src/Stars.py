import pyglet

class Star(object):
	"""A Star and all its properties."""

	def __init__(self, image, coordinates, name):
		self.sprite = pyglet.sprite.Sprite(image)
		self.sprite.scale = 0.2
		self.sprite.x = coordinates[0]
		self.sprite.y = coordinates[1]
		self.coordinates = coordinates
		self.label = pyglet.text.Label(
			name,
			font_name='Arial',
			font_size=15,
			x=coordinates[0], y=coordinates[1],
			anchor_x='center', anchor_y='top')
		self.name = name

	def scale(self, scaling_factor):
		"""Set star's sprite and label coordinates based on a scaling factor."""
		self.sprite.x = self.coordinates[0] * scaling_factor
		self.sprite.y = self.coordinates[1] * scaling_factor
		# for some reason, the labels are *not* centered under the star
		# so as a dumb, hopefully-temporary workaround, manually add an offset of 8.0
		self.label.x = (self.coordinates[0] * scaling_factor) + 8.0
		self.label.y = self.coordinates[1] * scaling_factor

class All(object):
	"""All stars are referenced from this object."""

	def __init__(self):
		pyglet.resource.path = ['../images']
		pyglet.resource.reindex()
		star_image = pyglet.resource.image('star.png')

		self.all = [
			Star(star_image, (10, 10), 'Sol'),
			Star(star_image, (5, 5), 'Alpha Centauri'),
			Star(star_image, (0, 0), 'Tau Ceti'),
			Star(star_image, (-5, -5), 'Eta Cassiopeiae'),
			Star(star_image, (-10, -10), 'Eridani'),
			Star(star_image, (10, -10), 'Delta Pavonis'),
			Star(star_image, (-10, 10), 'Xi Bootis'),
		]
	
	def draw_scaled(self, scaling_factor):
		"""Draw all stars and labels, scaled appropriately"""
		for star in self.all:
			star.scale(scaling_factor)
			star.sprite.draw()
			star.label.draw()

if __name__ == "__main__":
	All()
