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
(bottom, left, top, right) = (-49, -49, 50, 50)
print ('bottom, left, top, right: ',(bottom, left, top, right))
min_length = random.randint(2,20)
min_length = 50
amount = random.randint(2,20)
amount = 2
print 'min_length: %d; amount: %d'%(min_length, amount)

layer1 = pyglet.graphics.OrderedGroup(0)
layer2 = pyglet.graphics.OrderedGroup(1)
layer3 = pyglet.graphics.OrderedGroup(2)
layer4 = pyglet.graphics.OrderedGroup(3)

batch1 = pyglet.graphics.Batch()
# outline of box to be divided
batch1.add(4, GL_LINE_LOOP, layer1,
	( 'v2i', (left-1,bottom-1, left-1,top+1, right+1,top+1, right+1,bottom-1)),
	( 'c3B', (128,128,128, 128,128,128, 128,128,128, 128,128,128))
)

sub_rect_amounts = utilities.randomly_split_rectangle(bottom,left,top,right,min_length,amount)
print ('sub_rect_amounts: ',sub_rect_amounts)
for index, rect in enumerate(sub_rect_amounts.keys()):
	r = 256
	g = 128
	layer = layer2
	if index:
		r = 128
		g = 256
		layer = layer3
	(sub_bottom, sub_left, sub_top, sub_right) = rect
	# sub rectangles
	batch1.add(4, GL_LINE_LOOP, layer,
		( 'v2i', (sub_left,sub_bottom, sub_left,sub_top, sub_right,sub_top, sub_right,sub_bottom)),
		( 'c3B', (r,g,128, r,g,128, r,g,128, r,g,128))
	)

# base pixel + margin
batch2 = pyglet.graphics.Batch()
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
