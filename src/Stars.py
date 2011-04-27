import pyglet

class BackgroundStar(object):
	"""A simplified star for the background, to be drawn only as a point source"""

	def __init__(self, coordinates, color):
		self.coordinates = (coordinates[0], coordinates[1], -100)
		self.color = color

class NamedStar(object):
	"""A named star and all its properties."""
	pyglet.resource.path = ['../images']
	pyglet.resource.reindex()

	def __init__(self, coordinates, name, image=None):
		if not (-10000 < coordinates[0] < 10000) or not (-10000 < coordinates[1] < 10000):
			raise Exception, "coordinates must be between -10000 and 10000"
		if (len(name) > 15) or (len(name) < 3):
			raise Exception, "name must be between 3 and 15 characters long"

		if image == None:
			image = pyglet.resource.image('star.png')
		self.sprite = pyglet.sprite.Sprite(image,
			x=coordinates[0], y=coordinates[1]
		)
		self.sprite.scale = 0.2
		self.coordinates = coordinates
		self.label = pyglet.text.Label(name,
			font_name='Arial', font_size=15,
			x=coordinates[0], y=coordinates[1],
			anchor_x='center', anchor_y='top')
		self.name = name

	def scale(self, scaling_factor):
		"""Set star's sprite and label coordinates based on a scaling factor."""
		self.sprite.x = self.coordinates[0]*scaling_factor
		self.sprite.y = self.coordinates[1]*scaling_factor
		# manually center label under sprite, which can only be anchored bottom/left :(
		self.label.x = self.sprite.x+(self.sprite.width/2)
		self.label.y = self.sprite.y

class All(object):
	"""All stars are referenced from this object."""

	def __init__(self, named_stars, background_stars):
		self.named = named_stars

		# find bounding lines that contain all named stars
		(self.left_bounding_x, self.right_bounding_x, self.top_bounding_y, self.bottom_bounding_y) = [0, 0, 0, 0]
		for star in self.named:
			if star.coordinates[0] < self.left_bounding_x:
				self.left_bounding_x = star.coordinates[0]
			elif star.coordinates[0] > self.right_bounding_x:
				self.right_bounding_x = star.coordinates[0]
			if star.coordinates[1] < self.bottom_bounding_y:
				self.bottom_bounding_y = star.coordinates[1]
			elif star.coordinates[1] > self.top_bounding_y:
				self.top_bounding_y = star.coordinates[1]

		self.background = background_stars

		# create vertex/color list for all background stars
		# will be invoked as background_vertex_list.draw(pyglet.gl.GL_POINTS)
		self.background_star_vertices = []
		self.background_star_colors = []
		for background_star in self.background:
			[self.background_star_vertices.append(vertex) for vertex in background_star.coordinates]
			[self.background_star_colors.append(vertex) for vertex in background_star.color]
		self.background_vertex_list = pyglet.graphics.vertex_list(
			len(self.background),
			('v3i/static', self.background_star_vertices),
			('c3B/static', self.background_star_colors)
		)
	
	def draw_scaled(self, scaling_factor):
		"""Draw all named stars and labels, scaled appropriately"""
		for star in self.named:
			star.scale(scaling_factor)
			star.sprite.draw()
			star.label.draw()

if __name__ == "__main__":
	"nothing to do here unless called by something else"
	pass
