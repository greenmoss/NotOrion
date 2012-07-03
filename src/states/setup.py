#! /usr/bin/env python -O
from __future__ import division

from globals import g
import states
import panes.setup
import models.setup

class Setup(states.States):
	def __init__(self):
		g.logging.debug('instantiating state.Setup')
		self.pane = panes.setup.Setup(self)
		g.window.push_handlers(self.pane)

		self.pane.initialize_difficulty_dialog()
	
	def handle_difficulty_selection(self, chosen_difficulty):
		g.logging.debug('in handle_difficulty_selection, chosen_difficulty is %s',chosen_difficulty)

		g.setup.set_galaxy_from_difficulty(chosen_difficulty)

		if chosen_difficulty == 'Beginner':
			g.setup.generate_galaxy()
			self.pane.difficulty_dialog.teardown()
			g.application.set_state('galaxy')
			return

		self.pane.difficulty_dialog.teardown()
		self.pane.initialize_options_dialog()

	def handle_galaxy_age_help(self):
		self.pane.initialize_help_dialog(models.setup.Setup.galaxy_age_help_text)

	def handle_galaxy_age_selection(self, chosen_age):
		self.galaxy_age = chosen_age

		if not models.setup.Setup.age_defaults.has_key(chosen_age):
			raise Exception, "invalid age: %s"%chosen_age

		g.logging.debug(
			'in handle_galaxy_age_selection, for age %s, setting keys %s',
			chosen_age,
			models.setup.Setup.age_defaults[chosen_age].keys()
		)
		# is there a better way to merge dicts?
		for key, value in models.setup.Setup.age_defaults[chosen_age].iteritems():
			g.setup.galaxy_settings[key] = value

	def handle_galaxy_size_help(self):
		self.pane.initialize_help_dialog(models.setup.Setup.galaxy_size_help_text)

	def handle_galaxy_size_selection(self, chosen_size):
		g.setup.galaxy_settings['size'] = chosen_size

		if not models.setup.Setup.size_defaults.has_key(chosen_size):
			raise Exception, "invalid size: %s"%chosen_size

		g.logging.debug(
			'in handle_galaxy_size_selection, for size %s, setting keys %s',
			chosen_size,
			models.setup.Setup.size_defaults[chosen_size].keys()
		)
		# is there a better way to merge dicts?
		for key, value in models.setup.Setup.size_defaults[chosen_size].iteritems():
			g.setup.galaxy_settings[key] = value
	
	def handle_game_options_continue(self):
		"""Should have all necessary galaxy_settings, so generate the galaxy and enter galaxy state."""
		g.setup.generate_galaxy()
		self.pane.options_dialog.teardown()
		g.application.set_state('galaxy')
