#! python -O
from __future__ import division
import pyglet
import galaxy_objects
import galaxy

class DataContainer(object):
	"""A simple object to store all application data."""
	def __init__(self, stars=None):
		# if we are passed no stars, create defaults
		if stars == None:
			self.stars = galaxy_objects.All(
				# foreground stars
				[
					galaxy_objects.ForegroundStar((-1000, 900), 'Xi Bootis', 'red'),
					galaxy_objects.ForegroundStar((1225, 125), 'Alpha Centauri', 'green'),
					galaxy_objects.ForegroundStar((250, 250), 'Sol', 'blue'),
					galaxy_objects.ForegroundStar((0, 0), 'Tau Ceti', 'yellow'),
					galaxy_objects.ForegroundStar((-1125, -125), 'Eta Cassiopeiae', 'white'),
					galaxy_objects.ForegroundStar((750, -950), 'Delta Pavonis', 'brown'),
					galaxy_objects.ForegroundStar((-250, -250), 'Eridani', 'orange'),
					#galaxy_objects.ForegroundStar((-90, -1070), 'Betelgeuse', 'orange'),
					#galaxy_objects.ForegroundStar((90, 1070), 'Rigel', 'red'),
				],
				# background stars
				[
					galaxy_objects.BackgroundStar((0, 0), (0, 0, 255)),
					galaxy_objects.BackgroundStar((250, 250), (0, 255, 0)),
					galaxy_objects.BackgroundStar((-250, -250), (255, 0, 0)),
					galaxy_objects.BackgroundStar((10, -100), (228, 255, 255)),
					galaxy_objects.BackgroundStar((100, 100), (255, 255, 228)),
					galaxy_objects.BackgroundStar((-200, -300), (255, 228, 255)),
					galaxy_objects.BackgroundStar((-160, 228), (228, 255, 255)),
					galaxy_objects.BackgroundStar((589, -344), (228, 255, 255)),
					galaxy_objects.BackgroundStar((-420, -300), (255, 255, 228)),
					galaxy_objects.BackgroundStar((-400, 299), (255, 228, 255)),
					galaxy_objects.BackgroundStar((589, -344), (228, 255, 255)),
					galaxy_objects.BackgroundStar((420, -300), (255, 255, 228)),
					galaxy_objects.BackgroundStar((400, 199), (255, 228, 255)),
				],
				# black holes
				[
					galaxy_objects.BlackHole((300, 1000)),
					galaxy_objects.BlackHole((-1300, -1500)),
				#	galaxy_objects.BlackHole((800, -500)),
				#	galaxy_objects.BlackHole((-200, 1120)),
				]
			)
		else:
			self.stars = stars

class Application(object):
	"""Controller class for all game objects."""
	def __init__(self, data):
		# must be of type DataContainer
		self.data = data

		galaxy_window = galaxy.Window(1024, 768, self.data)

if __name__ == "__main__":
	application = Application(DataContainer())
	pyglet.app.run()
