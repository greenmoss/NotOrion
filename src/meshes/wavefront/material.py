import warnings

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

    def set_texture(self, path):
        self.texture = Texture(path)

    def prepare(self, face=GL_FRONT_AND_BACK):
        if self.texture:
            self.texture.prepare()
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

class Texture(object):
    def __init__(self, path):
        self.path = path

        # wavefront file has relative paths
        # we only need the file name, since pyglet takes care of path lookups
        self.image_name = self.path.split('/')[-1]

        self.image = pyglet.resource.image(self.image_name).texture

        self.verify_dimensions()

        self.warn = False

    def prepare(self):
        glEnable(self.image.target)
        glBindTexture(self.image.target, self.image.id)

    def verify_dimensions(self):
        self.verify('width')
        self.verify('height')

    def verify(self, dimension):
        value = self.image.__getattribute__(dimension)
        while value > 1:
            div_float = float(value) / 2.0
            div_int = int(div_float)
            if not (div_float == div_int):
                if self.warn: warnings.warn(
                    'image %s is %d, which is not a power of 2: partial texture coverage?'%(
                        dimension, self.image.__getattribute__(dimension)
                    )
                )
                break
            value = div_int

class Parser(object):
    """Object to parse lines of a materials definition file."""

    def __init__(self):
        self.materials = {}
        self.material = None
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
                    'ignored unparseable values in wavefront material file: %s'%values)
            return
        parse_function(parameters)

    def parse_newmtl(self, parameters):
        self.material = Material(parameters[0])
        self.materials[self.material.name] = self.material

    def parse_Kd(self, parameters):
        self.material.diffuse = map(float, parameters[0:])

    def parse_Ka(self, parameters):
        self.material.ambient = map(float, parameters[0:])

    def parse_Ks(self, parameters):
        self.material.specular = map(float, parameters[0:])

    def parse_Ke(self, parameters):
        self.material.emissive = map(float, parameters[0:])

    def parse_Ns(self, parameters):
        self.material.shininess = float(parameters[0])

    def parse_d(self, parameters):
        self.material.opacity = float(parameters[0])

    def parse_map_Kd(self, parameters):
        self.material.set_texture(parameters[0])

def load_materials_file(file_path):
    """Load one or more materials from a *.mtl file. Return a Hash
    containing all found materials; the hash keys are the material names
    as found in the .mtl file."""
    file_handle = open(file_path, 'r')
    parser = Parser()

    for line in file_handle:
        parser.parse(line)

    return parser.materials
