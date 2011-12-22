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
application.set_paths()

import galaxy
import galaxy_objects

class TestGalaxyWindowContainer(unittest.TestCase):
	data = application.DataContainer()
	data.galaxy_objects = galaxy_objects.All(
		[
			galaxy_objects.ForegroundStar((1000, -1000), 'Sol'),
			galaxy_objects.ForegroundStar((1000, 1000), 'Centauri'),
		],
		[
			galaxy_objects.BackgroundStar((10, 0), (128, 0, 255))
		])

	window_and_minimum_dimensions = (
		(640, 480, 480),
		(400, 400, 400),
		(600, 800, 600))

	window_and_minimum_scales = (
		(640, 480, 20.833333333333336),
		(400, 400, 25.0),
		(600, 800, 16.666666666666668))

	window_and_maximum_scales = (
		(640, 480, 20.833333333333336),
		(400, 400, 25.0),
		(600, 800, 16.666666666666668))

	scaled_coordinates = (
		(2.0, (200, -300), (600, 400), (1145.8333333333333, 208.33333333333331)),
		(0.5, (0, 0), (-250.0000000000001, -250.0), (-9921.875, -8255.208333333332)),
		(1.0, (4, 551), (533, 334), (273.4375, -651.0416666666666)),
		)
	
	# in some cases, need more foreground stars in test data
	more_data = application.DataContainer()
	more_data.galaxy_objects = galaxy_objects.All(
		[
			galaxy_objects.ForegroundStar((1000, -1000), 'Sol'),
			galaxy_objects.ForegroundStar((1000, 1000), 'Centauri'),
			galaxy_objects.ForegroundStar((-2000, 2000), 'Centauri1'),
			galaxy_objects.ForegroundStar((-2000, -2000), 'Sol1'),
			galaxy_objects.ForegroundStar((100, -100), 'Sol2'),
			galaxy_objects.ForegroundStar((200, -200), 'Sol3'),
			galaxy_objects.ForegroundStar((0, 0), 'Sol4'),
		],
		[
			galaxy_objects.BackgroundStar((10, 0), (128, 0, 255))
		])

	def testLackingStars(self):
		"Should complain if no galaxy_objects have been defined."
		self.assertRaises(galaxy.MissingDataException, galaxy.WindowContainer, application.DataContainer())
	
	def testWindowContainerDimensionsOutOfBounds(self):
		"Should not allow width or height outside of boundary limits."
		self.data.galaxy_window_state = galaxy.WindowState()
		out_of_bounds_window_dimensions = (
			(10000, 400), 
			(400, 10000),
			(10, 400), 
			(400, 10))
		for width, height in out_of_bounds_window_dimensions:
			self.assertRaises(galaxy.RangeException, galaxy.WindowContainer, self.data, width, height)
	
	def testScaleOutOfBounds(self):
		"Scale should raise an exception if it is set to 0 or less"
		for scale in (0, -10):
			new_window = galaxy.WindowContainer(self.data, 640, 480)
			self.assertRaises(galaxy.RangeException, new_window.set_scale, scale)
			new_window.window.close()
	
	def testStarBounds(self):
		"Given foreground stars, x and y bounds should match known values."
		star_sets = (
			((5, 10), (20, 50), (-5, 32), 12.5, 25.0),
			((25, 0), (-30, -5), (0, -10), 27.5, 5.0),
			)
		for star1, star2, star3, bounding_x, bounding_y in star_sets:
			data = application.DataContainer()
			data.galaxy_objects = galaxy_objects.All(
				[
					galaxy_objects.ForegroundStar(star1, 'star1'),
					galaxy_objects.ForegroundStar(star2, 'star2'),
					galaxy_objects.ForegroundStar(star3, 'star3'),
				],
				[
					galaxy_objects.BackgroundStar((10, 0), (128, 0, 255))
				])
			galaxy_window = galaxy.WindowContainer(data=data)
			self.assertEqual(galaxy_window.foreground_bounding_x, bounding_x)
			self.assertEqual(galaxy_window.foreground_bounding_y, bounding_y)
			galaxy_window.window.close()

	def testWindowContainerToAbsolute(self):
		"At various scales and centers, ensure test window coordinates match known absolute coordinates."
		galaxy_window = galaxy.WindowContainer(data=self.data)
		for scale, absolute_center, window_coordinate, absolute_coordinate in self.scaled_coordinates:
			galaxy_window.set_scale(scale)
			galaxy_window.set_center(absolute_center)
			self.assertEqual(galaxy_window.window_to_absolute(window_coordinate), absolute_coordinate)
		galaxy_window.window.close()

	def testAbsoluteToWindowContainer(self):
		"At various scales and centers, ensure test absolute coordinates match known window coordinates."
		galaxy_window = galaxy.WindowContainer(data=self.data)
		for scale, absolute_center, window_coordinate, absolute_coordinate in self.scaled_coordinates:
			galaxy_window.set_scale(scale)
			galaxy_window.set_center(absolute_center)
			self.assertEqual(galaxy_window.absolute_to_window(absolute_coordinate), window_coordinate)
		galaxy_window.window.close()
	
	def testCenterLimits(self):
		"Using different sets of galaxy_objects, scales and window sizes, ensure we have known window center limits."
		parameters = (
			(640, 480, (5, 10), (20, 50), (-5, 32), 0.9,
				0, 0, 0, 0),
			(1024, 768, (25, 0), (-30, -5), (0, -10), 1.0, 
				0, 0, 0, 0),
			(500, 600, (25, 0), (-30, -5), (0, -10), 3.5, 
				0, 0, 0, 0),
			)
		for width, height, star1, star2, star3, scale, top, right, bottom, left in parameters:
			data = application.DataContainer()
			data.galaxy_objects = galaxy_objects.All(
				[
					galaxy_objects.ForegroundStar(star1, 'star1'),
					galaxy_objects.ForegroundStar(star2, 'star2'),
					galaxy_objects.ForegroundStar(star3, 'star3'),
				],
				[
					galaxy_objects.BackgroundStar((10, 0), (128, 0, 255))
				])
			galaxy_window = galaxy.WindowContainer(data, width, height)
			galaxy_window.set_scale(scale)
			self.assertEqual(galaxy_window.center_limits, {'top': top, 'right': right, 'bottom': bottom, 'left': left})
			galaxy_window.window.close()
	
	def testSetCenter(self):
		"Within a window of known dimensions, galaxy_objects, and scale, setting the center should give known center coordinates."
		data = application.DataContainer()
		data.galaxy_objects = galaxy_objects.All(
			[
				galaxy_objects.ForegroundStar((500, 0), 'star1'),
				galaxy_objects.ForegroundStar((50, -400), 'star2'),
				galaxy_objects.ForegroundStar((-325, 320), 'star3'),
				galaxy_objects.ForegroundStar((0, 220), 'star4'),
			],
			[
				galaxy_objects.BackgroundStar((10, 0), (128, 0, 255))
			])
		galaxy_window = galaxy.WindowContainer(data)
		galaxy_window.set_scale(1.0)
		before_and_after_center_coordinates = (
			((30, 25), (0, 0)),
			((800, 35), (0, 0)),
			((80, 900), (0, 0)),
			((70, -900), (0, 0)),
			)
		for set_coordinates, final_coordinates in before_and_after_center_coordinates:
			galaxy_window.set_center(set_coordinates)
			self.assertEqual(galaxy_window.absolute_center, final_coordinates)
		galaxy_window.window.close()
	
	def testNewWindowContainerMinimumDimension(self):
		"Given various window dimensions, new windows should have minimum_dimension attribute set to known values."
		for width, height, minimum in self.window_and_minimum_dimensions:
			galaxy_window = galaxy.WindowContainer(self.data, width, height)
			self.assertEqual(galaxy_window.minimum_dimension, minimum)
			galaxy_window.window.close()
	
	def testResizeWindowContainerMinimumDimension(self):
		"Given various window dimensions, resized windows should have minimum_dimension attribute set to known values."
		galaxy_window = galaxy.WindowContainer(self.data, 400, 400)
		for width, height, minimum in self.window_and_minimum_dimensions:
			galaxy_window.window.on_resize(width, height)
			self.assertEqual(galaxy_window.minimum_dimension, minimum)
		galaxy_window.window.close()
	
	def testNewWindowContainerMinimumScale(self):
		"Given various window dimensions, new windows should have minimum_scale attribute set to known values."
		for width, height, scale in self.window_and_minimum_scales:
			galaxy_window = galaxy.WindowContainer(self.data, width, height)
			self.assertEqual(galaxy_window.minimum_scale, scale)
			galaxy_window.window.close()
	
	def testResizeWindowContainerMinimumScale(self):
		"Given various window dimensions, resized windows should have minimum_scale attribute set to known values."
		galaxy_window = galaxy.WindowContainer(self.data, 400, 400)
		for width, height, scale in self.window_and_minimum_scales:
			galaxy_window.window.on_resize(width, height)
			self.assertEqual(galaxy_window.minimum_scale, scale)
		galaxy_window.window.close()
	
	def testNewWindowContainerMaximumScale(self):
		"Given various window dimensions, new windows should have maximum_scale attribute set to known values."
		for width, height, scale in self.window_and_maximum_scales:
			galaxy_window = galaxy.WindowContainer(self.data, width, height)
			self.assertEqual(galaxy_window.maximum_scale, scale)
			galaxy_window.window.close()
	
	def testResizeWindowContainerMaximumScale(self):
		"Given various window dimensions, resized windows should have maximum_scale attribute set to known values."
		galaxy_window = galaxy.WindowContainer(self.data, 400, 400)
		for width, height, scale in self.window_and_maximum_scales:
			galaxy_window.window.on_resize(width, height)
			self.assertEqual(galaxy_window.maximum_scale, scale)
		galaxy_window.window.close()
	
	def testMiniMapInvisible(self):
		"Given various window dimensions and only two foreground stars, mini-map should not be visible."
		window_dimensions_and_vertices = (
			(640, 480),
			(400, 400),
			(600, 800))
		for width, height in window_dimensions_and_vertices:
			galaxy_window = galaxy.WindowContainer(self.data, width, height)
			self.assertEqual(galaxy_window.mini_map_visible, False)
			galaxy_window.window.close()
	
	def testMiniMapCorners(self):
		"Given various window dimensions, mini-map corners should be known values."
		window_dimensions_and_vertices = (
			(640, 480, {'top': 95, 'right': 620, 'left': 563.75, 'bottom': 20}),
			(400, 400, {'top': 95, 'right': 380, 'left': 323.75, 'bottom': 20}),
			(600, 800, {'top': 95, 'right': 580, 'left': 523.75, 'bottom': 20}))
		for width, height, mini_map_corners in window_dimensions_and_vertices:
			galaxy_window = galaxy.WindowContainer(self.more_data, width, height)
			galaxy_window.set_scale(0.5)
			galaxy_window.set_center((0,0))
			self.assertEqual(galaxy_window.mini_map_corners, mini_map_corners)
			galaxy_window.window.close()
	
	def testMiniMapWindowContainerCorners(self):
		"Given various window dimensions, mini-map window corners should be known values."
		window_dimensions_and_vertices = (
			(640, 480, {'top': 63.5, 'right': 599.875, 'left': 583.875, 'bottom': 51.5}),
			(400, 400, {'top': 63.5, 'right': 357.875, 'left': 345.875, 'bottom': 51.5}),
			(600, 800, {'top': 65.5, 'right': 557.875, 'left': 545.875, 'bottom': 49.5}))
		for width, height, mini_map_window_corners in window_dimensions_and_vertices:
			self.more_data.galaxy_window_state = galaxy.WindowState()
			galaxy_window = galaxy.WindowContainer(self.more_data, width, height)
			galaxy_window.set_scale(0.5)
			galaxy_window.set_center((0,0))
			self.assertEqual(galaxy_window.mini_map_window_corners, mini_map_window_corners)
			galaxy_window.window.close()
	
	def testScrollToCenter(self):
		"When scrolling mouse, window should stay centered on mouse position"
		scroll_data = (
			(512, 384, 5, (0.0, 0.0)),
			(199, 659, -17, (0, 50.68371862755731)),
			(730, 128, 0, (0.0, 50.68371862755731)),
			(2, 2, 31, (0, 88.03867196751236))
		)
		self.more_data.galaxy_window_state = galaxy.WindowState()
		galaxy_window = galaxy.WindowContainer(self.more_data, 1024, 768)
		for x, y, scroll_y, new_absolute_center in scroll_data:
			galaxy_window.window.on_mouse_scroll(x, y, 0, scroll_y)
			self.assertEqual(galaxy_window.absolute_center, new_absolute_center)
		galaxy_window.window.close()
	
	# this does not work?!
	#def testMouseOverSeesObjects(self):
	#	"Given known window dimensions and foreground objects, mouseovers should 'see' them"
	#	galaxy_window = galaxy.WindowContainer(self.more_data, width=400, height=400)
	#	over_objects = galaxy_window.detect_mouseover_objects(0,0,radius=4)
	#	galaxy_window.window.close()
	
if __name__ == "__main__":
	unittest.main()

