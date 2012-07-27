import pyglet

from globals import g

class Marker(object):
	"""Range markers and indicators visible within the galaxy main map."""
	marker_color = (25,128,25)

	def __init__(self, state):
		self.state = state

		self.visible = False
		self.reset_state = True
		self.concentric_markers = None

		self.circles_vertex_lists = []
		self.origin_star = None
		self.origin_coordinate = None
		self.cursor_label_batch = pyglet.graphics.Batch()
		self.cursor_label_visible = False
		self.cursor_label = pyglet.text.Label(
			"",
			x=0,
			y=0,
			anchor_x='center',
			anchor_y='bottom',
			color=(Marker.marker_color[0], Marker.marker_color[1], Marker.marker_color[2], 255),
			font_size=10,
			batch=self.cursor_label_batch
		)
		# shaded box behind cursor label, to make it easier to read
		self.cursor_label_box = pyglet.graphics.vertex_list( 4,
			'v2f',
			('c4B/static', (
				0, 0, 0, 200,
				0, 0, 0, 200,
				0, 0, 0, 200,
				0, 0, 0, 200,
				)
			)
		)
		self.line_vertex_list = pyglet.graphics.vertex_list( 2,
			('v2f', ( 0, 0,  0, 0 ) ),
			('c3B/static', Marker.marker_color*2)
		)
		# while we were marking ranges, which end stars were marked?
		self.marked_end_stars = {}
	
	def animate(self, dt):
		'Do any/all animations.'

		# markers for items under mouse
		if not(self.over_objects == self.highlight_objects):
			# new set of animations
			self.highlight_objects = self.over_objects

	def reset_circles(self):
		"remove circle vertices"
		self.concentric_markers = None
		# must manually delete old vertex lists, or we get (video?) memory leak
		for vertex_list in self.circles_vertex_lists:
			vertex_list.delete()
		self.circles_vertex_lists = []

	def reset_range_state(self):
		# reset all end star marker colors
		for end_star in self.marked_end_stars.keys():
			end_star.reset_marker()
			end_star.hide_marker()
		self.marked_end_stars = {}

		# reset origin star marker color
		if self.origin_star:
			self.origin_star.reset_marker()
			self.origin_star.hide_marker()
			self.marked_end_stars[self.origin_star] = True
			self.origin_star = None

		# reveal marker again if we are over a re-marked star
		for object in self.over_objects:
			if self.marked_end_stars.has_key(object):
				object.reveal_marker()

		self.marked_end_stars = {}

		self.origin_coordinate = None

		self.reset_circles()

		self.cursor_label_visible = False

		# set initial state for *next* range iteration
		self.reset_state = True

	def fix_mouse_in_window(self):
		"""_mouse_in_window is built in, so normally it wouldn't be a good idea to override it
		but since it reports "False" on startup even though the cursor is in the window, we'll
		cheat/fix/workaround"""
		g.window._mouse_in_window = True

	def set_over_objects(self, x, y):
		"Set objects that are under the cursor, and show/hide relevant markers"
		over_objects = []
		return
		detected_objects = self.state.detect_map_mouseover_objects(x,y)
		if len(detected_objects) > 0:
			# maximally-seen object is first
			for object in sorted(detected_objects, key=detected_objects.get, reverse=True):
				if type(object) == galaxy_objects.ForegroundStar:
					over_objects.append(object)
				elif type(object) == galaxy_objects.WormHole:
					over_objects.append(object)
				else: # black hole
					detected_objects.pop(object)

		if not(over_objects == self.over_objects):
			for object in self.over_objects:
				if not detected_objects.has_key(object):
					object.hide_marker()
			for object in over_objects:
				object.reveal_marker()
			self.over_objects = over_objects

	def set_range_circles(self, x, y):
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
					( 'c3B/static', Marker.marker_color*len(circle_vertices) )
				)
			)

	def set_info(self, visible = True, debug = False):
		self.visible = visible

		if visible is False:
			self.reset_range_state()
			return

		# do not attempt to set any range info unless our mouse cursor is within the window
		if self.window._mouse_in_window is False:
			return

		if self.reset_state is True:
			self.capture_range_state()

		end_coordinate = self.window_to_absolute((self.window._mouse_x, self.window._mouse_y))
		end_star = None

		# snap to star
		for object in self.over_objects:
			# it should be a star
			if type(object) is not galaxy_objects.ForegroundStar:
				continue

			# it should not be the origin star
			if object is self.origin_star:
				continue

			end_star = object
			end_coordinate = object.coordinates
			break

		# determine distance from origin to end
		distance = math.sqrt(
			abs(self.origin_coordinate[0]-end_coordinate[0])**2 +
			abs(self.origin_coordinate[1]-end_coordinate[1])**2
		)
		screen_distance = distance/self.foreground_scale

		if debug:
			if self.origin_star:
				logging.debug( "from %s: %s"%(self.origin_star.name, self.origin_star.coordinates) )
			if end_star:
				logging.debug( "to %s: %s"%(end_star.name, end_star.coordinates) )
			logging.debug( "distance: %0.2f; screen_distance: %0.2f"%(distance, screen_distance) )
		
		if screen_distance > 10:
			label_parsecs_float = round(distance/100, 1)
			label_distance = label_parsecs_float if label_parsecs_float < 1 else int(label_parsecs_float)
			label_unit = 'parsec' if label_distance is 1 else 'parsecs'
			self.cursor_label.text = "%s %s"%(label_distance, label_unit)

			end_coordinates = (self.window._mouse_x, self.window._mouse_y)
			if end_star:
				end_star_window_coordinates = self.absolute_to_window(end_star.coordinates)
				label_x = end_star_window_coordinates[0]
				label_y = end_star_window_coordinates[1]+8
				end_coordinates = end_star_window_coordinates
				end_star.marker.color = Marker.marker_color
				self.marked_end_stars[end_star] = True
			else:
				label_x = self.window._mouse_x
				label_y = self.window._mouse_y+5
			self.cursor_label.x = label_x
			self.cursor_label.y = label_y

			label_box_top = label_y + self.cursor_label.content_height
			label_box_bottom = label_y
			label_box_right = label_x + (self.cursor_label.content_width/2)
			label_box_left = label_x - (self.cursor_label.content_width/2)
			self.cursor_label_box.vertices = [
				label_box_right, label_box_bottom,
				label_box_right, label_box_top,
				label_box_left, label_box_top,
				label_box_left, label_box_bottom
			]

			range_origin_window_coordinates = self.absolute_to_window(self.origin_coordinate)
			self.line_vertex_list.vertices = [
				range_origin_window_coordinates[0], range_origin_window_coordinates[1],
				end_coordinates[0], end_coordinates[1]
			]

			self.cursor_label_visible = True
		else:
			self.cursor_label_visible = False

		if self.origin_star:
			self.origin_star.marker.color = Marker.marker_color
			self.origin_star.reveal_marker()

			if self.reset_state is True:
				window_range_origin = self.absolute_to_window(self.origin_star.coordinates)
				self.set_range_circles(window_range_origin[0], window_range_origin[1])

		# completed initial state of range iteration
		self.reset_state = False

	def handle_mouse_motion(self, x, y, dx, dy):
		self.fix_mouse_in_window()

		self.set_over_objects(x,y)
		#if self.visible is True:
		#	self.set_info()

	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		# range markers must be recalculated
		self.concentric_markers = None
	
	def on_resize(self, width, height):
		# range markers must be recalculated
		self.concentric_markers = None
