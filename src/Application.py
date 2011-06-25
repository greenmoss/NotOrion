#! python -O
from __future__ import division
import pyglet
import galaxy_objects
import galaxy

class DataContainer(object):
	"""A simple object to store all application data."""
	def __init__(self, init_galaxy_objects=None):
		# if we are passed no galaxy_objects, create defaults
		if init_galaxy_objects == None:
			self.galaxy_objects = galaxy_objects.All(
				# foreground stars
				[
					galaxy_objects.ForegroundStar((-1000, 900), 'Xi Bootis', 'red'),
					galaxy_objects.ForegroundStar((1225, 125), 'Alpha Centauri', 'green'),
					galaxy_objects.ForegroundStar((250, 250), 'Sol', 'blue'),
					galaxy_objects.ForegroundStar((0, 0), 'Tau Ceti', 'yellow'),
					galaxy_objects.ForegroundStar((-1125, -125), 'Eta Cassiopeiae', 'white'),
					galaxy_objects.ForegroundStar((750, -950), 'Delta Pavonis', 'brown'),
					galaxy_objects.ForegroundStar((-250, -250), 'Eridani', 'orange'),
					galaxy_objects.ForegroundStar((-90, -1070), 'Betelgeuse', 'orange'),
					galaxy_objects.ForegroundStar((100, -700), 'Rigel', 'red'),
					galaxy_objects.ForegroundStar((2000, -1100), 'Antares', 'white'),
					galaxy_objects.ForegroundStar((-1500, -525), 'Cygni', 'brown'),
					galaxy_objects.ForegroundStar((1300, 1100), 'Wolf', 'blue'),
					galaxy_objects.ForegroundStar((1200, -200), 'Lalande', 'red'),
					galaxy_objects.ForegroundStar((-1327, 1200), 'Luyten', 'blue'),
					galaxy_objects.ForegroundStar((0, 920), 'Ross', 'white'),
					galaxy_objects.ForegroundStar((-1025, -1250), 'Lacaille', 'green'),
					galaxy_objects.ForegroundStar((-800, 630), 'Aquarii', 'yellow'),
					galaxy_objects.ForegroundStar((-490, -525), 'Procyon', 'orange'),
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
					galaxy_objects.BlackHole((300, 1000), 120),
					galaxy_objects.BlackHole((-1300, -1500)),
					galaxy_objects.BlackHole((800, -500), 225),
					galaxy_objects.BlackHole((-200, 1120), 55),
				],
				# nebulae
				[
					galaxy_objects.Nebula((100, -700), 'red', [
						(0, 1, (135, -25), 0, 1.2), 
						(1, 2, (-120, 46), 148, 0.9),
						(1, 1, (-46, -55), 223, 1.05),
						(0, 2, (3, 14), 321, 1.63),
					]),
					galaxy_objects.Nebula((1225, 900), 'blue', [
						(1, 1, (35, -25), 0, 1.5), 
						(0, 2, (-20, 46), 45, 0.45),
						(0, 1, (-46, -55), 88, 0.78),
						(1, 2, (0, 5), 130, 1.1)
					]),
					galaxy_objects.Nebula((-900, 200), 'green', [
						(0, 1, (35, -25), 129, 1.95), 
						(1, 2, (-120, 46), 94, 1.22),
						(0, 1, (-146, -55), 210, 1.3),
						(0, 2, (36, 65), 290, 0.78)
					]),
					galaxy_objects.Nebula((-1230, 450), 'blue', [
						(1, 2, (125, -135), 25, 2.0), 
						(1, 2, (-10, 16), 95, 1.5),
						(0, 1, (-26, -25), 0, 1.88),
						(0, 1, (146, 35), 168, 1.68)
					]),
				],
				# worm holes
				[ (4,1), (2,6), (5,8), (0,7) ]
			)
		else:
			self.galaxy_objects = galaxy_objects

class Application(object):
	"""Controller class for all game objects."""
	def __init__(self, data):
		# must be of type DataContainer
		self.data = data

		galaxy_window = galaxy.Window(1024, 768, self.data)

if __name__ == "__main__":
	application = Application(DataContainer())
	pyglet.app.run()
