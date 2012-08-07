#! python -O
"""Setup code."""
from __future__ import division
import random
import textwrap
import logging
logger = logging.getLogger(__name__)

from globals import g

class Setup(object):
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
	
	# defaults based on galaxy age
	# copy estimated proportions from
	# http://masteroforion2.blogspot.com/2006/01/moo2-map-generator.html
	age_defaults={
		# MoO2: "mineral rich"
		"Young":{
			"object_pool":{
				'black hole':30,
				'blue':185,
				'white':220,
				'yellow':97,
				'orange':89,
				'red':372,
				'brown':7
			}
		},
		# MoO2: "average"
		"Mature":{
			"object_pool":{
				'black hole':40,
				'blue':105,
				'white':145,
				'yellow':136,
				'orange':144,
				'red':404,
				'brown':26
			}
		},
		# MoO2: "organic rich"
		"Old":{
			"object_pool":{
				'black hole':70,
				'blue':40,
				'white':40,
				'yellow':305,
				'orange':195,
				'red':327,
				'brown':23
			}
		},
	}
	# defaults based on galaxy size
	size_defaults={
		"Tiny":{
			"limits":(-350,-500,350,500),
			"star_count":5,
			"nebulae_count_min":0,
			"nebulae_count_max":1
		},
		"Small":{
			"limits":(-700,-1000,700,1000),
			"star_count":20,
			"nebulae_count_min":1,
			"nebulae_count_max":2
		},
		"Medium":{
			"limits":(-950,-1350,950,1350),
			"star_count":36,
			"nebulae_count_min":2,
			"nebulae_count_max":4
		},
		"Large":{
			"limits":(-1200,-1650,1200,1650),
			"star_count":54,
			"nebulae_count_min":3,
			"nebulae_count_max":6
		},
		"Huge":{
			"limits":(-1350,-1900,1350,1900),
			"star_count":71,
			"nebulae_count_min":4,
			"nebulae_count_max":7
		}
	}
	# difficulty levels that use standard sizes
	difficulty_preset_sizes={
		"Easy":'Small',
		"Normal":'Medium',
		"Challenging":'Large'
	}
	# difficulty levels that use customized sizes and other settings
	difficulty_custom_settings={
		# Beginner doesn't use any of the size defaults
		# Instead, we only have a few yellow stars and no other objects
		"Beginner":{
			"limits":(-250,-250,250,250),
			"star_count":5,
			"nebulae_count":0,
			"object_pool":{"yellow":1},
			"worm_hole_count":0
		}
	}

	def __init__(self):
		logger.debug("instantiated Setup")
		self.galaxy_settings = {}

	def set_galaxy_from_difficulty(self, chosen_difficulty="Normal"):
		self.galaxy_settings['age'] = 'Mature'

		settings_to_merge = None

		if Setup.difficulty_custom_settings.has_key(chosen_difficulty):
			settings_to_merge = Setup.difficulty_custom_settings[chosen_difficulty]

		if Setup.difficulty_preset_sizes.has_key(chosen_difficulty):
			size = Setup.difficulty_preset_sizes[chosen_difficulty]
			self.galaxy_settings['size'] = size
			settings_to_merge = Setup.size_defaults[Setup.difficulty_preset_sizes[chosen_difficulty]]

		if settings_to_merge is None:
			raise Exception, "no settings found for difficulty %s"%chosen_difficulty

		# is there a better way to merge dicts?
		for key, value in settings_to_merge.iteritems():
			self.galaxy_settings[key] = value

		if not self.galaxy_settings.has_key('worm_hole_count'):
			self.galaxy_settings['worm_hole_count'] = random.randint( 
				int(self.galaxy_settings['star_count']/10), 
				int(self.galaxy_settings['star_count']/5) 
			)

		if self.galaxy_settings.has_key('nebulae_count_min') and self.galaxy_settings.has_key('nebulae_count_max'):
			self.galaxy_settings['nebulae_count'] = random.randint(
				self.galaxy_settings['nebulae_count_min'],
				self.galaxy_settings['nebulae_count_max'],
			)

		logger.debug('in set_galaxy_from_difficulty, galaxy_settings is %s',self.galaxy_settings)

	def generate_galaxy(self):
		# ensure all necessary galaxy_settings have been set
		for setting in [
			'limits',
			'star_count',
			'worm_hole_count',
			'nebulae_count'
			# object_pool and dispersion are currently optional
		]:
			if not self.galaxy_settings.has_key(setting):
				raise Exception, "missing galaxy setting: %s"%setting

		if not self.galaxy_settings.has_key('object_pool'):
			self.galaxy_settings['object_pool'] = Setup.age_defaults[self.galaxy_settings['age']]['object_pool']

		if not self.galaxy_settings.has_key('dispersion'):
			# currently this is always set to 100
			self.galaxy_settings['dispersion'] = 100

		logger.debug('in generate_galaxy, galaxy_settings is %s',self.galaxy_settings)

		g.galaxy.generate(
			self.galaxy_settings['limits'],
			self.galaxy_settings['dispersion'],
			self.galaxy_settings['star_count'],
			self.galaxy_settings['object_pool'],
			self.galaxy_settings['worm_hole_count'],
			self.galaxy_settings['nebulae_count'],
		)
