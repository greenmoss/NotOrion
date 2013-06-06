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
    def __init__(self, file_name, file_handle=None, path=None):
        self.materials = {}
        self.meshes = {}        # Name mapping
        self.mesh_list = []     # Also includes anonymous meshes

        if file_handle is None:
            file_handle = open(file_name, 'r')

        if path is None:
            path = os.path.dirname(file_name)
        self.path = path

        this_mesh = None
        group = None
        this_material = None

        vertices = [[0., 0., 0.]]
        normals = [[0., 0., 0.]]
        tex_coords = [[0., 0.]]

        for line in open(file_name, "r"):
            if line.startswith('#'): 
                continue
            values = line.split()
            if not values: 
                continue

            if values[0] == 'v':
                vertices.append(map(float, values[1:4]))
            elif values[0] == 'vn':
                normals.append(map(float, values[1:4]))
            elif values[0] == 'vt':
                tex_coords.append(map(float, values[1:3]))
            elif values[0] == 'mtllib':
                file_path = os.path.join(self.path, values[1])
                loaded = material.load_materials_file(file_path)
                for material_name, material_object in loaded.iteritems():
                    self.materials[material_name] = material_object
            elif values[0] in ('usemtl', 'usemat'):
                this_material = self.materials.get(values[1], None)
                if this_material is None:
                    warnings.warn('Unknown material: %s' % values[1])
                if this_mesh is not None:
                    group = material.MaterialGroup(this_material)
                    this_mesh.groups.append(group)
            elif values[0] == 'o':
                this_mesh = mesh.Mesh(values[1])
                self.meshes[this_mesh.name] = this_mesh
                self.mesh_list.append(this_mesh)
                group = None
            elif values[0] == 'f':
                if len(normals) == 1: warnings.warn('No Normals found: black screen?')

                if this_mesh is None:
                    this_mesh = mesh.Mesh('')
                    self.mesh_list.append(this_mesh)
                if this_material is None:
                    this_material = material.Material()
                if group is None:
                    group = material.MaterialGroup(this_material)
                    this_mesh.groups.append(group)

                # For fan triangulation, remember first and latest vertices
                v1 = None
                vlast = None
                points = []
                for i, v in enumerate(values[1:]):
                    v_index, t_index, n_index = \
                        (map(int, [j or 0 for j in v.split('/')]) + [0, 0])[:3]
                    if v_index < 0:
                        v_index += len(vertices) - 1
                    if t_index < 0:
                        t_index += len(tex_coords) - 1
                    if n_index < 0:
                        n_index += len(normals) - 1
                    vertex = tex_coords[t_index] + \
                             normals[n_index] + \
                             vertices[v_index] 

                    if i >= 3:
                        # Triangulate
                        group.vertices += v1 + vlast
                    group.vertices += vertex

                    if i == 0:
                        v1 = vertex
                    vlast = vertex

    def draw(self):
        for this_mesh in self.mesh_list:
            this_mesh.draw()
