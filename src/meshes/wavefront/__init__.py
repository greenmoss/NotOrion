"""This library imports Wavefront-formatted 3D object definitions and
converts them into pyglet vertex lists."""

# TODO: move this into an independent git project library
# Derived from `contrib/model/examples/obj_test.py` in the pyglet directory
import os
import warnings

from pyglet.gl import *

import material
import mesh

class Wavefront(object):
    """Import a wavefront .obj file."""
    def __init__(self, file_name, path=None):
        self.file_name = file_name

        self.materials = {}
        self.meshes = {}        # Name mapping
        self.mesh_list = []     # Also includes anonymous meshes

        if path is None:
            path = os.path.dirname(self.file_name)
        self.path = path

        parser = Parser(self)

        for line in open(self.file_name, "r"):
            parser.parse(line)

    def draw(self):
        for this_mesh in self.mesh_list:
            this_mesh.draw()

class Parser(object):
    """Object to parse lines of a mesh definition file."""
    def __init__(self, wavefront):
        # unfortunately we can't escape from external effects on the
        # wavefront object
        self.wavefront = wavefront

        self.mesh = None
        self.material = None

        self.vertices = [[0., 0., 0.]]
        self.normals = [[0., 0., 0.]]
        self.tex_coords = [[0., 0.]]

        self.warn = False

    def parse(self, line):
        """Determine what type of line we are and dispatch
        appropriately."""
        if line.startswith('#'): return

        values = line.split()
        if len(values) < 2: return

        line_type = values[0]
        parameters = values[1:]

        try:
            parse_function = getattr(self, 'parse_%s'%line_type)
        except AttributeError:
            if self.warn: warnings.warn(
                    'ignored unparseable values in wavefront object file: %s'%values)
            return
        parse_function(parameters)

    # methods for parsing types of wavefront lines
    def parse_v(self, parameters):
        self.vertices.append(map(float, parameters[0:3]))

    def parse_vn(self, parameters):
        self.normals.append(map(float, parameters[0:3]))

    def parse_vt(self, parameters):
        self.tex_coords.append(map(float, parameters[0:2]))

    def parse_mtllib(self, parameters):
        file_path = os.path.join(self.wavefront.path, parameters[0])
        loaded = material.load_materials_file(file_path)
        for material_name, material_object in loaded.iteritems():
            self.wavefront.materials[material_name] = material_object

    def parse_usemtl(self, parameters):
        self.material = self.wavefront.materials.get(parameters[0], None)
        if self.material is None:
            if self.warn: warnings.warn('Unknown material: %s' % parameters[0])
        if self.mesh is not None:
            self.mesh.add_material(self.material)

    def parse_usemat(self, parameters):
        self.parse_usemtl(parameters)

    def parse_o(self, parameters):
        self.mesh = mesh.Mesh(parameters[0])
        self.wavefront.meshes[self.mesh.name] = self.mesh
        self.wavefront.mesh_list.append(self.mesh)

    def parse_f(self, parameters):
        if self.warn and (len(self.normals) == 1): 
            warnings.warn('No Normals found: black screen?')

        if self.mesh is None:
            self.mesh = mesh.Mesh('')
            self.wavefront.mesh_list.append(self.mesh)
        if self.material is None:
            self.material = material.Material()
        self.mesh.add_material(self.material)

        # For fan triangulation, remember first and latest vertices
        v1 = None
        vlast = None
        points = []
        for i, v in enumerate(parameters[0:]):
            v_index, t_index, n_index = \
                (map(int, [j or 0 for j in v.split('/')]) + [0, 0])[:3]
            if v_index < 0:
                v_index += len(self.vertices) - 1
            if t_index < 0:
                t_index += len(self.tex_coords) - 1
            if n_index < 0:
                n_index += len(self.normals) - 1
            vertex = self.tex_coords[t_index] + \
                     self.normals[n_index] + \
                     self.vertices[v_index] 

            if i >= 3:
                # Triangulate
                self.material.vertices += v1 + vlast
            self.material.vertices += vertex

            if i == 0:
                v1 = vertex
            vlast = vertex
