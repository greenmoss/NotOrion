#! /usr/bin/env python -O
from __future__ import division
import os
import argparse
import logging
logger = logging.getLogger(__name__)
import jsonpickle

import pyglet

from globals import g
import window
import models.galaxy
import models.setup
import states.galaxy
import states.setup

class Application(object):
	"""All application-level functionality, for instance game setup/teardown,
	saved-game load/write, etc."""
	
	def configure(self):
		self.parse_args()
		g.window = window.Window()
		g.galaxy = models.galaxy.Galaxy()
		g.setup = models.setup.Setup()

		self.states = {}
	
	def exit(self):
		logger.debug('exiting')
		self.save()
		g.window.close()
	
	def save(self):
		if not os.path.exists(g.paths['saved_games_dir']):
			os.makedirs(paths['saved_games_dir'])
		game_file_path = os.path.abspath(
			os.path.join(g.paths['saved_games_dir'], 'game.json')
		)

		saved_data = {}
		saved_data['galaxy'] = g.galaxy.save()
		saved_data['galaxy_state'] = self.states['galaxy'].save()

		with open(game_file_path, 'w') as file_handle:
			file_handle.write(jsonpickle.encode(saved_data))

	def load(self, filename):
		game_file_path = os.path.abspath(
			os.path.join(g.paths['saved_games_dir'], filename)
		)
		if not os.path.exists(game_file_path):
			raise Exception, "unable to find saved game file: %s"%game_file_path

		saved_data = {}
		with open(game_file_path) as file_handle:
			saved_data = jsonpickle.decode('\n'.join(file_handle.readlines()))

		g.galaxy = saved_data['galaxy']
		self.set_state('galaxy')
		self.state.load(saved_data['galaxy_state'])

	def run(self):
		if vars(self.args)['continue']: # "self.args.continue" is a syntax error, thus "vars(self.args)" instead
			logger.debug("received --continue")
			self.load('game.json')

		elif self.args.difficulty:
			logger.debug("received --difficulty: %s",self.args.difficulty)
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
		logger.debug("setting state to %s"%new_state)
		# if a state was already set, remove its handlers
		if len(g.window._event_stack) > 0:
			g.window.pop_handlers()

		# I am unsophisticated, and using an ugly if/then/else
		if self.states.has_key(new_state):
			self.state = self.states[new_state]

		elif new_state == 'setup':
			self.state = states.setup.Setup()

		elif new_state == 'galaxy':
			self.state = states.galaxy.Galaxy()

		else:
			raise Exception, "unknown state: %s"%new_state

		self.states[new_state] = self.state
