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

    def draw(self):
        self.mesh.draw()

class Sphere(Mesh):
    def __init__(self):
        super(Sphere, self).__init__('uv_sphere.obj')