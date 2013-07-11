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
    light_color = {
        'blue': [0.30, 0.69, 1.0, 1.0],
        'brown': [0.27, 0.09, 0.0, 1.0],
        'orange': [1.0, 0.57, 0.0, 1.0],
        'red': [0.86, 0.08, 0.24, 1.0],
        'white': [1.0, 1.0, 1.0, 1.0],
        'yellow': [1.0, 1.0, 0.0, 1.0]
    }

    def __init__(self, star_system_view):
        self.star_system_view = star_system_view

        self.mesh = meshes.Sphere()
        self.mesh.set_texture('star_surface.png')
        self.mesh.unset_diffuse()
        self.mesh.unset_ambient()
        self.mesh.unset_specular()
        self.lightfv = ctypes.c_float * 4
        self.persp = [-5., 1., 300.]

    def prepare(self, display_box):
        self.display_box = display_box
        self.port_height = display_box['top'] - display_box['bottom']
        self.port_width = display_box['right'] - display_box['left']

        star_type = self.star_system_view.model_star.type
        self.mesh.set_emissive(Star.light_color[star_type])

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

        glLoadIdentity()

        glPushMatrix()
        glTranslatef(Star.look[0], Star.look[1], Star.look[2])

        self.mesh.draw()
        glPopMatrix()

        glPopAttrib(GL_MODELVIEW)
