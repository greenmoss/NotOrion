from __future__ import division
import logging
logger = logging.getLogger(__name__)

import pyglet
from pyglet.gl import *

from globals import g
import common

class MiniMap(common.Pane):
    # offset from right/bottom of window
    offset = 20
    # either width or height, whichever is larger
    size = 75

    background_color = (0, 0, 0, 220) # transparent black
    border_color = (32, 32, 32) # dark grey
    active_area_color = (48, 48, 48) # light grey

    def __init__(self, state):
        self.state = state
        map_height = g.galaxy.top_bounding_y - g.galaxy.bottom_bounding_y
        map_width = g.galaxy.right_bounding_x - g.galaxy.left_bounding_x
        ratio = map_height/map_width
        if map_width > map_height:
            self.width = MiniMap.size
            self.height = self.width*ratio
        else: #map_width <= map_height
            self.height = MiniMap.size
            self.width = self.height/ratio

        # ratio of galaxy coordinates to mini-map coordinates
        self.ratio = self.width/map_width

        # what we will be drawing
        self.bg_vertex_list = pyglet.graphics.vertex_list( 
            4, 'v2f',
            ('c4B/static', MiniMap.background_color*4)
        )
        self.border_vertex_list = pyglet.graphics.vertex_list( 
            4, 'v2f',
            ('c3B/static', MiniMap.border_color*4)
        )
        self.active_area_vertex_list = pyglet.graphics.vertex_list( 
            4, 'v2f',
            ('c3B/static', MiniMap.active_area_color*4)
        )

        self.derive_dimensions()

    # dimensions of mini map vary with scale and window size
    def derive_dimensions(self):
        # where are the map view coordinates on the playing field?
        main_map_view_right_top = self.state.map_coordinate(
            (g.window.width, g.window.height), 'default_window'
        ).as_model()
        main_map_view_left_bottom = self.state.map_coordinate(
            (0, 0), 'default_window'
        ).as_model()

        # hide the mini-map if the entire playing field is visible
        # the integer modifiers create a minimum margin around stars before showing the mini-map
        if (
            (main_map_view_right_top.x >= g.galaxy.right_bounding_x+60) and
            (main_map_view_right_top.y >= g.galaxy.top_bounding_y+20) and
            (main_map_view_left_bottom.x <= g.galaxy.left_bounding_x-60) and
            (main_map_view_left_bottom.y <= g.galaxy.bottom_bounding_y-40)
        ):
            self.visible = False
            return

        self.corners = {
            'top':MiniMap.offset + self.height,
            'right':-MiniMap.offset + g.window.width,
            'bottom':MiniMap.offset,
            'left':-MiniMap.offset + g.window.width - self.width
        }

        center = (
            self.corners['right']-(self.corners['right']-self.corners['left'])/2.0,
            self.corners['top']-(self.corners['top']-self.corners['bottom'])/2.0,
        )

        # position of viewing area within playing field
        self.window_corners = {
            'top':center[1]+int(main_map_view_right_top.y*self.ratio),
            'right':center[0]+int(main_map_view_right_top.x*self.ratio),
            'bottom':center[1]+int(main_map_view_left_bottom.y*self.ratio),
            'left':center[0]+int(main_map_view_left_bottom.x*self.ratio),
        }

        # ensure window_corners do not fall outside corners
        if not(self.corners['bottom'] < self.window_corners['top'] < self.corners['top']):
            self.window_corners['top'] = self.corners['top']
        if not(self.corners['left'] < self.window_corners['right'] < self.corners['right']):
            self.window_corners['right'] = self.corners['right']
        if not(self.corners['top'] > self.window_corners['bottom'] > self.corners['bottom']):
            self.window_corners['bottom'] = self.corners['bottom']
        if not(self.corners['right'] > self.window_corners['left'] > self.corners['left']):
            self.window_corners['left'] = self.corners['left']

        # update all drawing vertices
        self.active_area_vertex_list.vertices = (
            self.window_corners['right'], self.window_corners['top'],
            self.window_corners['right'], self.window_corners['bottom'],
            self.window_corners['left'], self.window_corners['bottom'],
            self.window_corners['left'], self.window_corners['top'],
        )
        self.bg_vertex_list.vertices = (
            self.corners['right'], self.corners['top'],
            self.corners['right'], self.corners['bottom'],
            self.corners['left'], self.corners['bottom'],
            self.corners['left'], self.corners['top'],
        )
        self.border_vertex_list.vertices = (
            self.corners['right'], self.corners['top'],
            self.corners['right'], self.corners['bottom'],
            self.corners['left'], self.corners['bottom'],
            self.corners['left'], self.corners['top'],
        )

        # after all mini map parameters are calculated, display the mini map
        self.visible = True
    
    def handle_draw(self):
        if not self.visible:
            return

        self.drawing_origin_to_lower_left()

        glPushMatrix()

        # translucent gray rectangle behind mini-map
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.bg_vertex_list.draw(pyglet.gl.GL_QUADS)

        # borders of mini-map
        self.border_vertex_list.draw(pyglet.gl.GL_LINE_LOOP)

        # borders of mini-window within mini-map
        self.active_area_vertex_list.draw(pyglet.gl.GL_LINE_LOOP)

        glPopMatrix()
    
    def handle_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.state.vetoed_drag:
            return
        self.derive_dimensions()

    def handle_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.derive_dimensions()

    def handle_resize(self, width, height):
        self.derive_dimensions()

