from __future__ import division
import os
import logging
logger = logging.getLogger(__name__)

import pyglet
from pyglet.gl import *
import kytten

from globals import g
import views

class Setup(views.View):

	def __init__(self, state):
		logger.debug('instantiating views.Setup')

		self.state = state

		self.theme = kytten.Theme(
			os.path.join(g.paths['resources_dir'], 'gui'), 
			override={
				"gui_color": [64, 128, 255, 255],
				"font_size": 12
			}
		)
		self.batch = pyglet.graphics.Batch()
		self.group = pyglet.graphics.OrderedGroup(0)
	
	def initialize_difficulty_dialog(self):
		self.difficulty_dialog = kytten.Dialog(
			kytten.TitleFrame(
				"Choose Game Difficulty",
				kytten.VerticalLayout([
					kytten.Menu(
						options=g.setup.difficulty_options,
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
							options=g.setup.size_options,
							selected=g.setup.galaxy_config.size,
							on_select=self.state.handle_galaxy_size_selection,
						),
						kytten.Button("?", on_click=self.state.handle_galaxy_size_help),
					]),
					kytten.HorizontalLayout([
						kytten.Label("Galaxy Age"),
						None,
						kytten.Dropdown(
							options=g.setup.age_options,
							selected=g.setup.galaxy_config.age,
							on_select=self.state.handle_galaxy_age_selection,
						),
						kytten.Button("?", on_click=self.state.handle_galaxy_age_help),
					]),
					kytten.Button("Continue", on_click=self.state.handle_game_options_continue),
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

	# pyglet window handlers go here
	def on_draw(self):
		glClearColor(0.0, 0.0, 0.0, 0)
		g.window.clear()
		self.batch.draw()
