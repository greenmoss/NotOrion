import pyglet
from pyglet.gl import *
import sys
sys.path.append('../src')
import utilities
import random

window = pyglet.window.Window(width=1024, height=768)

(bottom, left, top, right) = (
    random.randint(-80, -30), 
    random.randint(-80, -30), 
    random.randint(30, 80), 
    random.randint(30, 80), 
)
(bottom, left, top, right) = (-300, -400, 300, 400)
print ('bottom, left, top, right: ',(bottom, left, top, right))
dispersion = random.randint(2,20)
dispersion = 1
amount = random.randint(2,20)
amount = 4501
print 'dispersion: %d; amount: %d'%(dispersion, amount)

layer1 = pyglet.graphics.OrderedGroup(0)
layer2 = pyglet.graphics.OrderedGroup(1)
layer3 = pyglet.graphics.OrderedGroup(2)
layer4 = pyglet.graphics.OrderedGroup(3)

batch1 = pyglet.graphics.Batch()
batch2 = pyglet.graphics.Batch()

# outline of box to be divided
batch1.add(4, GL_LINE_LOOP, layer1,
    ( 'v2i', (left-1,bottom-1, left-1,top+1, right+1,top+1, right+1,bottom-1)),
    ( 'c3B', (128,128,128, 128,128,128, 128,128,128, 128,128,128))
)

for coordinate in utilities.random_dispersed_coordinates(bottom,left,top,right,amount,dispersion):
    layer = layer2
    batch2.add(1, GL_POINTS, layer,
        ( 'v2i', (coordinate[0], coordinate[1])),
        ( 'c3B', (0, 255, 255))
    )

@window.event
def on_draw():
    window.clear()
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-512, 512, -364, 364)
    glMatrixMode(GL_MODELVIEW)
    batch1.draw()
    batch2.draw()

pyglet.app.run()

