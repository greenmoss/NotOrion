#! /usr/bin/env python -O
import pyglet
from pyglet.gl import *
import random

global window, label
window = pyglet.window.Window(400, 400)
label = pyglet.text.Label('Something', anchor_x='center', anchor_y='center')

global label_box, label_line_vertex_list
label_box = pyglet.graphics.vertex_list( 4,
	('v2f', ( 0, 0,   0, 0,   0, 0,   0, 0,)),
	('c4B/static', (
		0, 0, 0, 200,
		0, 0, 0, 200,
		0, 0, 0, 200,
		0, 0, 0, 200,
		)
	)
)
label_line_vertex_list = pyglet.graphics.vertex_list( 2,
	('v2f', ( 0, 0,  0, 0 ) ),
	('c3B/static', (25,128,25)*2)
)

global x_direction, y_direction
x_direction, y_direction = 1, 1
global x_move, y_move
x_move, y_move = random.randint(1,10), random.randint(1,10)

def move_label(dt):
	global x_direction, y_direction, x_move, y_move, window, label, label_box, label_line_vertex_list
	window._mouse_x += x_move*x_direction
	window._mouse_y += y_move*y_direction
	if (window._mouse_x > 399):
		window._mouse_x = 399
		x_direction = x_direction * -1
		x_move = random.randint(1,10)
	elif (window._mouse_x < 0):
		window._mouse_x = 0
		x_direction = x_direction * -1
		x_move = random.randint(1,10)
	if (window._mouse_y > 399):
		window._mouse_y = 399
		y_direction = y_direction * -1
		y_move = random.randint(1,10)
	elif (window._mouse_y < 0):
		window._mouse_y = 0
		y_direction = y_direction * -1
		y_move = random.randint(1,10)
	window._mouse_in_window = True
	label.x = window._mouse_x
	label.y = window._mouse_y

	label_box_top = label.y + (label.content_height/2)
	label_box_bottom = label.y - (label.content_height/2)
	label_box_right = label.x + (label.content_width/2)
	label_box_left = label.x - (label.content_width/2)
	label_box.vertices = [
		label_box_right, label_box_bottom,
		label_box_right, label_box_top,
		label_box_left, label_box_top,
		label_box_left, label_box_bottom
	]

	label_line_vertex_list.vertices = [
		200.0, 200.0,
		label.x, label.y
	]

pyglet.clock.schedule_interval(move_label, 0.01)

@window.event
def on_draw():
	window.clear()
	glPushAttrib(GL_ENABLE_BIT)
	glEnable(GL_LINE_STIPPLE)
	glLineStipple(1, 0x1111)
	label_line_vertex_list.draw(pyglet.gl.GL_LINES)
	glPopAttrib()
	label_box.draw(pyglet.gl.GL_QUADS)
	label.draw()

pyglet.app.run()
