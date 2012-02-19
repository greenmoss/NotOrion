#! /usr/bin/env python -O
from __future__ import division
import textwrap
import random

from globals import g
import states
import panes.setup

class Setup(states.States):
	"""Choose parameters for pre-game configuration."""

	galaxy_age_help_text = textwrap.dedent("""\
		Young galaxies have more mineral-rich planets and fewer planets suitable for farming.

		Mature galaxies have an even mix of farming planets and mineral-rich planets.

		Old galaxies have more planets suitable for farming and fewer mineral-rich planets.""")
	galaxy_size_help_text = textwrap.dedent("""\
		Galaxy sizes and number of stars:

		Tiny: 10 x 7 parsecs, 5 stars

		Small: 20 x 14 parsecs, 20 stars

		Medium: 27 x 19 parsecs, 36 stars

		Large: 33 x 24 parsecs, 54 stars

		Huge: 38 x 27 parsecs, 71 stars""")

	difficulty_options=["Beginner", "Easy", "Normal", "Challenging"]
	size_options=["Tiny", "Small", "Medium", "Large", "Huge"]
	age_options=["Young", "Mature", "Old"]

	def __init__(self):
		g.logging.debug('instantiating state.Setup')
		super(Setup, self).__init__()

		self.pane = panes.setup.Setup(self)
		self.pane.initialize_difficulty_dialog()
	
	def handle_difficulty_selection(self, chosen_difficulty):
		g.logging.debug('in handle_difficulty_selection, chosen_difficulty is %s'%chosen_difficulty)

		if chosen_difficulty == 'Beginner':
			# simplest: only a few stars, type yellow, no other objects
			# distribute the stars evenly over a small area
			foreground_limits = (-250,-250,250,250)
			foreground_dispersion = 100

			# generate galaxy and transition to galaxy state 
			g.galaxy.generate(
				foreground_limits,
				foreground_dispersion,
				5,                     # stars
				object_pool=['yellow'] # and all of the stars are yellow
			)
			self.pane.difficulty_dialog.teardown()
			g.application.set_state('galaxy')
			return

		if chosen_difficulty == "Easy":
			self.galaxy_size = "Small"
		elif chosen_difficulty == "Normal":
			self.galaxy_size = "Medium"
		elif chosen_difficulty == "Challenging":
			self.galaxy_size = "Large"
		else:
			raise Exception, "invalid difficulty selection: %s"%chosen_difficulty

		self.galaxy_age = "Mature"

		self.pane.difficulty_dialog.teardown()
		self.pane.initialize_options_dialog()

	def handle_galaxy_age_help(self):
		self.pane.initialize_help_dialog(self.galaxy_age_help_text)

	def handle_galaxy_age_selection(self, chosen_age):
		self.galaxy_age = chosen_age

	def handle_galaxy_size_help(self):
		self.pane.initialize_help_dialog(self.galaxy_size_help_text)

	def handle_galaxy_size_selection(self, chosen_size):
		self.galaxy_size = chosen_size
	
	def handle_galaxy_parameters(self):
		"""Given galaxy parameters, generate the galaxy.  If these parameters
		were set via a setup window, close the setup window."""

		# copying estimated proportions from
		# http://masteroforion2.blogspot.com/2006/01/moo2-map-generator.html
		if self.galaxy_size == 'Tiny':
			foreground_limits = (-350,-500,350,500)
			foreground_star_count = 5
			nebulae_count = random.randint(0,1)
		elif self.galaxy_size == 'Small':
			foreground_limits = (-700,-1000,700,1000)
			foreground_star_count = 20
			nebulae_count = random.randint(1,2)
		elif self.galaxy_size == 'Medium':
			foreground_limits = (-950,-1350,950,1350)
			foreground_star_count = 36
			nebulae_count = random.randint(2,4)
		elif self.galaxy_size == 'Large':
			foreground_limits = (-1200,-1650,1200,1650)
			foreground_star_count = 54
			nebulae_count = random.randint(3,6)
		else: #self.galaxy_size == 'Huge'
			foreground_limits = (-1350,-1900,1350,1900)
			foreground_star_count = 71
			nebulae_count = random.randint(4,7)

		g.logging.debug('foreground_star_count: %d'%foreground_star_count)

		foreground_dispersion = 100
		worm_hole_count = random.randint( int(foreground_star_count/10), int(foreground_star_count/5) )

		object_pool = []
		if self.galaxy_age == 'Young':
			# MoO2: "mineral rich"
			object_pool.extend(['black hole']*30)
			object_pool.extend(['blue']*185)
			object_pool.extend(['white']*220)
			object_pool.extend(['yellow']*97)
			object_pool.extend(['orange']*89)
			object_pool.extend(['red']*372)
			object_pool.extend(['brown']*7)

		elif self.galaxy_age == 'Mature':
			# MoO2: "average"
			object_pool.extend(['black hole']*40)
			object_pool.extend(['blue']*105)
			object_pool.extend(['white']*145)
			object_pool.extend(['yellow']*136)
			object_pool.extend(['orange']*144)
			object_pool.extend(['red']*404)
			object_pool.extend(['brown']*26)

		else: #self.galaxy_age == 'Old'
			# MoO2: "organic rich"
			object_pool.extend(['black hole']*70)
			object_pool.extend(['blue']*40)
			object_pool.extend(['white']*40)
			object_pool.extend(['yellow']*305)
			object_pool.extend(['orange']*195)
			object_pool.extend(['red']*327)
			object_pool.extend(['brown']*23)

		# generate galaxy and transition to galaxy state 
		g.galaxy.generate(
			foreground_limits,
			foreground_dispersion,
			foreground_star_count,
			worm_hole_count, 
			nebulae_count,
			object_pool
		)
	
		self.pane.options_dialog.teardown()
		g.application.set_state('galaxy')
