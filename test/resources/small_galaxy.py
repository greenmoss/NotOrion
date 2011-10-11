import galaxy_objects
import application

data = application.DataContainer()
data.galaxy_objects = galaxy_objects.All(
		# foreground stars
		[
			galaxy_objects.ForegroundStar((150, 50), 'Tau Ceti', 'yellow'),
			galaxy_objects.ForegroundStar((150, 150), 'Eta Cassiopeiae', 'yellow'),
			galaxy_objects.ForegroundStar((50, 150), 'Alpha Centauri', 'yellow'),
			galaxy_objects.ForegroundStar((-150, -150), 'Xi Bootis', 'yellow'),
			#galaxy_objects.ForegroundStar((600, 600), 'Star1', 'yellow'),
			#galaxy_objects.ForegroundStar((750, 750), 'Star2', 'yellow'),
		],
		# background stars
		[
			galaxy_objects.BackgroundStar((0, 0), (0, 0, 255)),
			galaxy_objects.BackgroundStar((250, 250), (0, 255, 0)),
			galaxy_objects.BackgroundStar((-250, -250), (255, 0, 0)),
			galaxy_objects.BackgroundStar((10, -100), (228, 255, 255)),
			galaxy_objects.BackgroundStar((100, 100), (255, 255, 228)),
			galaxy_objects.BackgroundStar((-200, -300), (255, 228, 255)),
			galaxy_objects.BackgroundStar((-160, 228), (228, 255, 255)),
			galaxy_objects.BackgroundStar((589, -344), (228, 255, 255)),
			galaxy_objects.BackgroundStar((-420, -300), (255, 255, 228)),
			galaxy_objects.BackgroundStar((-400, 299), (255, 228, 255)),
			galaxy_objects.BackgroundStar((589, -344), (228, 255, 255)),
			galaxy_objects.BackgroundStar((420, -300), (255, 255, 228)),
			galaxy_objects.BackgroundStar((400, 199), (255, 228, 255)),
		],
		# black holes
		#[
		#	galaxy_objects.BlackHole((250, -250), 120),
		#],
	)
