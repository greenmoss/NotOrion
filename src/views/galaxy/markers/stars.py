from __future__ import division

import pyglet

from globals import g
import views
import hover_objects

class Stars(hover_objects.HoverGroup):
    visible_batch = pyglet.graphics.Batch()
    invisible_batch = pyglet.graphics.Batch()

    def __init__(self, map_view):
        self.map_view = map_view
        self.map_view_type = views.galaxy.map.stars.Star
        super(Stars, self).__init__()

        # configure marker image animation
        image = pyglet.resource.image('star_marker_animation.png')
        image_seq = pyglet.image.ImageGrid(image, 1, 24)
        for image in image_seq:
            image.anchor_x = image.width // 2
            image.anchor_y = image.height // 2
        animation = pyglet.image.Animation.from_image_sequence(image_seq, 0.04)

        for map_star in self.map_view.stars.values():
            self.markers[map_star] = Marker(
                map_star, animation
            )
    
    def draw(self):
        Stars.visible_batch.draw()

class Marker(object):
    def __init__(self, map_object, animation):
        self.map_object = map_object
        self.color_stack = {}
        self.color = (255,255,255)
        self.star_marker_color_priority = 2

        self.sprite = pyglet.sprite.Sprite(
            animation,
            self.map_object.sprite.x,
            self.map_object.sprite.y
        )

        self.hide()
    
    def show(self, requestor=None):
        if requestor is None:
            requestor = self
        if self.color_stack.has_key(requestor.star_marker_color_priority):
            return
        self.color_stack[requestor.star_marker_color_priority] = requestor
        self.set_coordinates()

        self.show_top_color()

        self.visible = True
        self.sprite.batch = Stars.visible_batch
    
    def hide(self, requestor=None):
        if requestor is None:
            requestor = self
        if not self.color_stack.has_key(requestor.star_marker_color_priority):
            return
        self.color_stack.pop(requestor.star_marker_color_priority)

        if len(self.color_stack) == 0:
            self.visible = False
            self.sprite.batch = Stars.invisible_batch
            return

        self.show_top_color()
    
    def show_top_color(self):
        # prefer my own native color
        top = 0
        for number, requestor in self.color_stack.iteritems():
            if number > top:
                top = number
        self.sprite.color = self.color_stack[top].color
    
    def set_coordinates(self):
        self.sprite.x = self.map_object.sprite.x
        self.sprite.y = self.map_object.sprite.y
