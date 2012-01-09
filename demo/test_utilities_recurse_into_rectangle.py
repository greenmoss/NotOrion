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
min_length = random.randint(2,20)
min_length = 2
amount = random.randint(2,20)
amount = 1097
print 'min_length: %d; amount: %d'%(min_length, amount)

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

rectangles = []
utilities.recurse_into_rectangle(bottom,left,top,right,amount,min_length,rectangles)
for index, rect in enumerate(rectangles):
	r = 256
	g = 128
	layer = layer2
	batch = batch1
	if index%2:
		batch = batch2
		layer = layer3
	#	r = 128
	#	g = 256
	(sub_bottom, sub_left, sub_top, sub_right) = rect
	# sub rectangles
	batch.add(6, GL_LINE_LOOP, layer,
		( 'v2i', (sub_left,sub_bottom, sub_left,sub_bottom, sub_left,sub_top, sub_right,sub_top, sub_right,sub_bottom, sub_right,sub_bottom)),
		( 'c3B', (r,g,128, r,g,128, r,g,128, r,g,128, r,g,128, r,g,128))
	)

# base pixel + margin
batch2.add(4, GL_QUADS, layer4,
	( 'v2i', (left,bottom, left,bottom+min_length-1, left+min_length-1,bottom+min_length-1, left+min_length-1,bottom)),
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
