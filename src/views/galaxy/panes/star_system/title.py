from __future__ import division
import pyglet

class Title(object):
    edge_offset = 10

    def __init__(self, star_system_view):
        self.star_system_view = star_system_view

        self.label = pyglet.text.Label(
            '', # text will be filled in later
            font_name='Arial', font_size=12,
            # x and y coordinates of label will immediately be recalculated, but are required to initialize the label
            x=0, y=0,
            anchor_x='center', anchor_y='top')

    def prepare(self):
        self.label.text = self.star_system_view.model_star.name
        self.label.x = self.star_system_view.corners['left'] + self.star_system_view.center[0]
        self.label.y = self.star_system_view.corners['top'] - Title.edge_offset

    def draw(self):
        self.label.draw()
