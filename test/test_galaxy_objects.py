import unittest
import pyglet
import sys
sys.path.append('../src')
import galaxy_objects

pyglet.resource.path = ['../images']
pyglet.resource.reindex()
star_image = pyglet.resource.image('star.png')

class TestForegroundStar(unittest.TestCase):
	test_star = galaxy_objects.ForegroundStar((500, 500), 'sol', 'yellow')

	def testOutOfBounds(self):
		"Should not allow x or y coordinates outside of boundary limits."
		out_of_bounds_coordinates = (
			(100000, 0), 
			(-100000, 0), 
			(0, -100000), 
			(0, 100000))
		for coordinate in out_of_bounds_coordinates:
			self.assertRaises(galaxy_objects.RangeException, galaxy_objects.ForegroundStar, coordinate, 'sol')

	def testBadLengthName(self):
		"Should not allow star names longer or shorter than limit."
		test_names = (
			'a',
			'supercalifragilistic')
		for test_name in test_names:
			self.assertRaises(galaxy_objects.RangeException, galaxy_objects.ForegroundStar, (0, 0), test_name)
	
	def testBadColor(self):
		"Should only allow valid star colors."
		self.assertRaises(galaxy_objects.DataError, galaxy_objects.ForegroundStar, (0, 0), 'sol', 'chartreuse')

	def testScalingCoordinates(self):
		"Given scaling factors, star with known coordinates should scale to known test values."
		conversions = (
			(0.1334, 3748.1259370314847),
			(1.0, 500.0),
			(7.5321, 66.38254935542545))
		for scaler, result in conversions:
			self.test_star.scale_coordinates(scaler)
			self.assertEqual(self.test_star.sprite.x, result)
			self.assertEqual(self.test_star.sprite.y, result)
	
	def testScalingLabels(self):
		"Given scaling factors, star with known coordinates should scale to known test values."
		conversions = (
			(0.1334, 3748.025937031485, 3742.525937031485),
			(1.0, 499.9, 494.4),
			(7.5321, 66.28254935542546, 60.78254935542545))
		for scaler, resultx, resulty in conversions:
			self.test_star.scale_coordinates(scaler)
			self.assertEqual(self.test_star.label.x, resultx)
			self.assertEqual(self.test_star.label.y, resulty)
	
	def testColor(self):
		"Star color should have known values."
		self.assertEqual(self.test_star.sprite.color, [255,255,0])

class TestAll(unittest.TestCase):
	# some test data
	galaxy_objects = galaxy_objects.All(
		[
			galaxy_objects.ForegroundStar((-4000, -200), 'Xi Bootis'),
			galaxy_objects.ForegroundStar((-500, 2000), 'Alpha Centauri'),
			galaxy_objects.ForegroundStar((1000, -1000), 'Sol'),
			galaxy_objects.ForegroundStar((4000, 900), 'Delta Pavonis'),
		],
		[
			galaxy_objects.BackgroundStar((0, 0), (0, 0, 255)),
			galaxy_objects.BackgroundStar((10, 0), (128, 0, 255))
		],
		[ galaxy_objects.BlackHole((300, 1000), 120) ]
	)

	def testMissingNamedStars(self):
		"Require minimum number of foreground stars."
		self.assertRaises(galaxy_objects.MissingDataException, galaxy_objects.All, [], [])
		self.assertRaises(galaxy_objects.MissingDataException, galaxy_objects.All, [1], [])

	def testMissingBackgroundStars(self):
		"Providing too few background stars should be disallowed."
		self.assertRaises(galaxy_objects.MissingDataException, galaxy_objects.All, [1, 2], [])

	def testBoundingArea(self):
		"Bounding area of galaxy_objects using test data should return known test values."
		self.assertEqual(self.galaxy_objects.left_bounding_x, -4000)
		self.assertEqual(self.galaxy_objects.right_bounding_x, 4000)
		self.assertEqual(self.galaxy_objects.top_bounding_y, 1500)
		self.assertEqual(self.galaxy_objects.bottom_bounding_y, -1500)
	
	def testBackgroundStarVertices(self):
		"Vertices of background stars using test data should return known test values."
		# would be better to test on the constructed pyglect vertex list
		# but I don't know how to do that :(
		# then I could also delete testBackgroundStarColors
		self.assertEqual(self.galaxy_objects.background_star_vertices, [0, 0, 0, 10, 0, 0])
	
	def testBackgroundStarColors(self):
		"Colors of background stars using test data should return known test values."
		self.assertEqual(self.galaxy_objects.background_star_colors, [0, 0, 255, 128, 0, 255])
	
	def testMaxDistance(self):
		"Given test data, ensure maximum distance has been set correctly."
		self.assertEqual(self.galaxy_objects.max_distance, 8075.270893288967)
	
	def testMinDistance(self):
		"Given test data, ensure minimum distance has been set correctly."
		self.assertEqual(self.galaxy_objects.min_distance, 1280.6248474865697)
	
	def testAnimate(self):
		"Given a set of black holes and a given time delta, final sprite rotation should be a known value."
		self.galaxy_objects.animate(0.2)
		self.assertEqual(self.galaxy_objects.black_holes[0].sprite.rotation, 116.4)

if __name__ == "__main__":
	unittest.main()
