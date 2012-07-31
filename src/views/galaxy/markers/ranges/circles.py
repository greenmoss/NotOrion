import pyglet

class Circles(object):
	def __init__(self):
		self.concentric_markers = None
		self.circles = []

	def reset_circles(self):
		"remove circle vertices"
		self.concentric_markers = None
		# must manually delete old vertex lists, or we get (video?) memory leak
		for circle in self.circles:
			vertex_list.delete()
		self.circles_vertex_lists = []

	def set(self, x, y):
		"calculate vertices for successive range circle markers"

		# always reset in case we have old range circle markers
		# otherwise we will get a memory leak
		self.reset_circles()

		# Set logarithmically-scaled concentric circles showing range in parsecs from given x, y
		if not self.concentric_markers:
			self.concentric_markers = []

			# how many parsecs from corner to corner?
			right_top = self.window_to_absolute((self.window.width, self.window.height))
			left_bottom = self.window_to_absolute((0, 0))
			height_parsecs = (right_top[1]-left_bottom[1])/100
			width_parsecs = (right_top[0]-left_bottom[0])/100
			parsecs = math.sqrt(height_parsecs**2 + width_parsecs**2)

			# length of each parsec in window coordinates?
			coords_per_parsec = parsecs/100*self.foreground_scale

			# range marker steps, in parsecs, of appropriate size for screen size and scale
			marker_steps = filter( 
				lambda length: 
					length <= parsecs, 
					[1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128, 160, 192, 256, 320, 384, 512]
			)

			logging.debug( "in set_range_circles, parsecs: %s, steps: %s"%(parsecs, marker_steps) )
			previous_radius = 0
			previous_difference = 0
			for step in marker_steps:
				absolute_radius = step*100
				length = absolute_radius / self.foreground_scale
				difference = length - previous_radius
				# exclude radii of circles that would be too close to the previous radius
				if difference < 30:
					continue
				# ensure difference to previous circle always increases or remains the same
				if difference < previous_difference:
					continue
				previous_radius = length
				previous_difference = difference
				logging.debug( "step: %s, absolute_radius: %s, length: %s"%(step, absolute_radius, length) )

				self.concentric_markers.append( utilities.circle_vertices(length) )

		for circle_vertices in self.concentric_markers:
			positioned_circle_vertices = []
			for vertex in circle_vertices:
				positioned_circle_vertices.append( (vertex[0]+x, vertex[1]+y) )
			self.circles_vertex_lists.append( 
				pyglet.graphics.vertex_list( 
					len(circle_vertices),
					( 'v2f',        tuple(itertools.chain(*positioned_circle_vertices)) ),
					( 'c3B/static', Markers.marker_color*len(circle_vertices) )
				)
			)

class Circle(object):
	def __init__(self):
		self.vertex_list = []

