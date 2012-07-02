#! /usr/bin/env python -O
from __future__ import division

from globals import g
import states
import panes.galaxy

class Galaxy(states.States):
	"""Interactions with the galaxy."""

	def __init__(self):
		g.logging.debug('instantiating state.Galaxy')
		self.pane = panes.galaxy.Galaxy(self)
