#! python -O
from __future__ import division

from pyglet.gl import *
import pyglet

from globals import g

class Window(pyglet.window.Window):
	"""The game's GUI window. This is a subclassed pyglet window."""

	def __init__(self):
		super(Window, self).__init__(
			resizable=True, 
			caption='NotOrion', 
			width=800, height=600, 
			visible=False,
		)

		self.set_minimum_size(800, 600)

		self.key_handlers = {
			pyglet.window.key.ESCAPE: lambda: g.application.exit(),
			pyglet.window.key.Q: lambda: g.application.exit(),
		}

		self.register_event_type('on_update')
		pyglet.clock.schedule(self.update)

		self.set_visible()

	# TODO (debt) move this into views.setup
	# this activates kytten in state.setup
	def update(self, dt):
		self.dispatch_event('on_update', dt)

	def on_key_press(self, symbol, modifiers):
		handler = self.key_handlers.get(symbol, lambda: None)
		handler()
