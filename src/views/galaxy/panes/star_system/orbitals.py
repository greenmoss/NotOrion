import logging
logger = logging.getLogger(__name__)
import ctypes
import os

import pyglet
from pyglet.gl import *

import views.galaxy.map.stars
import utilities
import mesh
from globals import g

class Orbitals(object):
    def __init__(self, star_system_view):
        self.star_system_view = star_system_view
        self.orbital = Orbital(self.star_system_view)

    def draw(self, look, rotate):

        self.orbital.draw(look, rotate)

class Orbital(object):

    def __init__(self, star_system_view):
        self.star_system_view = star_system_view
        imported_path = os.path.join(g.paths['meshes_dir'], 'uv_sphere.obj')
        self.mesh = mesh.Wavefront(imported_path)

    def draw(self, look, rotate):
        glTranslated(look[0], look[1], look[2])
        glRotated(rotate[0], rotate[1], rotate[2], rotate[3])
        self.mesh.draw()
