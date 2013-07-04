import logging
logger = logging.getLogger(__name__)
import ctypes

import pyglet
from pyglet.gl import *

import views.galaxy.map.stars
import meshes

class Star(object):
    look = [1.04, 0.0, -6.0]
    light_pos = [-10, 0, 0, 0]
    diffuse_light = {
        'blue': [0.65, 0.85, 1.0, 0.0],
        'brown': [0.55, 0.36, 0.1, 0.0],
        'orange': [0.92, 0.65, 0.15, 0.0],
        'red': [0.86, 0.17, 0.0, 0.0],
        'white': [1.0, 1.0, 1.0, 0.0],
        'yellow': [0.99, 0.97, 0.22, 0.0]
    }

    def __init__(self, star_system_view):
        self.star_system_view = star_system_view

        self.mesh = meshes.Sphere()
        self.mesh.set_texture('star_surface.png')
        self.lightfv = ctypes.c_float * 4
        self.persp = [-5., 1., 300.]

    def prepare(self, display_box):
        self.display_box = display_box
        self.port_height = display_box['top'] - display_box['bottom']
        self.port_width = display_box['right'] - display_box['left']

        star_type = self.star_system_view.model_star.type
        self.light_dif = Star.diffuse_light[star_type]

    def draw(self):
        glLoadIdentity()
        gluPerspective(self.persp[0],
            float(self.port_width)/self.port_height,
            self.persp[1],
            self.persp[2])

        glViewport(
            self.display_box['left'],
            self.display_box['bottom'],
            self.port_width,
            self.port_height)

        glPushAttrib(GL_MODELVIEW)
        glMatrixMode(GL_MODELVIEW)

        glPushAttrib(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, self.lightfv(Star.light_pos[0],
            Star.light_pos[1], Star.light_pos[2], Star.light_pos[3]))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.lightfv(self.light_dif[0],
            self.light_dif[1], self.light_dif[2], self.light_dif[3]))
        glEnable(GL_LIGHT0)
        glPopAttrib(GL_LIGHT0)

        glLoadIdentity()

        glPushMatrix()
        glTranslatef(Star.look[0], Star.look[1], Star.look[2])

        self.mesh.draw()
        glPopMatrix()

        glPopAttrib(GL_MODELVIEW)
