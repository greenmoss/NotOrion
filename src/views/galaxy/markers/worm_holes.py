from globals import g
import views.galaxy

class WormHoles(object):
	def __init__(self):
		self.under_cursor = []

	def set_over_objects(self, objects_under_cursor):
		for map_object in objects_under_cursor:
			self.under_cursor = []
			if not type(map_object) == views.galaxy.map.objects.worm_holes.WormHole:
				continue
			self.under_cursor.append(map_object)
			#g.logging.debug("worm hole: %s",map_object)

class WormHole(object):
	pass
