"""This manages all 3D meshes in the game."""
import logging
logger = logging.getLogger(__name__)

import pywavefront

from globals import g

class Mesh(object):
    """This is a wrapper for Wavefront-imported files, adapted for use
    within NotOrion."""
    def __init__(self, object_file_name):
        imported = pywavefront.Wavefront(object_file_name)

        mesh_count = len(imported.mesh_list)
        if not mesh_count == 1:
            raise Exception, \
                    "found %d meshes within %s; we require exactly one mesh"%(
                    mesh_count, object_file_name)
        self.mesh = imported.mesh_list[0]
        #logger.debug( self.mesh )

        material_count = len(self.mesh.materials)
        if material_count < 1:
            raise Exception, \
                    "found 0 materials within %s; we require at least one material"%( 
                    object_file_name)
        #logger.debug( self.mesh.materials[0] )

    def set_texture(self, image_path):
        self.mesh.materials[0].set_texture(image_path)

    def set_diffuse(self, color_values):
        self.mesh.materials[0].set_diffuse(color_values)

    def unset_diffuse(self):
        self.set_diffuse([0., 0., 0., 0.])

    def set_ambient(self, color_values):
        self.mesh.materials[0].set_ambient(color_values)

    def unset_ambient(self):
        self.set_ambient([0., 0., 0., 0.])

    def set_specular(self, color_values):
        self.mesh.materials[0].set_specular(color_values)

    def unset_specular(self):
        self.set_specular([0., 0., 0., 0.])

    def set_emissive(self, color_values):
        self.mesh.materials[0].set_emissive(color_values)

    def unset_emissive(self):
        self.set_emissive([0., 0., 0., 0.])

    def draw(self):
        self.mesh.draw()

class Sphere(Mesh):
    def __init__(self):
        super(Sphere, self).__init__('uv_sphere.obj')
