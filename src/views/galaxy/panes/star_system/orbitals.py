import logging
logger = logging.getLogger(__name__)
import ctypes

import pyglet
from pyglet.gl import *

import views.galaxy.map.stars
import utilities
import meshes
from globals import g
import models

class Orbitals(object):
    def __init__(self, star_system_view):
        self.star_system_view = star_system_view
        self.all = []
        for orbit in range(0, 5):
            self.all.append(Orbital(self.star_system_view))

        self.light_amb = [0.1, 0.1, 0.1, 1.0]
        self.light_dif = [1.0, 1.0, 1.0, 1.0]

    def prepare(self, display_box):
        #logger.debug('display_box: %s'%self.display_box)
        self.orbital_width = int( (display_box['right'] - display_box['left']) / 5 )
        self.height = display_box['top'] - display_box['bottom']

        # adjust lighting based on star color
        star_type = self.star_system_view.model_star.type
        if star_type == 'blue':
            self.light_dif = [2.0, 2.0, 4.0, 1.0]
        elif star_type == 'brown':
            self.light_dif = [0.6, 0.4, 0.4, 1.0]
        elif star_type == 'orange':
            self.light_dif = [1.0, 0.9, 0.7, 1.0]
        elif star_type == 'red':
            self.light_dif = [0.8, 0.7, 0.6, 1.0]
        elif star_type == 'white':
            self.light_dif = [2.0, 2.0, 2.0, 1.0]
        elif star_type == 'yellow':
            self.light_dif = [1.0, 1.0, 0.9, 1.0]
        else:
            self.light_dif = [1.0, 1.0, 1.0, 1.0]

        model_orbitals = self.star_system_view.model_star.orbits
        for orbital_index in range(0, len(self.all)):
            orbital = self.all[orbital_index]
            model_orbital = model_orbitals[orbital_index]
            orbital_display_box = {
                'top':display_box['top'],
                'right':display_box['left'] + ((orbital_index + 1) * self.orbital_width),
                'bottom':display_box['bottom'],
                'left':display_box['left'] + (orbital_index * self.orbital_width),
            }
            orbital.prepare(model_orbital, orbital_display_box)

    def draw(self):
        glLoadIdentity()
        gluPerspective(self.star_system_view.persp[0],
            float(self.orbital_width)/self.height,
            self.star_system_view.persp[1],
            self.star_system_view.persp[2])

        for orbital in self.all:
            orbital.draw(self.light_amb, self.light_dif)

class Orbital(object):
    planet_z_depth = {
            'tiny': -225,
            'small': -175,
            'medium': -125,
            'large': -100,
            'huge': -75
    }

    def __init__(self, star_system_view):
        self.star_system_view = star_system_view
        self.model = None
        self.showing = False

        self.lightfv = ctypes.c_float * 4
        self.light_pos = [10, 0, 3, 0]
        self.look = [0, 0, -100]
        self.rotate = [0, 0, 0, 0]

        self.planet = meshes.Sphere()

    def prepare(self, model_orbital, display_box):
        self.model = model_orbital
        if type(self.model) == models.galaxy.orbitals.Planet:
            self.showing = True
            self.look = [0, 0, Orbital.planet_z_depth[self.model.size]]
            self.planet.set_texture('%s.png'%self.model.type)
        else:
            self.showing = False
            return

        self.display_box = display_box
        self.port_height = display_box['top'] - display_box['bottom']
        self.port_width = display_box['right'] - display_box['left']

    def draw(self, light_amb, light_dif):
        if self.showing is False: return
        #print 'showing orbital %d'%self.model.orbit_number

        glPushAttrib(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, self.lightfv(self.light_pos[0],
            self.light_pos[1], self.light_pos[2], self.light_pos[3]))
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.lightfv(light_amb[0],
            light_amb[1], light_amb[2], light_amb[3]))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.lightfv(light_dif[0],
            light_dif[1], light_dif[2], light_dif[3]))
        glEnable(GL_LIGHT0)

        glViewport(
            self.display_box['left'],
            self.display_box['bottom'],
            self.port_width,
            self.port_height)

        glPushAttrib(GL_MODELVIEW)
        glMatrixMode(GL_MODELVIEW)

        glLoadIdentity()

        glTranslated(self.look[0], self.look[1], self.look[2])
        glRotated(self.rotate[0], self.rotate[1], self.rotate[2], self.rotate[3])

        self.planet.draw()

        glPopAttrib(GL_LIGHT0)
        glPopAttrib(GL_MODELVIEW)
