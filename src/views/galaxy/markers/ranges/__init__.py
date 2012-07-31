import pyglet

import circles
import labels
import lines

class Ranges(object):
	marker_color = (25,128,25)

	def __init__(self):
		self.visible = False
		self.reset_state = True

	def reset_state(self):
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

	def set_info(self, visible, debug = False):
		self.visible = visible

		return

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
				end_star.marker.color = Markers.marker_color
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
			self.origin_star.marker.color = Markers.marker_color
			self.origin_star.reveal_marker()

			if self.reset_state is True:
				window_range_origin = self.absolute_to_window(self.origin_star.coordinates)
				self.set_range_circles(window_range_origin[0], window_range_origin[1])

		# completed initial state of range iteration
		self.reset_state = False
