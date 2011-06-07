#! python -O
from __future__ import division
import pyglet
import Stars
import Galaxy

class DataContainer(object):
	"""A simple object to store all application data."""
	def __init__(self, stars=None):
		# if we are passed no stars, create defaults
		if stars == None:
			pyglet.resource.path = ['../images']
			pyglet.resource.reindex()
			star_image = pyglet.resource.image('star.png')

			self.stars = Stars.All(
				[
					Stars.NamedStar((-1000, 900), 'Xi Bootis', star_image),
					Stars.NamedStar((1225, 125), 'Alpha Centauri', star_image),
					Stars.NamedStar((250, 250), 'Sol', star_image),
					Stars.NamedStar((0, 0), 'Tau Ceti', star_image),
					Stars.NamedStar((-1125, -125), 'Eta Cassiopeiae', star_image),
					Stars.NamedStar((750, -950), 'Delta Pavonis', star_image),
					Stars.NamedStar((-250, -250), 'Eridani', star_image),
				],
				[
					Stars.BackgroundStar((0, 0), (0, 0, 255)),
					Stars.BackgroundStar((250, 250), (0, 255, 0)),
					Stars.BackgroundStar((-250, -250), (255, 0, 0)),
					Stars.BackgroundStar((10, -100), (228, 255, 255)),
					Stars.BackgroundStar((100, 100), (255, 255, 228)),
					Stars.BackgroundStar((-200, -300), (255, 228, 255)),
					Stars.BackgroundStar((-160, 228), (228, 255, 255)),
					Stars.BackgroundStar((589, -344), (228, 255, 255)),
					Stars.BackgroundStar((-420, -300), (255, 255, 228)),
					Stars.BackgroundStar((-400, 299), (255, 228, 255)),
					Stars.BackgroundStar((589, -344), (228, 255, 255)),
					Stars.BackgroundStar((420, -300), (255, 255, 228)),
					Stars.BackgroundStar((400, 199), (255, 228, 255)),
				])
		else:
			self.stars = stars

class Application(object):
	"""Controller class for all game objects."""
	data = None

	def __init__(self, data):
		# must be of type DataContainer
		self.data = data

		galaxy_window = Galaxy.Window(1024, 768, self.data)

if __name__ == "__main__":
	application = Application(DataContainer())
	pyglet.app.run()
