#! /usr/bin/env python -O
from __future__ import division
import pyglet
import galaxy
import pickle
import argparse
import imp
import sys
import game_configuration
import os
import logging

def set_paths():
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

class DataContainer(object):
	"A simple object to store all application data."

	def __init__(self):
		self.paths = set_paths()
		self.galaxy_objects = None
		self.galaxy_window_state = galaxy.WindowState()

class Application(object):
	"Controller class for all game objects and functionality."

	def __init__(self, data=None):

		self.handle_cli_args()

		paths = set_paths()

		if not os.path.exists(paths['preferences_dir']):
			os.makedirs(paths['preferences_dir'])

		if not os.path.exists(paths['saved_games_dir']):
			os.makedirs(paths['saved_games_dir'])
		self.game_file_path = os.path.abspath(
			os.path.join(paths['saved_games_dir'], 'game.pickled')
		) # right now we only save one game file

		self.try_data_import(data)

		# if no data has been loaded, generate new
		if not hasattr(self, 'data'):
			self.data = DataContainer()

			# if difficulty was not set, self.args.difficulty will be None
			game_configuration.Choose(self.data, difficulty=self.args.difficulty)

		self.data.galaxy_window = galaxy.WindowContainer(self.data)

	def cleanup(self):
		"""Clean up the application. Ideally this would be automatic, via the opposite of __init__"""
		if hasattr(self, 'data'):
			self.save()

	def handle_cli_args(self):
		"Configure and parse command-line arguments"
		parser = argparse.ArgumentParser(description='NotOrion')
		parser.add_argument('--save-game-file')
		parser.add_argument('--data-init-file')
		parser.add_argument('--continue', action='store_true')
		parser.add_argument('--difficulty', choices=['Beginner', 'Easy', 'Normal', 'Challenging'])
		self.args = parser.parse_args()

	def try_data_import(self, data):
		"Determine source of data object, and attempt to import the data"
		# allow data to be passed as parameter, mostly useful for testing
		if data:
			self.data = data

		# read a python file to initialize self.data
		elif self.args.data_init_file:
			# *not* using file handle invocation, since it drops random "c" files
			if os.path.exists(self.args.data_init_file):
				imported = imp.load_source('', self.args.data_init_file)
				self.data = imported.data
			else:
				logging.warning( "file not found: %s; starting new game"%self.args.data_init_file )

		# unpickle a pickled file as source of self.data
		elif self.args.save_game_file:
			if os.path.exists(self.args.save_game_file):
				with open(self.args.save_game_file) as save_game_file:
					self.data = pickle.load(save_game_file)
			else:
				logging.warning( "file not found: %s; starting new game"%self.args.save_game_file )

		# unpickle the standard game file as source of self.data
		elif vars(self.args)['continue']: # "self.args.continue" is a syntax error, thus "vars(self.args)" instead
			if os.path.exists(self.game_file_path):
				with open(self.game_file_path) as save_game_file:
					self.data = pickle.load(save_game_file)
			else:
				logging.warning( "file not found: %s; starting new game"%self.game_file_path )

	def save(self):
		'Save game state'

		# do not save unless data container has been populated
		if not self.data.galaxy_objects:
			logging.warning( "no data; not saving" )
			return None

		with open(self.game_file_path, 'w') as save_game_file:
			pickle.dump(self.data, save_game_file)

if __name__ == "__main__":
	app = Application()
	pyglet.app.run()
	app.cleanup()
