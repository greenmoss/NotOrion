from __future__ import division
import logging
logger = logging.getLogger(__name__)

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
    center = (int(width/2),int(height-text_height)/2)

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

    def derive_dimensions(self):
        star_map_coordinate = self.state.map_coordinate(self.model_star.coordinates, 'model').as_default_window()

        offset_x = star_map_coordinate.x
        offset_y = star_map_coordinate.y

        top = offset_y + self.half_height
        right = offset_x + self.half_width
        bottom = offset_y - self.half_height
        left = offset_x - self.half_width

        max_top = g.window.height - StarSystem.edge_offset
        max_right = g.window.width - StarSystem.edge_offset
        min_bottom = StarSystem.edge_offset
        min_left = StarSystem.edge_offset

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
        self.orbitals.draw()

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

    def handle_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.visible:
            # recalculate position
            self.show(self.model_star)

    def handle_resize(self, width, height):
        if self.visible:
            # recalculate position
            self.show(self.model_star)
