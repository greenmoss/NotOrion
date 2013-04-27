import random
import logging
logger = logging.getLogger(__name__)

import utilities

class Orbitals(object):
    """Objects that orbit stars.

    Planets, asteroid belts, gas giants. 
    Note that when stars are created they automatically populate orbitals."""

    # table from http://masteroforion2.blogspot.com/2006/01/moo2-map-generator.html
    # modified to triple the weight of orbitals with "something"
    # otherwise we get very few planets
    star_orbital_probability_table = {
        'white': {
            'nothing':40, 'asteroid belt':20, 'gas giant':20, 'planet':60
        },
        'blue': {
            'nothing':130, 'asteroid belt':20, 'gas giant':20, 'planet':60
        },
        'yellow': {
            'nothing':31, 'asteroid belt':20, 'gas giant':20, 'planet':60
        },
        'orange': {
            'nothing':25, 'asteroid belt':20, 'gas giant':20, 'planet':60
        },
        'red': {
            'nothing':130, 'asteroid belt':20, 'gas giant':20, 'planet':60
        },
        'brown': {
            'nothing':130, 'asteroid belt':20, 'gas giant':20, 'planet':60
        },
    }

    def __init__(self):
        self.planets = []
        self.asteroid_belts = []
        self.gas_giants = []

        # keep track of stars and orbits that have been set
        self.star_orbits = {}
    
    def add(self, star, orbit_number, type=None):
        if type is None:
            type = utilities.choose_from_probability(Orbitals.star_orbital_probability_table[star.type])

        if self.star_orbits.has_key(star):
            if orbit_number in self.star_orbits[star]:
                raise Exception, "already added orbit %d for star %s"%(orbit_number, star.name)
        else:
            self.star_orbits[star] = []
        self.star_orbits[star].append(orbit_number)

        if type == 'nothing':
            object = Empty(star, orbit_number)
        elif type == 'planet':
            object = Planet(star, orbit_number)
            self.planets.append(object)
        elif type == 'asteroid belt':
            object = AsteroidBelt(star, orbit_number)
            self.asteroid_belts.append(object)
        elif type == 'gas giant':
            object = GasGiant(star, orbit_number)
            self.gas_giants.append(object)
        else:
            raise Exception, 'Unknown orbital type: %s'%type

        return object

class Planet(object):
    types = [
        'arid',
        'barren',
        'desert',
        'gaia',
        'ocean',
        'radiated',
        'swamp',
        'terran',
        'toxic',
        'tundra',
    ]

    sizes = [
        'tiny',
        'small',
        'normal',
        'large',
        'huge',
    ]

    gravity = [
        'low',
        'normal',
        'heavy',
    ]

    minerals = [
        'ultra rich',
        'rich',
        'normal',
        'poor',
        'ultra poor',
    ]

    names = [
        'Prime',
        'Secundus',
        'III',
        'IV',
        'V',
    ]

    # type probability uses only "average" age
    star_type_probability_table = {
        'white': {
            'toxic':17, 'radiated':37, 'barren':27, 'desert':6, 'tundra':4,
                'ocean':2, 'swamp':1, 'arid':3, 'terran':3, 'gaia':1
        },
        'blue': {
            'toxic':16, 'radiated':50, 'barren':27, 'desert':7, 'tundra':0,
                'ocean':0, 'swamp':0, 'arid':0, 'terran':0, 'gaia':0
        },
        'yellow': {
            'toxic':13, 'radiated':27, 'barren':30, 'desert':6, 'tundra':8,
                'ocean':4, 'swamp':4, 'arid':3, 'terran':4, 'gaia':1
        },
        'orange': {
            'toxic':17, 'radiated':17, 'barren':23, 'desert':8, 'tundra':7,
                'ocean':6, 'swamp':7, 'arid':6, 'terran':8, 'gaia':1
        },
        'red': {
            'toxic':16, 'radiated':13, 'barren':50, 'desert':3, 'tundra':7,
                'ocean':2, 'swamp':2, 'arid':3, 'terran':4, 'gaia':1
        },
        'brown': {
            'toxic':21, 'radiated':29, 'barren':10, 'desert':20, 'tundra':10,
                'ocean':2, 'swamp':2, 'arid':2, 'terran':3, 'gaia':1
        },
    }

    star_richness_probability_table = {
        'white': {
            'ultra poor':0, 'poor':20, 'normal':41, 'rich':29, 'ultra rich':10,
        },
        'blue': {
            'ultra poor':0, 'poor':0, 'normal':40, 'rich':42, 'ultra rich':19,
        },
        'yellow': {
            'ultra poor':0, 'poor':30, 'normal':40, 'rich':20, 'ultra rich':9,
        },
        'orange': {
            'ultra poor':10, 'poor':40, 'normal':40, 'rich':10, 'ultra rich':0,
        },
        'red': {
            'ultra poor':19, 'poor':39, 'normal':42, 'rich':0, 'ultra rich':0,
        },
        'brown': {
            'ultra poor':5, 'poor':11, 'normal':61, 'rich':18, 'ultra rich':5,
        },
    }

    size_probability_table = {
        'tiny':1, 'small':2, 'medium':4, 'large':2, 'huge':1
    }

    size_richness_gravity_table = {
        'tiny': {
            'ultra poor':'low', 'poor':'low', 'normal':'low', 'rich':'medium', 'ultra rich':'medium',
        },
        'small': {
            'ultra poor':'low', 'poor':'low', 'normal':'medium', 'rich':'medium', 'ultra rich':'medium',
        },
        'medium': {
            'ultra poor':'low', 'poor':'medium', 'normal':'medium', 'rich':'medium', 'ultra rich':'high',
        },
        'large': {
            'ultra poor':'medium', 'poor':'medium', 'normal':'medium', 'rich':'high', 'ultra rich':'high',
        },
        'huge': {
            'ultra poor':'medium', 'poor':'medium', 'normal':'high', 'rich':'high', 'ultra rich':'high',
        },
    }

    def __init__(self, star, orbit_number):
        self.star = star
        self.orbit_number = orbit_number
        self.name = Planet.names[orbit_number]
        self.type = utilities.choose_from_probability(Planet.star_type_probability_table[self.star.type])
        self.size = utilities.choose_from_probability(Planet.size_probability_table)
        self.richness = utilities.choose_from_probability(Planet.star_richness_probability_table[self.star.type])
        self.gravity = Planet.size_richness_gravity_table[self.size][self.richness]
        logger.debug("%s: %s %s %s %s", self.name, self.size, self.type, self.richness, self.gravity)

class Empty(object):
    """An empty orbit."""
    def __init__(self, star, orbit_number):
        logger.debug('')
        self.star = star
        self.orbit_number = orbit_number

class GasGiant(object):
    def __init__(self, star, orbit_number):
        logger.debug('gas giant')
        self.star = star
        self.orbit_number = orbit_number

class AsteroidBelt(object):
    def __init__(self, star, orbit_number):
        logger.debug('asteroid belt')
        self.star = star
        self.orbit_number = orbit_number
