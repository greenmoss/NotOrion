#! /usr/bin/env python -O
from __future__ import division
import os

import pyglet
from pyglet.gl import *
import kytten

from globals import g
import panes

class Setup(panes.Panes):

	def __init__(self, state):
		g.logging.debug('instantiating panes.Setup')

		self.state = state

		super(Setup, self).__init__()

		self.theme = kytten.Theme(
			os.path.join(g.application.paths['resources_dir'], 'gui'), 
			override={
				"gui_color": [64, 128, 255, 255],
				"font_size": 12
			}
		)
		self.batch = pyglet.graphics.Batch()
		self.group = pyglet.graphics.OrderedGroup(0)

	def on_draw(self):
		glClearColor(0.0, 0.0, 0.0, 0)
		g.window.clear()
		self.batch.draw()
	
	def initialize_difficulty_dialog(self):
		self.difficulty_dialog = kytten.Dialog(
			kytten.TitleFrame(
				"Choose Game Difficulty",
				kytten.VerticalLayout([
					kytten.Menu(
						options=self.state.difficulty_options,
						on_select=self.state.handle_difficulty_selection
					)
				]),
			),
			window=g.window, batch=self.batch, group=self.group,
			anchor=kytten.ANCHOR_CENTER,
			theme=self.theme
		)

	def initialize_options_dialog(self):
		self.options_dialog = kytten.Dialog(
			kytten.TitleFrame(
				"Choose Game Options",
				kytten.VerticalLayout([
					kytten.HorizontalLayout([
						kytten.Label("Galaxy Size"),
						None,
						kytten.Dropdown(
							options=self.state.size_options,
							selected=self.state.galaxy_size,
							on_select=self.state.handle_galaxy_size_selection,
						),
						kytten.Button("?", on_click=self.state.handle_galaxy_size_help),
					]),
					kytten.HorizontalLayout([
						kytten.Label("Galaxy Age"),
						None,
						kytten.Dropdown(
							options=self.state.age_options,
							selected=self.state.galaxy_age,
							on_select=self.state.handle_galaxy_age_selection,
						),
						kytten.Button("?", on_click=self.state.handle_galaxy_age_help),
					]),
					kytten.Button("Continue", on_click=self.state.handle_galaxy_parameters),
				]),
			),
			window=g.window, batch=self.batch, group=self.group,
			anchor=kytten.ANCHOR_CENTER,
			theme=self.theme
		)
	
	def initialize_help_dialog(self, message):
		# must initially set to None in order to be able to define teardown()
		self.help_dialog = None

		def teardown():
			self.help_dialog.teardown()

		self.help_dialog = kytten.Dialog(
			kytten.Frame(
				kytten.VerticalLayout([
					kytten.Document(message, width=400),
					kytten.Button("Done", on_click=teardown),
				]),
			),
			window=g.window, batch=self.batch, group=self.group,
			anchor=kytten.ANCHOR_CENTER,
			theme=self.theme
		)
