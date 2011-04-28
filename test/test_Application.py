import unittest
import Application
import pyglet

class TestGalaxyWindow(unittest.TestCase):
	galaxy_window = Application.GalaxyWindow()
	out_of_bounds_window_dimensions = (
		(10000, 400), 
		(400, 10000),
		(10, 400), 
		(400, 10))
	window_aspect_ratios = (
		(640, 480, 1.3333333333333333),
		(500, 1000, 0.5),
		(1423, 955, 1.4900523560209424))
	dimensions_into_foreground_scale = (
		(640, 480, 96.0),
		(500, 1000, 200.0),
		(1423, 955, 191.0))
	dimensions_into_foreground_resize_rescale = (
		(640, 480, 0.2, 3840.0),
		(500, 1000, 1.0, 768.0),
		(1423, 955, 7.4, 103.78378378378378))

	def testWindowDimensionsOutOfBounds(self):
		"Should not allow width or height outside of boundary limits."
		for width, height in self.out_of_bounds_window_dimensions:
			self.assertRaises(Application.RangeException, Application.GalaxyWindow, width, height)
	
	def testResizeWindowDimensionsOutOfBounds(self):
		"Resize should not allow width or height outside of boundary limits."
		for width, height in self.out_of_bounds_window_dimensions:
			self.assertRaises(Application.RangeException, self.galaxy_window.on_resize, width, height)

	def testAspectRatio(self):
		"Given test window dimensions, aspect ratio for new windows should return known test values."
		for width, height, ratio in self.window_aspect_ratios:
			new_window = Application.GalaxyWindow(width, height)
			self.assertEqual(new_window.window_aspect_ratio, ratio)
			new_window.close()

	def testResizeAspectRatio(self):
		"Given test window dimensions, aspect ratio for resized windows should return known test values."
		for width, height, ratio in self.window_aspect_ratios:
			self.galaxy_window.on_resize(width, height)
			self.assertEqual(self.galaxy_window.window_aspect_ratio, ratio)

	def testDimensionsIntoForegroundScale(self):
		"Given test window dimensions, dimensions-into-scale ratio for new windows should return known test values."
		for width, height, ratio in self.dimensions_into_foreground_scale:
			new_window = Application.GalaxyWindow(width, height)
			self.assertEqual(new_window.dimensions_into_foreground_scale, ratio)
			new_window.close()

	def testResizeRescaleDimensionsIntoForegroundScale(self):
		"Given test window dimensions, dimensions-into-scale ratio for resized, rescaled windows should return known test values."
		for width, height, new_scale, ratio in self.dimensions_into_foreground_resize_rescale:
			self.galaxy_window.on_resize(width, height)
			self.galaxy_window.rescale(new_scale)
			self.assertEqual(self.galaxy_window.dimensions_into_foreground_scale, ratio)

if __name__ == "__main__":
	unittest.main()

