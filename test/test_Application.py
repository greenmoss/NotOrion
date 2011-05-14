import unittest
import Application
import Stars
import pyglet

class TestGalaxyWindow(unittest.TestCase):
	out_of_bounds_window_dimensions = (
		(10000, 400), 
		(400, 10000),
		(10, 400), 
		(400, 10))
	
	stars = Stars.All(
		[
			Stars.NamedStar((1000, -1000), 'Sol'),
			Stars.NamedStar((1000, 1000), 'Centauri'),
		],
		[
			Stars.BackgroundStar((10, 0), (128, 0, 255))
		])
	data = Application.DataContainer()
	data.stars = stars

	window_and_minimum_dimensions = (
		(640, 480, 480),
		(200, 200, 200),
		(600, 800, 600))

	window_and_minimum_scales = (
		(640, 480, 8.333333333333334),
		(200, 200, 20.0),
		(600, 800, 6.666666666666667))

	window_and_maximum_scales = (
		(640, 480, 4.166666666666667),
		(200, 200, 10.0),
		(600, 800, 3.3333333333333335))

	def testLackingStars(self):
		"Should complain if no stars have been defined."
		self.assertRaises(Application.MissingDataException, Application.GalaxyWindow)

	def testWindowDimensionsOutOfBounds(self):
		"Should not allow width or height outside of boundary limits."
		for width, height in self.out_of_bounds_window_dimensions:
			self.assertRaises(Application.RangeException, Application.GalaxyWindow, width, height)
	
	def testResizeWindowDimensionsOutOfBounds(self):
		"Resize should not allow width or height outside of boundary limits."
		galaxy_window = Application.GalaxyWindow(data=self.data)
		for width, height in self.out_of_bounds_window_dimensions:
			self.assertRaises(Application.RangeException, galaxy_window.on_resize, width, height)
		galaxy_window.close()
	
	def testScaleOutOfBounds(self):
		"Scale should raise an exception if it is set to 0 or less"
		for scale in (0, -10):
			new_window = Application.GalaxyWindow(640, 480, self.data)
			self.assertRaises(Application.RangeException, new_window.set_scale, scale)
			new_window.close()
	
	def testWindowToAbsolute(self):
		"At various scales and centers, ensure test window coordinates match known absolute coordinates."
		scaled_coordinates = (
			(2.0, (200, -300), (600, 400), (55.29600000000001, -54.528)),
			(0.5, (0, 0), (-250, -250), (-146.304, -121.72800000000001)),
			(1.0, (4, 551), (533, 334), (4.8, 96.19200000000001)),
			)
		galaxy_window = Application.GalaxyWindow(data=self.data)
		for scale, absolute_center, window_coordinate, absolute_coordinate in scaled_coordinates:
			galaxy_window.set_scale(scale)
			galaxy_window.set_center(absolute_center)
			self.assertEqual(galaxy_window.window_to_absolute(window_coordinate), absolute_coordinate)
		galaxy_window.close()
	
	def testNewWindowMinimumDimension(self):
		"Given various window dimensions, new windows should have minimum_dimension attribute set to known values."
		for width, height, minimum in self.window_and_minimum_dimensions:
			galaxy_window = Application.GalaxyWindow(width, height, data=self.data)
			self.assertEqual(galaxy_window.minimum_dimension, minimum)
			galaxy_window.close()
	
	def testResizeWindowMinimumDimension(self):
		"Given various window dimensions, resized windows should have minimum_dimension attribute set to known values."
		galaxy_window = Application.GalaxyWindow(400, 400, data=self.data)
		for width, height, minimum in self.window_and_minimum_dimensions:
			galaxy_window.on_resize(width, height)
			self.assertEqual(galaxy_window.minimum_dimension, minimum)
		galaxy_window.close()
	
	def testNewWindowMinimumScale(self):
		"Given various window dimensions, new windows should have minimum_scale attribute set to known values."
		for width, height, scale in self.window_and_minimum_scales:
			galaxy_window = Application.GalaxyWindow(width, height, data=self.data)
			self.assertEqual(galaxy_window.minimum_scale, scale)
			galaxy_window.close()
	
	def testResizeWindowMinimumScale(self):
		"Given various window dimensions, resized windows should have minimum_scale attribute set to known values."
		galaxy_window = Application.GalaxyWindow(400, 400, data=self.data)
		for width, height, scale in self.window_and_minimum_scales:
			galaxy_window.on_resize(width, height)
			self.assertEqual(galaxy_window.minimum_scale, scale)
		galaxy_window.close()
	
	def testNewWindowMaximumScale(self):
		"Given various window dimensions, new windows should have maximum_scale attribute set to known values."
		for width, height, scale in self.window_and_maximum_scales:
			galaxy_window = Application.GalaxyWindow(width, height, data=self.data)
			self.assertEqual(galaxy_window.maximum_scale, scale)
			galaxy_window.close()
	
	def testResizeWindowMaximumScale(self):
		"Given various window dimensions, resized windows should have maximum_scale attribute set to known values."
		galaxy_window = Application.GalaxyWindow(400, 400, data=self.data)
		for width, height, scale in self.window_and_maximum_scales:
			galaxy_window.on_resize(width, height)
			self.assertEqual(galaxy_window.maximum_scale, scale)
		galaxy_window.close()
	
if __name__ == "__main__":
	unittest.main()

