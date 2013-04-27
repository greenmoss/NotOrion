import random

import pyglet

class FixedSizeObject(object):
    'Within the galaxy view, objects that maintain a constant size whenever scale changes.'

    # default is a very low-layer group
    pyglet_ordered_group = pyglet.graphics.OrderedGroup(100)

    def __init__(self, view_coordinates):
        self.view_coordinates = view_coordinates
        self.sprite_coordinates = view_coordinates

    def generate_centered_animated_sprite(self, coordinates=None, image_file_name=None, frame_count=None, duration=None, offset=None):
        """Generate an animated sprite with its anchor in the center of the first image. 
        If coordinates or image are not specified, it is assumed these should be retrieved 
        from self."""
        if coordinates is None:
            coordinates = self.sprite_coordinates

        if image_file_name is None:
            image_file_name = self.image_file_name
        animation_image = pyglet.resource.image(image_file_name)

        if frame_count is None:
            # derive number of frames from width divided by height
            (count, remainder) = divmod(animation_image.width, animation_image.height)
            if remainder > 0:
                raise DataError, "animation image width could not be divided evenly by animation image height" 
            frame_count = count

        if duration is None:
            duration = random.uniform(0.1,0.3)

        animation_image_seq = pyglet.image.ImageGrid(animation_image, 1, frame_count)
        for image in animation_image_seq:
            image.anchor_x = image.width // 2
            image.anchor_y = image.height // 2
        if offset is None:
            offset = random.randint(1, frame_count)
        offset_animation = animation_image_seq[offset:] + animation_image_seq[:offset]

        animation = pyglet.image.Animation.from_image_sequence(offset_animation, duration)
        return(
            pyglet.sprite.Sprite(animation,
                coordinates[0], coordinates[1]
            )
        )

    def generate_centered_sprite(self, coordinates=None, image_file_name=None):
        """Generate a sprite with its anchor in the center. 
        If coordinates or image are not specified, it is assumed these should be retrieved 
        from self."""
        if coordinates is None:
            coordinates = self.sprite_coordinates
        if image_file_name is None:
            image_file_name = self.image_file_name

        image = pyglet.resource.image(image_file_name)
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        return(
            pyglet.sprite.Sprite(image,
                coordinates[0], coordinates[1],
                group = self.pyglet_ordered_group, 
            )
        )

    def scale_coordinates(self, scaling_factor):
        "Set object's sprite coordinates based on a scaling factor."
        self.sprite_coordinates = (int(self.coordinates[0]/scaling_factor), int(self.coordinates[1]/scaling_factor))
        self.sprite.x = self.sprite_coordinates[0]
        self.sprite.y = self.sprite_coordinates[1]

class StaticImageObject(FixedSizeObject):
    'All foreground objects with a static sprite image that maintain a constant size across rescales, eg stars.'

    def __init__(self, coordinates, image_file_name=None):
        super(StaticImageObject, self).__init__(coordinates)

        self.sprite = self.generate_centered_sprite()

        self.scaled_sprite_origin = (
            int(self.sprite.image.anchor_x*self.sprite.scale), 
            int(self.sprite.image.anchor_y*self.sprite.scale))

class AnimatedObject(FixedSizeObject):
    'All animated foreground objects that maintain a constant size across rescales, eg black holes.'

    def __init__(self, coordinates, image_file_name=None, frame_count=None):
        self.frame_count = frame_count

        super(AnimatedObject, self).__init__(coordinates)

        self.sprite = self.generate_centered_animated_sprite()
        #self.sprite.batch = self.sprites_batch2
        #self.sprite.group = self.group
