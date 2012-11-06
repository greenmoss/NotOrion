import logging
logger = logging.getLogger(__name__)

import pyglet

import views.galaxy.map.stars
import utilities

class Orbits(object):
	def __init__(self, star_system_view):
		pass

class Orbit(object):

	def __init__(self, star_system_view):
		self.star_system_view = star_system_view
