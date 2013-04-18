---
layout: post
title: "Lost In Translation"
description: ""
category: 
tags: [updates, in the weeds]
---
{% include JB/setup %}
**WARNING**: This will be a technical/code-heavy post; note tag <a
 href="{{ BASE_PATH }}/tags.html#in the weeds-ref">in the weeds</a>.

After having created nice-looking scenes in Blender, it is now time to
import a mesh and texture into Pyglet. Predictably, this has been a
struggle. The documentation is sparse, so I once again have to turn to
code deconstruction. 

The [pyglet object test](https://github.com/greenmoss/pyglet_obj_test/)
has proven useful as a starting point. However, this has two problems.

At first there was no texture, only a color. I posted a [Stackexchange
question](http://gamedev.stackexchange.com/questions/53036/example-of-texture-mapping-in-pyglet),
read up on the [Wavefront object
format](http://en.wikipedia.org/wiki/Wavefront_.obj_file), and
determined this was due to a missing UVMap in Blender.  After manually
creating a UVMap and applying it, the texture is properly displayed by
pyglet_obj_test. However, this leads to the second problem.

There is apparently a bug with the pyglet_obj_test texture mapping. When
displaying a sphere, I see this (pretend it's a single sphere rotating):

<img alt='flawed_sphere_angle1' src='{{ BASE_PATH }}/img/flawed_sphere1.png' />

<img alt='flawed_sphere_angle2' src='{{ BASE_PATH }}/img/flawed_sphere2.png' />

Delving further, I reduced my mesh to the simplest possible: one
triangle plus a texture. The wavefront export file looks like:

    mtllib uv_plane.mtl
    o Cube
    v 1.000011 0.000012 1.000013
    v -1.000021 0.000022 1.000023
    v 1.000031 0.000032 -1.000033
    v -1.000041 0.000042 -1.000043
    vt 0.000051 1.000052
    vt 0.000061 0.000062
    vt 1.000071 0.000072
    vt 1.000081 1.000082
    vn 0.000091 1.000092 -0.000093
    usemtl Material.004_terran6_mod.png
    s off
    f 2/3/1 1/2/1 3/1/1

(the decimal-values-approaching zero, such as ".000013" are manually
introduced by me to assist in debugging). Even here the problem
manifests: the rendered triangle is only partially filled. In the image,
note the image **should** be a complete triangle, but is instead missing
its top and left corners:

<img alt='flawed_plane' src='{{ BASE_PATH }}/img/flawed_plane.png' />
 
Since the important part of the texture mapping code in the object test
involves `glInterleavedArrays`, I decided to attack the problem from a
different angle: build up from the pyglet [opengl imaging
example](http://www.pyglet.org/doc/programming_guide/opengl_imaging.html).
Or so I thought. Nope, not working.

I've [posted to
pyglet-users](https://groups.google.com/forum/?fromgroups=#!topic/pyglet-users/KkKcD-FWiag),
and will continue poking around until hopefully I can make my way past
this roadblock.

Apropos, several people have forwarded "[on Infinite
Loops](http://threepanelsoul.com/2013/04/15/on-infinite-loops/)". Yup.
