import pyglet

class BackgroundStar(object):
	"""A simplified star for the background, to be drawn only as a point source"""

	def __init__(self, coordinates, color):
		self.coordinates = coordinates
		self.color = color

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
		self.sprite.x = self.coordinates[0]*scaling_factor
		self.sprite.y = self.coordinates[1]*scaling_factor
		# for some reason, the labels are *not* centered under the star
		# so as a dumb, hopefully-temporary workaround, manually add an offset of 8.0
		self.label.x = (self.coordinates[0]*scaling_factor)+8.0
		self.label.y = self.coordinates[1]*scaling_factor

class All(object):
	"""All stars are referenced from this object."""

	def __init__(self):
		pyglet.resource.path = ['../images']
		pyglet.resource.reindex()
		star_image = pyglet.resource.image('star.png')

		self.named = [
			Star(star_image, (0, 0), 'Tau Ceti'),
			Star(star_image, (5, 5), 'Alpha Centauri'),
			Star(star_image, (-5, -5), 'Eta Cassiopeiae'),
			Star(star_image, (10, 10), 'Sol'),
			Star(star_image, (-10, -10), 'Eridani'),
			Star(star_image, (10, -10), 'Delta Pavonis'),
			Star(star_image, (-10, 10), 'Xi Bootis'),
		]
		self.background = [
			BackgroundStar((1, 2), (200, 255, 255)),
			BackgroundStar((-5, 3), (255, 255, 200)),
			BackgroundStar((4, -1), (255, 200, 255)),
			BackgroundStar((2, -3), (255, 255, 255)),
			BackgroundStar((0, 1), (215, 255, 255)),
			BackgroundStar((-4, 0), (255, 255, 215)),
			BackgroundStar((-2, -7), (255, 215, 255)),
			BackgroundStar((1, 7), (255, 255, 255)),
			BackgroundStar((-6, -5), (228, 255, 255)),
			BackgroundStar((2, -6), (255, 255, 228)),
			BackgroundStar((-8, 4), (255, 215, 255)),
		]
	
	def draw_scaled(self, scaling_factor):
		"""Draw all named stars and labels, scaled appropriately"""
		for star in self.named:
			star.scale(scaling_factor)
			star.sprite.draw()
			star.label.draw()
	
	def draw_background(self):
		"""Draw background star/point sources"""
		for star in self.background:
			pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,
				('v3i', (star.coordinates[0], star.coordinates[1], -100)),
				('c3B', (star.color[0], star.color[1], star.color[2]))
			)

if __name__ == "__main__":
	All()
