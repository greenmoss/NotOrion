from globals import g
import views.galaxy
import hover_objects

class WormHoles(hover_objects.HoverGroup):
	"""The worm hole marker view "wraps" the star marker view."""

	def __init__(self, map_view, marker_stars):
		self.map_view = map_view
		self.map_view_type = views.galaxy.map.objects.worm_holes.WormHole
		super(WormHoles, self).__init__()

		for map_worm_hole in self.map_view.worm_holes:
			self.markers[map_worm_hole] = Marker(
				map_worm_hole, marker_stars
			)

class Marker(object):
	def __init__(self, map_object, marker_stars):
		# each worm hole needs to inform marker Stars about marker view state
		self.map_object = map_object
		self.color = self.map_object.color
		self.marker_stars = marker_stars

		self.marker_star1 = marker_stars.markers[map_object.star1_view]
		self.marker_star2 = marker_stars.markers[map_object.star2_view]

		self.hide()
	
	def show(self):
		self.visible = True
		self.marker_star1.show(self)
		self.marker_star2.show(self)
	
	def hide(self):
		self.visible = False
		self.marker_star1.hide(self)
		self.marker_star2.hide(self)
