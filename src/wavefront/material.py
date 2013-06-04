from pyglet.gl import *

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
