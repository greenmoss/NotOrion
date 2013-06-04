import logging
logger = logging.getLogger(__name__)

import pyglet

import views.galaxy.map.stars

class Star(object):

    def __init__(self, star_system_view):
        self.star_system_view = star_system_view

        Star = views.galaxy.map.stars.Star
        image = pyglet.resource.image(Star.image_file_name)
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        self.sprite = pyglet.sprite.Sprite(image, 0, 0)

    def prepare(self):
        Star = views.galaxy.map.stars.Star
        self.sprite.color = Star.colors[self.star_system_view.model_star.type]
        self.sprite.x = self.star_system_view.corners['left'] + 10
        self.sprite.y = self.star_system_view.corners['bottom'] + self.star_system_view.center[1]

    def draw(self):
        self.sprite.draw()
