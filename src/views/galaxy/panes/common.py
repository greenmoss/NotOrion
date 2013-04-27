import pyglet
from pyglet.gl import *

from globals import g

class Pane(object):
    """Common methods for drawing panes."""

    def drawing_origin_to_lower_left(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, g.window.width, 0, g.window.height)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
