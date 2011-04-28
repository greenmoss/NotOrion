import unittest
import Stars
import pyglet

pyglet.resource.path = ['../images']
pyglet.resource.reindex()
star_image = pyglet.resource.image('star.png')

class TestNamedStar(unittest.TestCase):
	test_star = Stars.NamedStar((500, 500), 'sol')

	def testOutOfBounds(self):
		"Should not allow x or y coordinates outside of boundary limits."
		out_of_bounds_coordinates = (
			(100000, 0), 
			(-100000, 0), 
			(0, -100000), 
			(0, 100000))
		for coordinate in out_of_bounds_coordinates:
			self.assertRaises(Exception, Stars.NamedStar, coordinate, 'sol')

	def testBadLengthName(self):
		"Should not allow star names longer or shorter than limit."
		test_names = (
			'a',
			'supercalifragilistic')
		for test_name in test_names:
			self.assertRaises(Exception, Stars.NamedStar, (0, 0), test_name)

	def testScalingCoordinates(self):
		"Given scaling factors, star with known coordinates should scale to known test values."
		conversions = (
			(0.1334, 66.69999999999999),
			(1.0, 500.0),
			(7.5321, 3766.0499999999997))
		for scaler, result in conversions:
			self.test_star.scale(scaler)
			self.assertEqual(self.test_star.sprite.x, result)
			self.assertEqual(self.test_star.sprite.y, result)
	
	def testScalingLabels(self):
		"Given scaling factors, star with known coordinates should scale to known test values."
		conversions = (
			(0.1334, 71.69999999999999, 66.69999999999999),
			(1.0, 505.0, 500.0),
			(7.5321, 3771.0499999999997, 3766.0499999999997))
		for scaler, resultx, resulty in conversions:
			self.test_star.scale(scaler)
			self.assertEqual(self.test_star.label.x, resultx)
			self.assertEqual(self.test_star.label.y, resulty)

class TestAll(unittest.TestCase):
	# some test data
	stars = Stars.All(
		[
			Stars.NamedStar((-4000, -200), 'Xi Bootis'),
			Stars.NamedStar((-500, 2000), 'Alpha Centauri'),
			Stars.NamedStar((1000, -1000), 'Sol'),
			Stars.NamedStar((4000, 900), 'Delta Pavonis'),
		],
		[
			Stars.BackgroundStar((0, 0), (0, 0, 255)),
			Stars.BackgroundStar((10, 0), (128, 0, 255))
		])

	def testBoundingArea(self):
		"Bounding area of stars using test data should return known test values."
		self.assertEqual(self.stars.left_bounding_x, -4000)
		self.assertEqual(self.stars.right_bounding_x, 4000)
		self.assertEqual(self.stars.top_bounding_y, 2000)
		self.assertEqual(self.stars.bottom_bounding_y, -1000)
	
	def testBackgroundStarVertices(self):
		"Vertices of stars using test data should return known test values."
		# would be better to test on the constructed pyglect vertex list
		# but I don't know how to do that :(
		# then I could also delete testBackgroundStarColors
		self.assertEqual(self.stars.background_star_vertices, [0, 0, -100, 10, 0, -100])
	
	def testBackgroundStarColors(self):
		"Vertices of stars using test data should return known test values."
		self.assertEqual(self.stars.background_star_colors, [0, 0, 255, 128, 0, 255])

if __name__ == "__main__":
	unittest.main()
