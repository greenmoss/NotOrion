#! /usr/bin/env python -O
from __future__ import division
import os
import random

import pyglet
from pyglet.gl import *

from globals import g
import panes
import panes.galaxy_objects as go
import utilities

class Galaxy(panes.Panes):
	# when scaling/rescaling, minimum distance between stars/black holes
	min_scaled_separation = 10
	# .01 more or less than 1.0 should be fast enough zoom speed
	zoom_speed = 1.01

	def __init__(self, state):
		g.logging.debug('instantiating panes.Galaxy')

		self.background_stars = go.background_stars.BackgroundStars()
		self.stars = go.stars.Stars()
		self.black_holes = go.black_holes.BlackHoles()
		self.nebulae = go.nebulae.Nebulae()
		self.worm_holes = go.worm_holes.WormHoles(self.stars)

		# black background
		glClearColor(0.0, 0.0, 0.0, 0)

		self.state = state

		self.bounding_y = g.galaxy.top_bounding_y
		if -g.galaxy.bottom_bounding_y > g.galaxy.top_bounding_y:
			self.bounding_y = -g.galaxy.bottom_bounding_y
		self.bounding_x = g.galaxy.right_bounding_x
		if -g.galaxy.left_bounding_x > g.galaxy.right_bounding_x:
			self.bounding_x = -g.galaxy.left_bounding_x

		self.derive_from_window_dimensions()
		self.set_scale(self.maximum_scale)
		self.set_center((0, 0))

		g.window.push_handlers(self)

		#pyglet.clock.schedule_interval(self.animate, 1/60.)
	
	def derive_from_window_dimensions(self):
		"Set attributes that are based on window dimensions."
		self.half_width = g.window.width/2
		self.half_height = g.window.height/2

		# Derive minimum and maximum scale, based on minimum and maximum distances between galaxy objects.
		self.minimum_dimension = (g.window.width < g.window.height) and g.window.width or g.window.height
			
		self.minimum_scale = g.galaxy.min_distance/self.minimum_dimension*5.0
		self.maximum_scale = g.galaxy.max_distance/self.minimum_dimension
		# restrict zooming out to the minimum distance between sprites
		if(g.galaxy.min_distance/self.maximum_scale < Galaxy.min_scaled_separation):
			self.maximum_scale = g.galaxy.min_distance/Galaxy.min_scaled_separation
		if self.minimum_scale > self.maximum_scale:
			self.maximum_scale = self.minimum_scale

	def set_center(self, coordinates):
		"Set the window center, for rendering objects."
		coordinates = [coordinates[0], coordinates[1]]
		# would the new center make us fall outside acceptable margins?
		if coordinates[1] > self.center_limits['top']:
			coordinates[1] = self.center_limits['top']
		elif coordinates[1] < self.center_limits['bottom']:
			coordinates[1] = self.center_limits['bottom']

		if coordinates[0] > self.center_limits['right']:
			coordinates[0] = self.center_limits['right']
		elif coordinates[0] < self.center_limits['left']:
			coordinates[0] = self.center_limits['left']

		self.pane_center = (coordinates[0], coordinates[1])

		# every time we update the center, the mini-map will change
		#self.derive_mini_map()

	def set_scale(self, scale):
		"Set attributes that are based on zoom/scale."

		# scale must be larger than 0
		if scale <= 0:
			raise RangeException, "scale must be greater than 0"

		if (scale < self.minimum_scale):
			scale = self.minimum_scale
		elif (scale > self.maximum_scale):
			scale = self.maximum_scale

		# the integer modifiers ensure all stars and labels remain visible at the limits 
		# of the pan area
		self.center_limits = {
			'top':self.bounding_y/scale+110-self.half_height,
			'right':self.bounding_x/scale+140-self.half_width,
			'bottom':-self.bounding_y/scale-120+self.half_height,
			'left':-self.bounding_x/scale-140+self.half_width,
		}
		if self.center_limits['top'] < self.center_limits['bottom']:
			self.center_limits['top'] = 0
			self.center_limits['bottom'] = 0
		if self.center_limits['right'] < self.center_limits['left']:
			self.center_limits['right'] = 0
			self.center_limits['left'] = 0

		self.scale = scale

		# recalculate all object attributes that rely on scale
		self.stars.set_scale(scale)
		self.black_holes.set_scale(scale)
		self.nebulae.set_scale(scale)
		self.worm_holes.set_scale(scale) # *must* be set *after* stars

	def pane_to_window(self, coordinates):
		"Translate pane coordinate into window coordinate, accounting for pane center and scale."
		return(
			coordinates[0]/self.scale+self.half_width-self.pane_center[0],
			coordinates[1]/self.scale+self.half_height-self.pane_center[1]
		)

	def window_to_pane(self, coordinates):
		"Translate window coordinate into pane coordinate, accounting for pane center and scale."
		return(
			(self.pane_center[0]+coordinates[0]-self.half_width)*self.scale,
			(self.pane_center[1]+coordinates[1]-self.half_height)*self.scale
		)
	
	def drawing_origin_to_center(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(-self.half_width, self.half_width, -self.half_height, self.half_height)
		glMatrixMode(GL_MODELVIEW)

	def drawing_to_center_of_viewing_area(self):
		gluLookAt(
			self.pane_center[0], self.pane_center[1], 0.0,
			self.pane_center[0], self.pane_center[1], -100.0,
			0.0, 1.0, 0.0)

	# all pyglet.window handlers
	def on_draw(self):
		g.window.clear()

		self.drawing_origin_to_center()
		self.background_stars.draw()

		self.drawing_to_center_of_viewing_area()
		self.nebulae.draw()
		self.worm_holes.draw()
		self.stars.draw()
		self.black_holes.draw()

		glLoadIdentity()

	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.set_center((self.pane_center[0] - dx, self.pane_center[1] - dy))
	
	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		prescale_pane_mouse = self.window_to_pane((x,y))

		#self.reset_range_state()

		self.set_scale(self.scale*(Galaxy.zoom_speed**scroll_y))

		# range markers must be recalculated
		#self.concentric_range_markers = None

		postscale_pane_mouse = self.window_to_pane((x,y))

		# scale the prescale mouse according to the *new* scale
		prescale_mouse = (prescale_pane_mouse[0]/self.scale, prescale_pane_mouse[1]/self.scale)
		postscale_mouse = (postscale_pane_mouse[0]/self.scale, postscale_pane_mouse[1]/self.scale)

		self.set_center(
			(
				prescale_mouse[0]-postscale_mouse[0]+self.pane_center[0], 
				prescale_mouse[1]-postscale_mouse[1]+self.pane_center[1]
			)
		)
	
	def on_resize(self, width, height):
		# reset openGL attributes to match new window dimensions
		glViewport(0, 0, width, height)
		glMatrixMode(gl.GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, width, 0, height, -1, 1)
		glMatrixMode(gl.GL_MODELVIEW)

		self.derive_from_window_dimensions()

		# window resize affects scale attributes, so recalculate
		self.set_scale(self.scale)

		# ensure center is still in a valid position
		self.set_center((self.pane_center[0], self.pane_center[1]))

		# range markers must be recalculated
		#self.concentric_range_markers = None
