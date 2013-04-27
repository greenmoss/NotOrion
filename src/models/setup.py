#! python -O
"""Setup code."""
from __future__ import division
import random
import textwrap
import logging
logger = logging.getLogger(__name__)

from globals import g

class GalaxyConfig(object):
    """Keep track of all configurations for building a galaxy."""

    # TODO: nebulae_count_min/max do not belong here
    [
        limits, nebulae_count, nebulae_count_min, nebulae_count_max, object_pool, 
        size, star_count, worm_hole_count 
    ] = [None] * 8

    # age defaults to Mature
    age = 'Mature'

    # currently this is always set to 100
    dispersion = 100

    def __init__(self):
        logger.debug("instantiated GalaxyConfig")
    
    def merge(self, configs):
        """Merge a hash of values into this configuration."""
        for key, value in configs.iteritems():
            if not hasattr(self, key): raise Exception, "attempted to set nonexistent attribute %s"%key
            self.__setattr__(key, value)
    
    def is_set(self, setting):
        """Find out whether a given configuration has been set."""
        if self.__getattribute__(setting) is None:
            return False
        return True

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
    
    # TODO (debt): move setup size and age default information into galaxy model
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
        self.galaxy_config = GalaxyConfig()

    def set_galaxy_from_difficulty(self, chosen_difficulty="Normal"):
        settings_to_merge = None

        if Setup.difficulty_custom_settings.has_key(chosen_difficulty):
            settings_to_merge = Setup.difficulty_custom_settings[chosen_difficulty]

        if Setup.difficulty_preset_sizes.has_key(chosen_difficulty):
            size = Setup.difficulty_preset_sizes[chosen_difficulty]
            self.galaxy_config.size = size
            settings_to_merge = Setup.size_defaults[Setup.difficulty_preset_sizes[chosen_difficulty]]

        if settings_to_merge is None:
            raise Exception, "no settings found for difficulty %s"%chosen_difficulty

        self.galaxy_config.merge(settings_to_merge)

        if not self.galaxy_config.is_set('worm_hole_count'):
            self.galaxy_config.worm_hole_count = random.randint( 
                int(self.galaxy_config.star_count/10), 
                int(self.galaxy_config.star_count/5) 
            )

        if self.galaxy_config.is_set('nebulae_count_min') and self.galaxy_config.is_set('nebulae_count_max'):
            self.galaxy_config.nebulae_count = random.randint(
                self.galaxy_config.nebulae_count_min,
                self.galaxy_config.nebulae_count_max,
            )

    def get_galaxy_config(self):
        # ensure all necessary galaxy configs have been set
        for setting in [
            'limits',
            'star_count',
            'worm_hole_count',
            'nebulae_count'
        ]:
            if not self.galaxy_config.is_set(setting):
                raise Exception, "missing galaxy setting: %s"%setting

        if self.galaxy_config.is_set('object_pool') is False:
            self.galaxy_config.object_pool = Setup.age_defaults[self.galaxy_config.age]['object_pool']

        return self.galaxy_config
