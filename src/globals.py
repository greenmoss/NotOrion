#! /usr/bin/env python -O
""" This contains one object, with one instance, to contain globals that will
be used across the entire game.

With the exception of external modules such as logging that will be shared and
imported once, object properties are initialized but *not* assigned here.  """

import logging
import os

import pyglet

class Globals(object):
	
	def __init__(self):
		self.logging = logging
		# paths must be set very early, so do it here instead of in application
		self.paths = self.get_paths()
		self.application = None
		self.window = None
		self.galaxy = None

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
		
g = Globals()
