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

class TestNebula(unittest.TestCase):

	def testValidLobeCount(self):
		"Number of lobes should fall within acceptable limits."
		invalid_lobe_counts = (
			[], 
			[1, 2, 3, 4, 5, 6, 7] )
		for lobe_arg in invalid_lobe_counts:
			self.assertRaises(galaxy_objects.RangeException, galaxy_objects.Nebula, (0,0), 'red', lobe_arg)

	def testValidPrimaryColor(self):
		"Nebula primary color should be a valid value."
		self.assertRaises(galaxy_objects.DataError, galaxy_objects.Nebula, (0,0), 'chartreuse', [1,2,3])

	def testValidSecondaryColor(self):
		"Lobes should request a valid secondary color."
		invalid_lobe_secondary_colors = ( -1, 2 )
		for lobe_secondary in invalid_lobe_secondary_colors:
			self.assertRaises(galaxy_objects.RangeException, galaxy_objects.Nebula, (0,0), 'red', [(invalid_lobe_secondary_colors)])

	def testValidSpriteIdentifier(self):
		"Lobes should request a valid sprite identifier."
		invalid_lobe_sprite_identifiers = ( 0, 3 )
		for sprite_identifier in invalid_lobe_sprite_identifiers:
			self.assertRaises(galaxy_objects.RangeException, galaxy_objects.Nebula, (0,0), 'red', [(0, sprite_identifier)])

	def testLobeValidCoordinates(self):
		"Lobes coordinates should fall in valid bounds."
		invalid_lobe_coordinates = ( (-210, 0), (0, -210), (210, 0), (0, 210) )
		for coordinate in invalid_lobe_coordinates:
			self.assertRaises(galaxy_objects.RangeException, galaxy_objects.Nebula, (0,0), 'red', [(0, 1, coordinate)])

	def testLobeValidRotation(self):
		"Lobes rotation should fall in valid bounds."
		invalid_lobe_rotations = ( -1, 361 )
		for rotation in invalid_lobe_rotations:
			self.assertRaises(galaxy_objects.RangeException, galaxy_objects.Nebula, (0,0), 'red', [(0, 1, (0, 0), rotation)])

	def testLobeValidScale(self):
		"Lobes scale should fall in valid bounds."
		invalid_lobe_scales = ( 0.2, 4.1 )
		for scale in invalid_lobe_scales:
			self.assertRaises(galaxy_objects.RangeException, galaxy_objects.Nebula, (0,0), 'red', [(0, 1, (0, 0), 0, scale)])
	
	def testLobeScaling(self):
		"Given test data, lobes should scale to known values."
		test_nebula = galaxy_objects.Nebula(
			(10, 20), 'red', [
				(0, 1, (5, -5), 0, 1.0)
			]
		)
		test_scales = ( 
			(2.0, 7.5, 7.5, 0.5),
			(1.0, 15.0, 15.0, 1.0),
			(0.5, 30.0, 30.0, 2.0)
		)
		for scaling_factor, x, y, sprite_scale in test_scales:
			test_nebula.scale_coordinates_and_size(scaling_factor)
			self.assertEqual(test_nebula.lobes[0]['sprite'].x, x)
			self.assertEqual(test_nebula.lobes[0]['sprite'].y, y)
			self.assertEqual(test_nebula.lobes[0]['sprite'].scale, sprite_scale)

class TestWormHole(unittest.TestCase):

	def testUniqueWormHole(self):
		"Named stars may only have one wormhole"
		(star1, star2, star3) = (
			galaxy_objects.ForegroundStar((-4000, -200), 'Xi Bootis'),
			galaxy_objects.ForegroundStar((-500, 2000), 'Alpha Centauri'),
			galaxy_objects.ForegroundStar((1000, -1000), 'Sol')
			)
		(bgstar1, bgstar2) = (
			galaxy_objects.BackgroundStar((0, 0), (0, 0, 255)),
			galaxy_objects.BackgroundStar((10, 0), (128, 0, 255))
			)
		self.assertRaises(
			galaxy_objects.DataError, 
			galaxy_objects.All,
			[ star1, star2, star3 ],
			[ bgstar1, bgstar2 ],
			worm_holes=[ (0,1), (0,2) ]
		)

