import pyglet

class Line(object):
	def __init__(self):
		self.vertex_list = pyglet.graphics.vertex_list( 2,
			('v2f', ( 0, 0,  0, 0 ) ),
			('c3B/static', marker_color*2)
		)

class LineFromStar(object):
	def __init__(self):
		super(LineFromStar, self).__init__()
		self.origin_star = None
		# while we were marking ranges, which end stars were marked?
		self.marked_end_stars = {}

class LineFromCoordinate(object):
	def __init__(self):
		super(LineFromCoordinate, self).__init__()
		self.origin_coordinate = None

