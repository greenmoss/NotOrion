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
	absolute_and_window_coordinates = (
		(640, 480, 2.1, (0, 0), (0, 0)), 
		(923, 561, 0.34, (-5, 3), (-11294.117647058822, 6776.470588235294)), 
		(1024, 768, 8, (15, -2), (1440.0, -192.0)))

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

	def testScaledWindow(self):
		"Given test window dimensions, scaled_window ratio for new windows should return known test values."
		scaled_window_values = (
			(640, 480, 96.0),
			(500, 1000, 200.0),
			(1423, 955, 191.0))
		for width, height, ratio in scaled_window_values:
			new_window = Application.GalaxyWindow(width, height)
			self.assertEqual(new_window.scaled_window, ratio)
			new_window.close()

	def testResizeRescaleScaledWindow(self):
		"Given test window dimensions, scaled_window ratio for resized, rescaled windows should return known test values."
		rescaled_scaled_window_values = (
			(640, 480, 0.2, 3840.0),
			(500, 1000, 1.0, 768.0),
			(1423, 955, 7.4, 103.78378378378378))
		for width, height, new_scale, ratio in rescaled_scaled_window_values:
			self.galaxy_window.on_resize(width, height)
			self.galaxy_window.derive_from_scale(new_scale)
			self.assertEqual(self.galaxy_window.scaled_window, ratio)

	def testInverseForegroundScale(self):
		"Given test window dimensions, inverse foreground scale for new windows should return known test values."
		inverse_foreground_scale_values = (
			(5.0, 0.2),
			(10.0, 0.1),
			(0.2, 5.0))
		for scale, inverse_scale in inverse_foreground_scale_values:
			self.galaxy_window.derive_from_scale(scale)
			self.assertEqual(self.galaxy_window.inverse_foreground_scale, inverse_scale)
	
	def testScaleOutOfBounds(self):
		"Scale should raise an exception if it is set to 0 or less"
		for scale in (0, -10):
			new_window = Application.GalaxyWindow(640, 480)
			self.assertRaises(Application.RangeException, new_window.derive_from_scale, scale)
	
	def testAbsoluteToWindow(self):
		"For predefined window dimensions, scale level, and absolute coordinates, should convert to known window coordinates."
		for width, height, scale_level, absolute_coordinates, window_coordinates in self.absolute_and_window_coordinates:
			self.galaxy_window.on_resize(width, height)
			self.galaxy_window.derive_from_scale(scale_level)
			self.assertEqual(self.galaxy_window.absolute_to_window(absolute_coordinates), window_coordinates)
	
	def testWindowToAbsolute(self):
		"For predefined window dimensions, scale level, and window coordinates, should convert to known absolute coordinates."
		for width, height, scale_level, absolute_coordinates, window_coordinates in self.absolute_and_window_coordinates:
			self.galaxy_window.on_resize(width, height)
			self.galaxy_window.derive_from_scale(scale_level)
			self.assertEqual(self.galaxy_window.window_to_absolute(window_coordinates), absolute_coordinates)

if __name__ == "__main__":
	unittest.main()

