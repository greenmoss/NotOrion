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
	background_fields_of_view = (
		(640, 480, 7.5),
		(500, 1000, 15.625),
		(1423, 955, 14.921875))

	def testOutOfBounds(self):
		"Should not allow width or height outside of boundary limits."
		for width, height in self.out_of_bounds_window_dimensions:
			self.assertRaises(Application.RangeException, Application.GalaxyWindow, width, height)
	
	def testResizeOutOfBounds(self):
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

	def testBackgroundFieldOfView(self):
		"Given test window dimensions, background field of view for new windows should return known test values."
		for width, height, background_field_of_view in self.background_fields_of_view:
			new_window = Application.GalaxyWindow(width, height)
			self.assertEqual(new_window.background_field_of_view, background_field_of_view)
			new_window.close()

	def testResizeBackgroundFieldOfView(self):
		"Given test window dimensions, background field of view for resized windows should return known test values."
		for width, height, background_field_of_view in self.background_fields_of_view:
			self.galaxy_window.on_resize(width, height)
			self.assertEqual(self.galaxy_window.background_field_of_view, background_field_of_view)

if __name__ == "__main__":
	unittest.main()

