from pyglet.gl import *

class Mesh(object):
    def __init__(self, name):
        self.name = name
        self.materials = []

        # Display list, created only if compile() is called, but used
        # automatically by draw()
        self.display_list = None

    def has_material(self, new_material):
        """Determine whether we already have a material of this name."""
        for material in self.materials:
            if material.name == new_material.name:
                return True
        return False

    def add_material(self, material):
        """Add a material to the mesh, IFF it is not already present."""
        if self.has_material(material): return
        self.materials.append(material)

    def draw(self):
        if self.display_list:
            glCallList(self.display_list)
            return

        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glPushAttrib(GL_CURRENT_BIT | GL_ENABLE_BIT | GL_LIGHTING_BIT)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        for material in self.materials:
            material.prepare()
            if material.array is None:
                material.array = (GLfloat * len(material.vertices))(*material.vertices)
                material.triangles = len(material.vertices) / 8
            glInterleavedArrays(GL_T2F_N3F_V3F, 0, material.array)
            glDrawArrays(GL_TRIANGLES, 0, material.triangles)
        glPopAttrib()
        glPopClientAttrib()

    def compile(self):
        if not self.display_list:
            display_list = glGenLists(1)
            glNewList(display_list, GL_COMPILE)
            self.draw()
            glEndList()
            self.display_list = display_list
