class Mass(object):
	"""All physical masses within a galaxy that we can interact with."""

	def __init__(self, coordinates):
		if not (-10000 < coordinates[0] < 10000) or not (-10000 < coordinates[1] < 10000):
			raise RangeException, "coordinates must be between -10000 and 10000"

		self.coordinates = coordinates
