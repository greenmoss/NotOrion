import os
import sys
import unittest

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'src'
    )
)

from globals import g

import application
import script

class TestGeneratedGalaxy(unittest.TestCase):
    def testCompletion(self):
        "Game should launch, generate galaxy, and exit with no errors."
        g.application = application.Application()

        # set our settings here instead of from argparse
        settings = application.Settings()
        settings.difficulty = 'Normal'

        g.application.configure(settings, script.Script())
        g.application.script.schedule_exit()
        g.application.run()
