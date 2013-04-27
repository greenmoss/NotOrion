from __future__ import division
import logging
logger = logging.getLogger(__name__)
import platform

from pyglet.gl import *

from globals import g
import views
import utilities

import background_stars
import black_holes
import nebulae
import stars
import worm_holes

class Galaxy(views.View):
    # when scaling/rescaling, minimum distance between stars/black holes
    min_scaled_separation = 10
    # .01 more or less than 1.0 should be fast enough zoom speed
    zoom_speed = 1.01

    coordinate_handlers = {
        'centered_window': lambda *args: CenteredWindowCoordinate(*args),
        'default_window': lambda *args: DefaultWindowCoordinate(*args),
        'foreground': lambda *args: ForegroundCoordinate(*args),
        'model': lambda *args: ModelCoordinate(*args),
    }

    def __init__(self, state):
        logger.debug('instantiating views.Galaxy')

        self.state = state

        self.background_stars = background_stars.BackgroundStars()
        self.stars = stars.Stars()
        self.black_holes = black_holes.BlackHoles()
        self.nebulae = nebulae.Nebulae()
        self.worm_holes = worm_holes.WormHoles(self.stars)

        # black background
        glClearColor(0.0, 0.0, 0.0, 0)

        self.bounding_y = g.galaxy.top_bounding_y
        if -g.galaxy.bottom_bounding_y > g.galaxy.top_bounding_y:
            self.bounding_y = -g.galaxy.bottom_bounding_y
        self.bounding_x = g.galaxy.right_bounding_x
        if -g.galaxy.left_bounding_x > g.galaxy.right_bounding_x:
            self.bounding_x = -g.galaxy.left_bounding_x

        self.derive_from_window_dimensions()
        self.set_scale(self.maximum_scale)
        self.set_center((0, 0))

        #g.window.push_handlers(self)

        #pyglet.clock.schedule_interval(self.animate, 1/60.)
    
    def coordinate(self, coordinates, type="foreground"):
        return Galaxy.coordinate_handlers[type](coordinates, self)
    
    def derive_from_window_dimensions(self):
        "Set attributes that are based on window dimensions."
        self.half_width = g.window.width/2
        self.half_height = g.window.height/2

        # Derive minimum and maximum scale, based on minimum and maximum distances between galaxy objects.
        self.minimum_dimension = (g.window.width < g.window.height) and g.window.width or g.window.height
            
        self.minimum_scale = g.galaxy.min_distance/self.minimum_dimension*5.0
        self.maximum_scale = g.galaxy.max_distance/self.minimum_dimension
        # restrict zooming out to the minimum distance between sprites
        if(g.galaxy.min_distance/self.maximum_scale < Galaxy.min_scaled_separation):
            self.maximum_scale = g.galaxy.min_distance/Galaxy.min_scaled_separation
        if self.minimum_scale > self.maximum_scale:
            self.maximum_scale = self.minimum_scale
    
    def load(self, attribs):
        self.set_scale(attribs['scale'])
        self.set_center(attribs['view_center'])

    def save(self):
        return {
            'scale': self.scale, 
            'view_center': self.view_center
        }

    def set_center(self, coordinates):
        "Set the window center, for rendering objects."
        coordinates = [coordinates[0], coordinates[1]]
        # would the new center make us fall outside acceptable margins?
        if coordinates[1] > self.center_limits['top']:
            coordinates[1] = self.center_limits['top']
        elif coordinates[1] < self.center_limits['bottom']:
            coordinates[1] = self.center_limits['bottom']

        if coordinates[0] > self.center_limits['right']:
            coordinates[0] = self.center_limits['right']
        elif coordinates[0] < self.center_limits['left']:
            coordinates[0] = self.center_limits['left']

        self.view_center = (coordinates[0], coordinates[1])

        # every time we update the center, the mini-map will change
        #self.derive_mini_map()

    def set_scale(self, scale):
        "Set attributes that are based on zoom/scale."

        # scale must be larger than 0
        if scale <= 0:
            raise RangeException, "scale must be greater than 0"

        if (scale < self.minimum_scale):
            scale = self.minimum_scale
        elif (scale > self.maximum_scale):
            scale = self.maximum_scale

        # the integer modifiers ensure all stars and labels remain visible at the limits 
        # of the pan area
        self.center_limits = {
            'top':self.bounding_y/scale+110-self.half_height,
            'right':self.bounding_x/scale+140-self.half_width,
            'bottom':-self.bounding_y/scale-120+self.half_height,
            'left':-self.bounding_x/scale-140+self.half_width,
        }
        if self.center_limits['top'] < self.center_limits['bottom']:
            self.center_limits['top'] = 0
            self.center_limits['bottom'] = 0
        if self.center_limits['right'] < self.center_limits['left']:
            self.center_limits['right'] = 0
            self.center_limits['left'] = 0

        self.scale = scale

        # recalculate all object attributes that rely on scale
        # TODO (debt) use observer pattern instead, eg stars should be attaching to "set_scale"
        self.stars.set_scale(scale)
        self.black_holes.set_scale(scale)
        self.nebulae.set_scale(scale)
        self.worm_holes.set_scale(scale) # *must* be set *after* stars
    
    def set_drawing_matrices(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(-self.half_width, self.half_width, -self.half_height, self.half_height)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_drawing_to_foreground(self):
        self.translate_x = int(-self.view_center[0])
        self.translate_y = int(-self.view_center[1])
        glTranslated(self.translate_x,self.translate_y,0)

    def handle_draw(self):
        g.window.clear()

        self.set_drawing_matrices()

        self.background_stars.draw()

        self.set_drawing_to_foreground()

        self.nebulae.draw()
        self.worm_holes.draw()
        self.stars.draw()
        self.black_holes.draw()

        glLoadIdentity()

    def handle_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.state.vetoed_drag:
            return
        if platform.system() == 'Darwin': dy = -dy
        self.set_center((self.view_center[0] - dx, self.view_center[1] - dy))
    
    def handle_mouse_scroll(self, x, y, scroll_x, scroll_y):
        prescale_model_coordinate = self.state.map_coordinate((x, y), 'default_window').as_model()

        self.set_scale(self.scale*(Galaxy.zoom_speed**scroll_y))

        postscale_model_coordinate = self.state.map_coordinate((x, y), 'default_window').as_model()

        # scale the prescale mouse according to the *new* scale
        prescale_mouse = (prescale_model_coordinate.x/self.scale, prescale_model_coordinate.y/self.scale)
        postscale_mouse = (postscale_model_coordinate.x/self.scale, postscale_model_coordinate.y/self.scale)

        self.set_center(
            (
                prescale_mouse[0]-postscale_mouse[0]+self.view_center[0], 
                prescale_mouse[1]-postscale_mouse[1]+self.view_center[1]
            )
        )
    
    def handle_resize(self, width, height):
        # reset openGL attributes to match new window dimensions
        glViewport(0, 0, width, height)
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)

        self.derive_from_window_dimensions()

        # window resize affects scale attributes, so recalculate
        self.set_scale(self.scale)

        # ensure center is still in a valid position
        self.set_center((self.view_center[0], self.view_center[1]))

