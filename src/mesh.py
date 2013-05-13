# TODO: move this into an independent git project library
# Derived from `contrib/model/examples/obj_test.py` in the pyglet directory
import os
import warnings

from pyglet.gl import *
from pyglet import image

class Material(object):
    diffuse = [.8, .8, .8]
    ambient = [.2, .2, .2]
    specular = [0., 0., 0.]
    emission = [0., 0., 0.]
    shininess = 0.
    opacity = 1.
    texture = None

    def __init__(self, name):
        self.name = name

    def prepare(self, face=GL_FRONT_AND_BACK):
        if self.texture:
            glEnable(self.texture.target)
            glBindTexture(self.texture.target, self.texture.id)
        else:
            glDisable(GL_TEXTURE_2D)

        glMaterialfv(face, GL_DIFFUSE,
            (GLfloat * 4)(*(self.diffuse + [self.opacity])))
        glMaterialfv(face, GL_AMBIENT,
            (GLfloat * 4)(*(self.ambient + [self.opacity])))
        glMaterialfv(face, GL_SPECULAR,
            (GLfloat * 4)(*(self.specular + [self.opacity])))
        glMaterialfv(face, GL_EMISSION,
            (GLfloat * 4)(*(self.emission + [self.opacity])))
        glMaterialf(face, GL_SHININESS, self.shininess)

    def verify_dimensions(self):
        self.verify('width')
        self.verify('height')

    def verify(self, dimension):
        value = self.texture.__getattribute__(dimension)
        while value > 1:
            div_float = float(value) / 2.0
            div_int = int(div_float)
            if not (div_float == div_int):
                warnings.warn(
                    'texture %s is %d, which is not a power of 2: partial mesh coverage?'%(
                        dimension, self.texture.__getattribute__(dimension)
                    )
                )
                break
            value = div_int

class MaterialGroup(object):
    def __init__(self, material):
        self.material = material

        # Interleaved array of floats in GL_T2F_N3F_V3F format
        self.vertices = []
        self.array = None

class Mesh(object):
    def __init__(self, name):
        self.name = name
        self.groups = []

        # Display list, created only if compile() is called, but used
        # automatically by draw()
        self.display_list = None

    def draw(self):
        if self.display_list:
            glCallList(self.display_list)
            return

        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glPushAttrib(GL_CURRENT_BIT | GL_ENABLE_BIT | GL_LIGHTING_BIT)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        for group in self.groups:
            group.material.prepare()
            if group.array is None:
                group.array = (GLfloat * len(group.vertices))(*group.vertices)
                group.triangles = len(group.vertices) / 8
            glInterleavedArrays(GL_T2F_N3F_V3F, 0, group.array)
            glDrawArrays(GL_TRIANGLES, 0, group.triangles)
        glPopAttrib()
        glPopClientAttrib()

    def compile(self):
        if not self.display_list:
            display_list = glGenLists(1)
            glNewList(display_list, GL_COMPILE)
            self.draw()
            glEndList()
            self.display_list = display_list

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

        mesh = None
        group = None
        material = None

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
                self.load_material_library(values[1])
            elif values[0] in ('usemtl', 'usemat'):
                material = self.materials.get(values[1], None)
                if material is None:
                    warnings.warn('Unknown material: %s' % values[1])
                if mesh is not None:
                    group = MaterialGroup(material)
                    mesh.groups.append(group)
            elif values[0] == 'o':
                mesh = Mesh(values[1])
                self.meshes[mesh.name] = mesh
                self.mesh_list.append(mesh)
                group = None
            elif values[0] == 'f':
                if len(normals) == 1: warnings.warn('No Normals found: black screen?')

                if mesh is None:
                    mesh = Mesh('')
                    self.mesh_list.append(mesh)
                if material is None:
                    material = Material()
                if group is None:
                    group = MaterialGroup(material)
                    mesh.groups.append(group)

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

    def open_material_file(self, file_name):
        '''Override for loading from archive/network etc.'''
        return open(os.path.join(self.path, file_name), 'r')

    def load_material_library(self, file_name):
        material = None
        file_handle = self.open_material_file(file_name)

        for line in file_handle:
            if line.startswith('#'):
                continue
            values = line.split()
            if not values:
                continue

            if values[0] == 'newmtl':
                material = Material(values[1])
                self.materials[material.name] = material
            elif material is None:
                warnings.warn('Expected "newmtl" in %s' % file_name)
                continue

            try:
                if values[0] == 'Kd':
                    material.diffuse = map(float, values[1:])
                elif values[0] == 'Ka':
                    material.ambient = map(float, values[1:])
                elif values[0] == 'Ks':
                    material.specular = map(float, values[1:])
                elif values[0] == 'Ke':
                    material.emissive = map(float, values[1:])
                elif values[0] == 'Ns':
                    material.shininess = float(values[1])
                elif values[0] == 'd':
                    material.opacity = float(values[1])
                elif values[0] == 'map_Kd':
                    try:
                        material.texture = image.load(values[1]).texture
                    except image.ImageDecodeException:
                        warnings.warn('Could not load texture %s' % values[1])
            except:
                warnings.warn('Parse error in %s.' % file_name)

        if material.texture: material.verify_dimensions()

    def draw(self):
        for mesh in self.mesh_list:
            mesh.draw()
