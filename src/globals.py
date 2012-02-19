#! /usr/bin/env python -O
""" This contains one object, with one instance, to contain globals that will
be used across the entire game.

With the exception of external modules such as logging that will be shared and
imported once, object properties are initialized but *not* assigned here.  """

import logging

class Globals(object):
	
	def __init__(self):
		self.logging = logging
		self.application = None
		self.window = None
		self.galaxy = None
		
g = Globals()
