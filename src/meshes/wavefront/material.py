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

        # Interleaved array of floats in GL_T2F_N3F_V3F format
        self.vertices = []
        self.array = None

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

def load_materials_file(file_path):
    """Load one or more materials from a *.mtl file. Return a Hash
    containing all found materials; the hash keys are the material names
    as found in the .mtl file."""
    this_material = None
    file_handle = open(file_path, 'r')
    materials = {}

    for line in file_handle:
        if line.startswith('#'):
            continue
        values = line.split()
        if not values:
            continue

        if values[0] == 'newmtl':
            this_material = Material(values[1])
            materials[this_material.name] = this_material
        elif this_material is None:
            warnings.warn('Expected "newmtl" in %s' % file_name)
            continue

        if values[0] == 'Kd':
            this_material.diffuse = map(float, values[1:])
        elif values[0] == 'Ka':
            this_material.ambient = map(float, values[1:])
        elif values[0] == 'Ks':
            this_material.specular = map(float, values[1:])
        elif values[0] == 'Ke':
            this_material.emissive = map(float, values[1:])
        elif values[0] == 'Ns':
            this_material.shininess = float(values[1])
        elif values[0] == 'd':
            this_material.opacity = float(values[1])
        elif values[0] == 'map_Kd':
            # wavefront file has relative paths
            # we only need the file name, since pyglet takes care of path lookups
            path = values[1].split('/')[-1]
            this_material.texture = pyglet.resource.image(path).texture

    if this_material.texture: this_material.verify_dimensions()
    return materials
