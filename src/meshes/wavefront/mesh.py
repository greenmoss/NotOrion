from pyglet.gl import *

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
