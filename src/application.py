#! python -O
from __future__ import division
import pyglet
import galaxy
import pickle
import argparse
import imp
import sys

class DataContainer(object):
	"A simple object to store all application data."

	def __init__(self):
		self.galaxy_objects = None
		self.galaxy_window_state = galaxy.WindowState()

class Application(object):
	"Controller class for all game objects and functionality."

	def __init__(self, data=None):
		self.game_file_path = "/tmp/notorion.save" # temporary, until we find OS-appropriate location

		parser = argparse.ArgumentParser(description='NotOrion')
		parser.add_argument('--save-game-file')
		parser.add_argument('--data-init-file')
		args = parser.parse_args()

		if data:
			# assign parameter "data" as self.data
			self.data = data

		elif args.data_init_file:
			# read a python file to initialize self.data
			# *not* using file handle invocation, since it drops random "c" files
			imported = imp.load_source('', args.data_init_file)
			self.data = imported.data

		elif args.save_game_file:
			# unpickle a pickled file as source of self.data
			with open(args.save_game_file) as save_game_file:
				self.data = pickle.load(save_game_file)

		else:
			# generate a new galaxy
			pass

		galaxy_window = galaxy.Window(self.data)
		pyglet.app.run()
		with open(self.game_file_path, 'w') as save_game_file:
			pickle.dump(self.data, save_game_file)

if __name__ == "__main__":
	Application()
