import unittest

# path to our code (in unix): "../src"
import os
import sys
sys.path.append(
	os.path.join(
		os.path.dirname(os.path.abspath( __file__ )), os.path.pardir, 'src'
	)
)
import application
import game_configuration
import galaxy
import pyglet

class TestApplication(unittest.TestCase):

	# Not sure how much this actually proves, so for now it's just a commented-out concept
	"""
	def testSuccessfulExecution(self):
		"Application should launch and then successfully exit."
		data = application.DataContainer()
		game_configuration.Choose(data, difficulty="Beginner")
		data.galaxy_window = galaxy.WindowContainer(data)
		data.galaxy_window.window.height = 400
		data.galaxy_window.window.width = 400

		def exit(dt):
			pyglet.app.exit()

		pyglet.clock.schedule_interval(exit, 0.01)
		pyglet.app.run()

		# can't assert anything here, other than non-zero exit?
	"""

if __name__ == "__main__":
	unittest.main()
