import unittest
import pyglet
import sys
sys.path.append('../src')
import Application
import Stars

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

	scaled_coordinates = (
		(2.0, (200, -300), (600, 400), (458.3333333333333, 83.33333333333333)),
		(0.5, (0, 0), (-250, -250), (-3968.75, -3302.083333333333)),
		(1.0, (4, 551), (533, 334), (109.375, -260.41666666666663)),
		)
	
	# in some cases, need more stars in test data
	more_stars_data = Application.DataContainer()
	more_stars_data.stars = Stars.All(
		[
			Stars.NamedStar((1000, -1000), 'Sol'),
			Stars.NamedStar((1000, 1000), 'Centauri'),
			Stars.NamedStar((-2000, 2000), 'Centauri1'),
			Stars.NamedStar((-2000, -2000), 'Sol1'),
			Stars.NamedStar((100, -100), 'Sol2'),
			Stars.NamedStar((200, -200), 'Sol3'),
		],
		[
			Stars.BackgroundStar((10, 0), (128, 0, 255))
		])

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
	
	def testStarBounds(self):
		"Given foreground stars, x and y bounds should match known values."
		star_sets = (
			((5, 10), (20, 50), (-5, 32), 20, 50),
			((25, 0), (-30, -5), (0, -10), 30, 10),
			)
		for star1, star2, star3, bounding_x, bounding_y in star_sets:
			stars = Stars.All(
				[
					Stars.NamedStar(star1, 'star1'),
					Stars.NamedStar(star2, 'star2'),
					Stars.NamedStar(star3, 'star3'),
				],
				[
					Stars.BackgroundStar((10, 0), (128, 0, 255))
				])
			data = Application.DataContainer()
			data.stars = stars
			galaxy_window = Application.GalaxyWindow(data=data)
			self.assertEqual(galaxy_window.stars_bounding_x, bounding_x)
			self.assertEqual(galaxy_window.stars_bounding_y, bounding_y)
			galaxy_window.close()

	def testWindowToAbsolute(self):
		"At various scales and centers, ensure test window coordinates match known absolute coordinates."
		galaxy_window = Application.GalaxyWindow(data=self.data)
		for scale, absolute_center, window_coordinate, absolute_coordinate in self.scaled_coordinates:
			galaxy_window.set_scale(scale)
			galaxy_window.set_center(absolute_center)
			self.assertEqual(galaxy_window.window_to_absolute(window_coordinate), absolute_coordinate)
		galaxy_window.close()

	def testAbsoluteToWindow(self):
		"At various scales and centers, ensure test absolute coordinates match known window coordinates."
		galaxy_window = Application.GalaxyWindow(data=self.data)
		for scale, absolute_center, window_coordinate, absolute_coordinate in self.scaled_coordinates:
			galaxy_window.set_scale(scale)
			galaxy_window.set_center(absolute_center)
			self.assertEqual(galaxy_window.absolute_to_window(absolute_coordinate), window_coordinate)
		galaxy_window.close()
	
	def testCenterLimits(self):
		"Using different sets of stars, scales and window sizes, ensure we have known window center limits."
		parameters = (
			(640, 480, (5, 10), (20, 50), (-5, 32), 0.9,
				421.79750654142674, 4.7190026165707195, -421.79750654142674, -4.7190026165707195),
			(1024, 768, (25, 0), (-30, -5), (0, -10), 1.0, 
				0, 5.1887177639254105, 0, -5.1887177639254105),
			(500, 600, (25, 0), (-30, -5), (0, -10), 3.5, 
				0, 121.6072381275556, 0, -121.6072381275556),
			)
		for width, height, star1, star2, star3, scale, top, right, bottom, left in parameters:
			stars = Stars.All(
				[
					Stars.NamedStar(star1, 'star1'),
					Stars.NamedStar(star2, 'star2'),
					Stars.NamedStar(star3, 'star3'),
				],
				[
					Stars.BackgroundStar((10, 0), (128, 0, 255))
				])
			data = Application.DataContainer()
			data.stars = stars
			galaxy_window = Application.GalaxyWindow(width, height, data)
			galaxy_window.set_scale(scale)
			self.assertEqual(galaxy_window.center_limits, {'top': top, 'right': right, 'bottom': bottom, 'left': left})
			galaxy_window.close()
	
	def testSetCenter(self):
		"Within a window of known dimensions, stars, and scale, setting the center should give known center coordinates."
		stars = Stars.All(
			[
				Stars.NamedStar((500, 0), 'star1'),
				Stars.NamedStar((50, -400), 'star2'),
				Stars.NamedStar((-325, 320), 'star3'),
				Stars.NamedStar((0, 220), 'star4'),
			],
			[
				Stars.BackgroundStar((10, 0), (128, 0, 255))
			])
		data = Application.DataContainer()
		data.stars = stars
		galaxy_window = Application.GalaxyWindow(data=data)
		galaxy_window.set_scale(1.0)
		before_and_after_center_coordinates = (
			((30, 25), (30, 25)),
			((800, 35), (88.0, 35)),
			((80, 900), (80, 116.0)),
			((70, -900), (70, -116.0)),
			)
		for set_coordinates, final_coordinates in before_and_after_center_coordinates:
			galaxy_window.set_center(set_coordinates)
			self.assertEqual(galaxy_window.absolute_center, final_coordinates)
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
	
	def testMiniMapInvisible(self):
		"Given various window dimensions and only two named stars, mini-map should not be visible."
		window_dimensions_and_vertices = (
			(640, 480),
			(200, 200),
			(600, 800))
		for width, height in window_dimensions_and_vertices:
			galaxy_window = Application.GalaxyWindow(width, height, data=self.data)
			self.assertEqual(galaxy_window.mini_map_visible, False)
			galaxy_window.close()
	
	def testMiniMapCorners(self):
		"Given various window dimensions, mini-map corners should be known values."
		window_dimensions_and_vertices = (
			(640, 480, {'top': 95, 'right': 620, 'left': 545.0, 'bottom': 20}),
			(200, 200, {'top': 95, 'right': 180, 'left': 105.0, 'bottom': 20}),
			(600, 800, {'top': 95, 'right': 580, 'left': 505.0, 'bottom': 20}))
		for width, height, mini_map_corners in window_dimensions_and_vertices:
			galaxy_window = Application.GalaxyWindow(width, height, data=self.more_stars_data)
			galaxy_window.set_scale(0.5)
			self.assertEqual(galaxy_window.mini_map_corners, mini_map_corners)
			galaxy_window.close()
	
	def testMiniMapWindowCorners(self):
		"Given various window dimensions, mini-map window corners should be known values."
		window_dimensions_and_vertices = (
			(640, 480, {'top': 67.5, 'right': 595.8333333333334, 'left': 569.1666666666666, 'bottom': 47.5}),
			(200, 200, {'top': 61.666666666666664, 'right': 146.66666666666666, 'left': 138.33333333333334, 'bottom': 53.333333333333336}),
			(600, 800, {'top': 74.16666666666666, 'right': 555.0, 'left': 530.0, 'bottom': 40.833333333333336}))
		for width, height, mini_map_window_corners in window_dimensions_and_vertices:
			galaxy_window = Application.GalaxyWindow(width, height, data=self.more_stars_data)
			galaxy_window.set_scale(0.5)
			self.assertEqual(galaxy_window.mini_map_window_corners, mini_map_window_corners)
			galaxy_window.close()
	
	def testScrollToCenter(self):
		"When scrolling mouse, window should stay centered on mouse position"
		scroll_data = (
			(512, 384, 5, (0.0, 0.0)),
			(199, 659, -17, (-57.6872870197289, 50.68371862755737)),
			(730, 128, 0, (-57.6872870197289, 50.68371862755737)),
			(2, 2, 31, (30.65763499540185, 102.2439908222284))
		)
		galaxy_window = Application.GalaxyWindow(1024, 768, data=self.more_stars_data)
		for x, y, scroll_y, new_absolute_center in scroll_data:
			galaxy_window.on_mouse_scroll(x, y, 0, scroll_y)
			self.assertEqual(galaxy_window.absolute_center, new_absolute_center)
		galaxy_window.close()
	
if __name__ == "__main__":
	unittest.main()

