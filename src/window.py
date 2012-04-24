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

		self.register_event_type('on_update')
		pyglet.clock.schedule(self.update)

		self.set_visible()

	# this activates kytten in state.setup; it should move into panes.setup
	def update(self, dt):
		self.dispatch_event('on_update', dt)
