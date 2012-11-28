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

class TestNotOrion(unittest.TestCase):
	def testComplete(self):
		"Game should launch and exit with no errors."
		g.application = application.Application()
		g.application.configure(args={})
		g.application.run()