class Coordinate(object):
    def __init__(self, coordinates, view):
        self.view = view
        self.type = self.__class__.__name__
        self.x = coordinates[0]
        self.y = coordinates[1]

        self.centered_window = None
        self.default_window = None
        self.foreground = None
        self.model = None
    
    def __repr__(self):
        return "type %s: %s, %s"%(self.type, self.x, self.y)
    
    def as_tuple(self):
        return( (self.x, self.y) )

class CenteredWindowCoordinate(Coordinate):
    def as_default_window(self):
        if self.default_window:
            return self.default_window
        converted_x = self.x + self.view.half_width
        converted_y = self.y + self.view.half_height
        self.default_window = DefaultWindowCoordinate((converted_x, converted_y), self.view)
        return self.default_window
    
    def as_foreground(self):
        if self.foreground:
            return self.foreground
        converted_x = self.x + self.view.view_center[0]
        converted_y = self.y + self.view.view_center[1]
        self.foreground = ForegroundCoordinate((converted_x, converted_y), self.view)
        return self.foreground

class DefaultWindowCoordinate(Coordinate):
    """A coordinate using default pyglet window coordinates.

    Lower left is 0/0, upper right is width/height."""
    def as_centered_window(self):
        if self.centered_window:
            return self.centered_window
        converted_x = self.x - self.view.half_width
        converted_y = self.y - self.view.half_height
        self.centered_window = CenteredWindowCoordinate((converted_x, converted_y), self.view)
        return self.centered_window
    
    def as_foreground(self):
        if self.foreground:
            return self.foreground
        self.foreground = self.as_centered_window().as_foreground()
        return self.foreground
    
    def as_model(self):
        if self.model:
            return self.model
        self.model = self.as_foreground().as_model()
        return self.model

class ForegroundCoordinate(Coordinate):
    """A coordinate scaled by the view's scaling factor.
    
    The x/y coordinate will update if the scale changes, but *not* if we pan.
    """
    def as_centered_window(self):
        if self.centered_window:
            return self.centered_window
        converted_x = self.x - self.view.view_center[0]
        converted_y = self.y - self.view.view_center[1]
        self.centered_window = CenteredWindowCoordinate((converted_x, converted_y), self.view)
        return self.centered_window
    
    def as_default_window(self):
        if self.default_window:
            return self.default_window
        self.default_window = self.as_centered_window().as_default_window()
        return self.default_window
    
    def as_model(self):
        if self.model:
            return self.model
        converted_x = self.x * self.view.scale
        converted_y = self.y * self.view.scale
        self.model = ModelCoordinate((converted_x, converted_y), self.view)
        return self.model

class ModelCoordinate(Coordinate):
    """A coordinate defined within the galaxy model.

    Regardless of zooming or panning, the x/y coordinate should not update.
    Note that conversion from/to model/foreground is approximate."""

    def as_centered_window(self):
        if self.centered_window:
            return self.centered_window
        self.centered_window = self.as_foreground().as_centered_window()
        return self.centered_window

    def as_default_window(self):
        if self.default_window:
            return self.default_window
        self.default_window = self.as_centered_window().as_default_window()
        return self.default_window
    
    def as_foreground(self):
        if self.foreground:
            return self.foreground
        converted_x = self.x / self.view.scale
        converted_y = self.y / self.view.scale
        self.foreground = ForegroundCoordinate((converted_x, converted_y), self.view)
        return self.foreground
