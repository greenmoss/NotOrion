#! /usr/bin/env python -O
""" This contains game initialization code only. All implementation details
should occur elsewhere.  

Importantly, the single game-wide global object is initialized *first* so it
can be reused across the rest of the game.  """
import os
import sys

sys.path.append(
	os.path.join(
		os.path.dirname(os.path.abspath(__file__)),
		'src'
	)
)

from globals import g

import application
g.application = application.Application()
g.application.configure()
g.application.run()
