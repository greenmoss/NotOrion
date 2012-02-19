#! /usr/bin/env python -O
from __future__ import division
import os

import pyglet

from globals import g
import window
import galaxy
import states.setup
import states.galaxy

class Application(object):
	"""All application-level functionality, for instance game setup/teardown,
	saved-game load/write, etc."""
	
	def run(self):
		self.paths = self.get_paths()
		g.window = window.Window()
		g.galaxy = galaxy.Galaxy()
		self.set_state('setup')
		pyglet.app.run()
	
	def set_state(self, new_state):
		g.logging.debug("setting state to %s"%new_state)

		# I am unsophisticated, and using an ugly if/then/else
		if new_state == 'setup':
			self.state = states.setup.Setup()

		elif new_state == 'galaxy':
			self.state = states.galaxy.Galaxy()

		else:
			raise Exception, "unknown state: %s"%new_state

	def get_paths(self):
		"""Determine paths to all game resources."""
		paths = { 'application': os.path.abspath( __file__ ) }
		paths['code_dir'] = os.path.dirname(paths['application'])
		paths['root_dir'] = os.path.abspath(os.path.join(paths['code_dir'], os.path.pardir))
		paths['resources_dir'] = os.path.abspath(os.path.join(paths['root_dir'], 'resources'))
		paths['images_dir'] = os.path.abspath(os.path.join(paths['resources_dir'], 'images'))
		paths['preferences_dir'] = pyglet.resource.get_settings_path('NotOrion')
		paths['saved_games_dir'] = os.path.join(paths['preferences_dir'], 'saved_games')

		# load images using pyglet's resource path
		if (pyglet.resource.path.count(paths['images_dir']) == 0):
			pyglet.resource.path.append(paths['images_dir'])
			pyglet.resource.reindex()

		return paths
	
