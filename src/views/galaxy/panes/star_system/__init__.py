from __future__ import division
import logging
logger = logging.getLogger(__name__)
import ctypes

import pyglet
from pyglet.gl import *

from globals import g
from .. import common
import views.galaxy.map.stars
import title
import star
import orbitals

class StarSystem(common.Pane):
    """A window pane showing a star system."""
    height = 225
    width = 750
    text_height = 25
    # system name on top, orbital labels on bottom
    text_height = 25
    center = (int(width/2),int(height-text_height)/2)
    orbital_view_height = height - (text_height * 2)

    # divide into display areas for star and orbitals
    # 11 parts: 1 for partial star on left side, 2 for each of the 5
    # orbitals
    star_right_corner = int(width / 11)
    orbital_view_width = star_right_corner * 2
    orbital_positions = []
    for position in range(0,5):
        push_rightwards = (position * orbital_view_width)
        left = star_right_corner + push_rightwards
        right = star_right_corner + push_rightwards + orbital_view_width
        orbital_positions.append({'left': left, 'right': right})
    print orbital_positions

    background_color = (0, 0, 0) # black
    border_color = (32, 32, 32) # dark grey
    edge_offset = 10 # window should be no closer to edge than this

    def __init__(self, state):
        self.state = state
        self.model_star = None
        self.half_height = int(StarSystem.height/2)
        self.half_width = int(StarSystem.width/2)

        self.bg_vertex_list = pyglet.graphics.vertex_list( 
            4, 'v2f',
            ('c3B/static', StarSystem.background_color*4)
        )
        self.border_vertex_list = pyglet.graphics.vertex_list( 
            4, 'v2f',
            ('c3B/static', StarSystem.border_color*4)
        )

        self.visible = False
        self.clicked_on_me = False

        self.title = title.Title(self)
        self.star = star.Star(self)
        self.orbitals = orbitals.Orbitals(self)

        self.light_pos = [10, 0, 3, 0]
        self.light_amb = [0.1, 0.1, 0.1, 1.0]
        self.light_dif = [1.0, 1.0, 1.0, 1.0]
        self.persp = [-5., 50., 200.]
        self.look = [0, 0, -100]
        self.rotate = [0, 0, 0, 0]

        self.mod = self.light_pos
        self.pos = 0

    def derive_dimensions(self):
        star_map_coordinate = self.state.map_coordinate(self.model_star.coordinates, 'model').as_default_window()

        offset_x = star_map_coordinate.x
        offset_y = star_map_coordinate.y

        top = int(offset_y + self.half_height)
        right = int(offset_x + self.half_width)
        bottom = int(offset_y - self.half_height)
        left = int(offset_x - self.half_width)

        max_top = int(g.window.height - StarSystem.edge_offset)
        max_right = int(g.window.width - StarSystem.edge_offset)
        min_bottom = int(StarSystem.edge_offset)
        min_left = int(StarSystem.edge_offset)

        if top > max_top:
            difference = top - max_top
            top = top - difference
            bottom = bottom - difference

        if right > max_right:
            difference = right - max_right
            right = right - difference
            left = left - difference

        if bottom < min_bottom:
            difference = min_bottom - bottom
            top = top + difference
            bottom = bottom + difference

        if left < min_left:
            difference = min_left - left
            right = right + difference
            left = left + difference

        self.bg_vertex_list.vertices = (
            right, top,
            right, bottom,
            left, bottom,
            left, top,
        )
        self.border_vertex_list.vertices = (
            right, top,
            right, bottom,
            left, bottom,
            left, top,
        )

        self.corners = {'top':top, 'right':right, 'bottom':bottom, 'left':left}
        logger.debug(self.corners)

    def hide(self):
        self.model_star = None
        self.visible = False

    def load(self, star):
        if star is None:
            return
        self.show(star)

    def save(self):
        return self.model_star

    def show(self, star):
        self.model_star = star
        self.derive_dimensions()
        self.title.show()
        self.star.show()
        self.visible = True

    def handle_draw(self):
        if not self.visible:
            return

        self.drawing_origin_to_lower_left()
        self.bg_vertex_list.draw(pyglet.gl.GL_QUADS)
        self.border_vertex_list.draw(pyglet.gl.GL_LINE_LOOP)
        self.title.draw()
        self.star.draw()

        glPushAttrib(GL_DEPTH_TEST)
        glEnable(GL_DEPTH_TEST)

        glPushAttrib(GL_COLOR_MATERIAL)
        glEnable(GL_COLOR_MATERIAL)

        glPushAttrib(GL_LIGHTING)
        glEnable(GL_LIGHTING)

        glPushAttrib(GL_PROJECTION)
        glMatrixMode(GL_PROJECTION)

        port_height = self.corners['top'] - self.corners['bottom']
        port_width = StarSystem.orbital_view_width

        glLoadIdentity()
        gluPerspective(self.persp[0],
                float(port_width)/port_height, self.persp[1],
                self.persp[2])

        fourfv = ctypes.c_float * 4









        glPushAttrib(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, fourfv(self.light_pos[0],
            self.light_pos[1], self.light_pos[2], self.light_pos[3]))
        glLightfv(GL_LIGHT0, GL_AMBIENT, fourfv(self.light_amb[0],
            self.light_amb[1], self.light_amb[2], self.light_amb[3]))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, fourfv(self.light_dif[0],
            self.light_dif[1], self.light_dif[2], self.light_dif[3]))
        glEnable(GL_LIGHT0)

        glViewport(
             self.corners['left'] + StarSystem.orbital_positions[0]['left'],
             self.corners['bottom'],
             port_width,
             port_height)

        glPushAttrib(GL_MODELVIEW)
        glMatrixMode(GL_MODELVIEW)

        glLoadIdentity()

        self.orbitals.draw(self.look, self.rotate)

        glPopAttrib(GL_LIGHT0)
        glPopAttrib(GL_MODELVIEW)



        glPushAttrib(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, fourfv(self.light_pos[0],
            self.light_pos[1], self.light_pos[2], self.light_pos[3]))
        glLightfv(GL_LIGHT0, GL_AMBIENT, fourfv(self.light_amb[0],
            self.light_amb[1], self.light_amb[2], self.light_amb[3]))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, fourfv(self.light_dif[0],
            self.light_dif[1], self.light_dif[2], self.light_dif[3]))
        glEnable(GL_LIGHT0)

        glViewport(
             self.corners['left'] + StarSystem.orbital_positions[1]['left'],
             self.corners['bottom'],
             port_width,
             port_height)

        glPushAttrib(GL_MODELVIEW)
        glMatrixMode(GL_MODELVIEW)

        glLoadIdentity()

        self.orbitals.draw(self.look, self.rotate)

        glPopAttrib(GL_LIGHT0)
        glPopAttrib(GL_MODELVIEW)



        glPushAttrib(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, fourfv(self.light_pos[0],
            self.light_pos[1], self.light_pos[2], self.light_pos[3]))
        glLightfv(GL_LIGHT0, GL_AMBIENT, fourfv(self.light_amb[0],
            self.light_amb[1], self.light_amb[2], self.light_amb[3]))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, fourfv(self.light_dif[0],
            self.light_dif[1], self.light_dif[2], self.light_dif[3]))
        glEnable(GL_LIGHT0)

        glViewport(
             self.corners['left'] + StarSystem.orbital_positions[2]['left'],
             self.corners['bottom'],
             port_width,
             port_height)

        glPushAttrib(GL_MODELVIEW)
        glMatrixMode(GL_MODELVIEW)

        glLoadIdentity()

        self.orbitals.draw(self.look, self.rotate)

        glPopAttrib(GL_LIGHT0)
        glPopAttrib(GL_MODELVIEW)



        glPushAttrib(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, fourfv(self.light_pos[0],
            self.light_pos[1], self.light_pos[2], self.light_pos[3]))
        glLightfv(GL_LIGHT0, GL_AMBIENT, fourfv(self.light_amb[0],
            self.light_amb[1], self.light_amb[2], self.light_amb[3]))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, fourfv(self.light_dif[0],
            self.light_dif[1], self.light_dif[2], self.light_dif[3]))
        glEnable(GL_LIGHT0)

        glViewport(
             self.corners['left'] + StarSystem.orbital_positions[3]['left'],
             self.corners['bottom'],
             port_width,
             port_height)

        glPushAttrib(GL_MODELVIEW)
        glMatrixMode(GL_MODELVIEW)

        glLoadIdentity()

        self.orbitals.draw(self.look, self.rotate)

        glPopAttrib(GL_LIGHT0)
        glPopAttrib(GL_MODELVIEW)



        glPushAttrib(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, fourfv(self.light_pos[0],
            self.light_pos[1], self.light_pos[2], self.light_pos[3]))
        glLightfv(GL_LIGHT0, GL_AMBIENT, fourfv(self.light_amb[0],
            self.light_amb[1], self.light_amb[2], self.light_amb[3]))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, fourfv(self.light_dif[0],
            self.light_dif[1], self.light_dif[2], self.light_dif[3]))
        glEnable(GL_LIGHT0)

        glViewport(
             self.corners['left'] + StarSystem.orbital_positions[4]['left'],
             self.corners['bottom'],
             port_width,
             port_height)

        glPushAttrib(GL_MODELVIEW)
        glMatrixMode(GL_MODELVIEW)

        glLoadIdentity()

        self.orbitals.draw(self.look, self.rotate)

        glPopAttrib(GL_LIGHT0)
        glPopAttrib(GL_MODELVIEW)



























        glPopAttrib(GL_PROJECTION)
        glPopAttrib(GL_DEPTH_TEST)
        glPopAttrib(GL_COLOR_MATERIAL)
        glPopAttrib(GL_LIGHTING)

    def handle_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.clicked_on_me:
            self.state.vetoed_drag = self
            return

        self.hide()

    def handle_mouse_press(self, x, y, button, modifiers):
        self.clicked_on_me = False
        if not pyglet.window.mouse.LEFT:
            return

        # if we clicked on nothing
        objects_under_cursor = self.state.masks.detected_objects()
        if len(objects_under_cursor) == 0:
            self.hide()
            return

        # if we clicked within an already-open window
        for map_object in objects_under_cursor:
            if type(map_object) is StarSystem:
                self.clicked_on_me = True
                return

        # if we clicked on a star in the map view
        map_star = None
        for map_object in objects_under_cursor:
            if type(map_object) is not views.galaxy.map.stars.Star:
                continue
            map_star = map_object
        if map_star is None:
            self.hide()
            return

        self.clicked_on_me = True
        self.show(map_star.physical_star)

    #def handle_key_press(self, *args):
    #    self.orbitals.handle_key_press(*args)

    def handle_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.Z:
            print 'next position'
            self.pos += 1

        if symbol == pyglet.window.key.A:
            print 'tweak: self.light_pos'
            self.mod = self.light_pos
        elif symbol == pyglet.window.key.S:
            print 'tweak: self.light_amb'
            self.mod = self.light_amb
        elif symbol == pyglet.window.key.D:
            print 'tweak: self.light_dif'
            self.mod = self.light_dif
        elif symbol == pyglet.window.key.F:
            print 'tweak: self.persp'
            self.mod = self.persp
        elif symbol == pyglet.window.key.G:
            print 'tweak: self.look'
            self.mod = self.look
        elif symbol == pyglet.window.key.H:
            print 'tweak: self.rotate'
            self.mod = self.rotate

        if (self.pos >= len(self.mod)): self.pos = 0

        unit = 1
        if type(self.mod[0]) == type(1.0):
            unit = .1

        if symbol == pyglet.window.key.X:
            print 'add %s'%unit
            self.mod[self.pos] += unit
        elif symbol == pyglet.window.key.C:
            print 'subtract %s'%unit
            self.mod[self.pos] -= unit

        print "modifiers: %s; selected: %s (%s)"%(self.mod, self.pos,
                self.mod[self.pos])

    def handle_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.visible:
            # recalculate position
            self.show(self.model_star)

    def handle_resize(self, width, height):
        if self.visible:
            # recalculate position
            self.show(self.model_star)
