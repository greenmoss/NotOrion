#! /usr/bin/env python -O
# Try to consistently trigger segfault/bus error due to moving/changing star label
import sys
sys.path.append('../src')
import application
import galaxy
import game_configuration
import pyglet
import random
import guppy

global x_direction, y_direction
x_direction, y_direction = 1, 1
global x_move, y_move
x_move, y_move = random.randint(1,10), random.randint(1,10)

def move_label(dt, data):
    if dt > 5:
        print '----- stuttered %d seconds: heap dump -----'%dt
        print guppy.hpy().heap()
        data.galaxy_window.window.close()

    global x_direction, y_direction, x_move, y_move
    # for this test, the origin is the first named star
    data.galaxy_window.range_origin_star = data.galaxy_objects.named_stars[0]
    data.galaxy_window.range_origin_coordinate = data.galaxy_objects.named_stars[0].coordinates
    gw = data.galaxy_window.window
    gw._mouse_x += x_move*x_direction
    gw._mouse_y += y_move*y_direction
    if (gw._mouse_x > 399):
        gw._mouse_x = 399
        x_direction = x_direction * -1
        x_move = random.randint(1,10)
    elif (gw._mouse_x < 0):
        gw._mouse_x = 0
        x_direction = x_direction * -1
        x_move = random.randint(1,10)
    if (gw._mouse_y > 399):
        gw._mouse_y = 399
        y_direction = y_direction * -1
        y_move = random.randint(1,10)
    elif (gw._mouse_y < 0):
        gw._mouse_y = 0
        y_direction = y_direction * -1
        y_move = random.randint(1,10)
    gw._mouse_in_window = True
    data.galaxy_window.set_range_info()

data = application.DataContainer()
# populate galaxy/data with "Beginner" random stars/positions
game_configuration.Choose(data, difficulty="Beginner")
data.galaxy_window = galaxy.WindowContainer(data)
data.galaxy_window.window.height = 400
data.galaxy_window.window.width = 400

pyglet.clock.schedule_interval(move_label, 0.01, data)

print "----- Launching: heap dump -----"
print guppy.hpy().heap()

pyglet.app.run()

print "----- Terminating: heap dump -----"
print guppy.hpy().heap()
