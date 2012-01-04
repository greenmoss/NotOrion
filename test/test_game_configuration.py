import unittest
import pyglet

# path to our code (in unix): "../src"
import os
import sys
sys.path.append(
	os.path.join(
		os.path.dirname(os.path.abspath( __file__ )), os.path.pardir, 'src'
	)
)
import application
paths = application.set_paths()

import game_configuration

class TestChoose(unittest.TestCase):
	data = application.DataContainer()
	data.paths = paths

	def testPassedDifficultyHasNoWindow(self):
		"When we are passed a difficulty, we should not show a setup window."
		choose = game_configuration.Choose(self.data, 'Easy')
		self.assertEqual(choose.setup_window, None)

	def testNoDifficultyHasWindow(self):
		"When we are not passed a difficulty, we should show a setup window."
		choose = game_configuration.Choose(self.data)
		self.assertIsInstance(choose.setup_window, pyglet.window.Window)
		choose.setup_window.close()

	def testInvalidChosenDifficulty(self):
		"If we are passed an invalid difficulty, we shoud raise an exception."
		self.assertRaises(game_configuration.DataError, game_configuration.Choose, self.data, 'boo')
	
if __name__ == "__main__":
	unittest.main()