class TestAll(unittest.TestCase):
	# some test data
	(star1, star2, star3, star4) = (
		galaxy_objects.ForegroundStar((-4000, -200), 'Xi Bootis'),
		galaxy_objects.ForegroundStar((-500, 2000), 'Alpha Centauri'),
		galaxy_objects.ForegroundStar((1000, -1000), 'Sol'),
		galaxy_objects.ForegroundStar((4000, 900), 'Delta Pavonis')
		)
	(bgstar1, bgstar2) = (
		galaxy_objects.BackgroundStar((0, 0), (0, 0, 255)),
		galaxy_objects.BackgroundStar((10, 0), (128, 0, 255))
		)
	valid_star_set = [ star1, star2, star3, star4 ]
	valid_background_star_set = [ bgstar1, bgstar2 ]
	valid_black_hole_set = [ galaxy_objects.BlackHole((300, 1000), 120) ]
	valid_nebulae_set = [
		galaxy_objects.Nebula(
			(0, 0), 'red', [
				(0, 1, (5, -5), 0, 1.0)
			]
		)
	]
	valid_worm_hole_set = [(0,1)]
	galaxy_objects = galaxy_objects.All(
		valid_star_set,
		valid_background_star_set,
		valid_black_hole_set,
		valid_nebulae_set,
		valid_worm_hole_set
	)

	def testDisallowedStarBlackHoleOverlap(self):
		"Stars and black holes should be a minimum distance apart."
		self.assertRaises(
			galaxy_objects.DataError, 
			galaxy_objects.All, 
			[
				galaxy_objects.ForegroundStar((-4000, -200), 'Xi Bootis'),
				galaxy_objects.ForegroundStar((-4000, -200), 'Evil Xi Bootis'),
			], 
			self.valid_background_star_set
		)
		self.assertRaises(
			galaxy_objects.DataError, 
			galaxy_objects.All, 
			[
				galaxy_objects.ForegroundStar((-4000, -200), 'Xi Bootis'),
				galaxy_objects.ForegroundStar((-4000, 200), 'Spica'),
			], 
			self.valid_background_star_set,
			[ galaxy_objects.BlackHole((-4000, 200), 120) ]
		)
	
	def testDisallowedNebulaOverlap(self):
		"Nebulae should be a minimum distance apart."
		self.assertRaises(
			galaxy_objects.DataError, 
			galaxy_objects.All, 
			self.valid_star_set,
			self.valid_background_star_set,
			self.valid_black_hole_set,
			[
				galaxy_objects.Nebula(
					(0, 0), 'red', [
						(0, 1, (5, -5), 0, 1.0)
					]
				),
				galaxy_objects.Nebula(
					(0, 399), 'red', [
						(0, 1, (5, -5), 0, 1.0)
					]
				)
			]
		)
		self.assertRaises(
			galaxy_objects.DataError, 
			galaxy_objects.All, 
			self.valid_star_set,
			self.valid_background_star_set,
			self.valid_black_hole_set,
			[
				galaxy_objects.Nebula(
					(0, 0), 'red', [
						(0, 1, (5, -5), 0, 1.0)
					]
				),
				galaxy_objects.Nebula(
					(-399, 0), 'red', [
						(0, 1, (5, -5), 0, 1.0)
					]
				)
			]
		)

	def testMissingNamedStars(self):
		"Require minimum number of foreground stars."
		self.assertRaises(galaxy_objects.MissingDataException, galaxy_objects.All, [], self.valid_background_star_set)
		self.assertRaises(galaxy_objects.MissingDataException, galaxy_objects.All, [self.star1], self.valid_background_star_set)

	def testMissingBackgroundStars(self):
		"Providing too few background stars should be disallowed."
		self.assertRaises(galaxy_objects.MissingDataException, galaxy_objects.All, self.valid_star_set, [])
	
	def testPickle(self):
		"If we are pickled, the unpickled object should match the original."
		import pickle
		pickled = pickle.dumps(self.galaxy_objects)
		restored = pickle.loads(pickled)
		# some simple equality tests, that will be improved upon once objects have equality functions
		self.assertEqual(self.galaxy_objects.left_bounding_x, restored.left_bounding_x)
		self.assertEqual(self.galaxy_objects.background_star_vertices, restored.background_star_vertices)
		self.assertEqual(self.galaxy_objects.min_coords, restored.min_coords)

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
