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

    def draw(self):
        self.orbital.draw()

class Orbital(object):

    def __init__(self, star_system_view):
        self.star_system_view = star_system_view
        imported_path = os.path.join(g.paths['meshes_dir'], 'uv_sphere.obj')
        self.mesh = mesh.Wavefront(imported_path)

    def draw(self):
        fourfv = ctypes.c_float * 4
        glLightfv(GL_LIGHT0, GL_POSITION, fourfv(10, 20, 20, 0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, fourfv(0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, fourfv(0.8, 0.8, 0.8, 1.0))
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        gluLookAt(0, 3, 3, 0, 0, 0, 0, 1, 0)
        self.mesh.draw()
