#! /usr/bin/env python -O
from __future__ import division
import os
import argparse

import pyglet

from globals import g
import window
import galaxy
import setup
import states.setup
import states.galaxy

class Application(object):
	"""All application-level functionality, for instance game setup/teardown,
	saved-game load/write, etc."""
	
	def configure(self):
		self.paths = self.get_paths()
		self.parse_args()
		g.window = window.Window()
		g.galaxy = galaxy.Galaxy()
		g.setup = setup.Setup()

	def run(self):
		if self.args.difficulty:
			g.logging.debug("received --difficulty: %s",self.args.difficulty)
			g.setup.set_galaxy_from_difficulty(self.args.difficulty)
			g.setup.generate_galaxy()
			self.set_state('galaxy')
		else:
			self.set_state('setup')
		pyglet.app.run()

	def parse_args(self):
		"Configure and parse command-line arguments"
		parser = argparse.ArgumentParser(description='NotOrion')
		parser.add_argument('--save-game-file')
		parser.add_argument('--continue', action='store_true')
		parser.add_argument('--difficulty', choices=['Beginner', 'Easy', 'Normal', 'Challenging'])
		self.args = parser.parse_args()
	
	def set_state(self, new_state):
		g.logging.debug("setting state to %s"%new_state)
		# if a state was already set, remove its handlers
		if len(g.window._event_stack) > 0:
			g.window.pop_handlers()

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
	
