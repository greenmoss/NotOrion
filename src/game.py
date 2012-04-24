#! /usr/bin/env python -O
""" This contains game initialization code only. All implementation details
should occur elsewhere.  

Importantly, the single game-wide global object is initialized *first* so it
can be reused across the rest of the game.  """
from globals import g
g.logging.basicConfig(level=g.logging.DEBUG)

import application
g.application = application.Application()
g.application.configure()
g.application.run()
