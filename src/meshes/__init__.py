"""This manages all 3D meshes in the game."""
import os
import wavefront

from globals import g

class Mesh(object):
    def __init__(self, mesh_name):
        path = os.path.join(g.paths['meshes_dir'], mesh_name)
        self.mesh = wavefront.Wavefront(path)

    def draw(self):
        self.mesh.draw()

class Sphere(Mesh):
    def __init__(self):
        super(Sphere, self).__init__('uv_sphere.obj')
