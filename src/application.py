#! python -O
from __future__ import division
import pyglet
import galaxy
#import jsonpickle
import argparse
import imp
import sys

class DataContainer(object):
	"A simple object to store all application data."

	def __init__(self):
		self.galaxy_objects = None

class Application(object):
	"Controller class for all game objects and functionality."

	def __init__(self, data=None):
		#self.game_file_path = "/tmp/notorion.save" # temporary, until we find OS-appropriate location

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
			# unpickle a jsonpickled file as source of self.data
			pass
			#self.data = jsonpickle.decode(args.save_game_file)
			#args.save_game_file.close()

		else:
			# generate a new galaxy
			pass

		galaxy_window = galaxy.Window(1024, 768, self.data)
		pyglet.app.run()
		#with open(self.game_file_path, 'w') as saved_game_file:
		#	saved_game_file.write(jsonpickle.encode(self.data))
		#print pickled

if __name__ == "__main__":
	Application()
