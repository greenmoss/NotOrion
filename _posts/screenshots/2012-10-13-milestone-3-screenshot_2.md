---
layout: screenshot
title: "milestone 3, screenshot 2"
description: "the entire galaxy"
category: screenshots
tags: [milestone-3]
slug: the_entire_galaxy
thumb_width: 150
thumb_height: 113
tiny_width: 40
tiny_height: 30
---
{% include JB/setup %}

This shows a "normal" sized galaxy. 

One of the first questions I have consistently gotten when people have looked at this map is "what are those blue lines"? The answer is: worm holes. Based on this kind of feedback, I'll probably need to make it more obvious when you hover your mouse over them. Maybe I will display a translucent informational window above the mouse cursor.

Another question is "what are those brown things". For example in this screen shot look above and to the right of "Musca" about 1/3 of the way from the top left of the screen shot. Those are black holes, and while the game is running they rotate slowly. Short of blocking spaceship travel routes, they won't be of much interest in the original MoO2 rules. To make it clearer, I will still do an informational hover window for these too.

The purple/red/green shapes are nebulae. People who first see the map have fortunately so far understood immediately what they are. I'm generating them from randomly-arranged small, static <a href="https://github.com/greenmoss/NotOrion/tree/master/resources/images">cloud-like images</a>. Each of these was in turn created in <a href="http://inkscape.org/">Inkscape</a> with <a href="http://en.wikipedia.org/wiki/Perlin_noise">Perlin noise</a>. You can also download the <a href="https://github.com/greenmoss/NotOrion/blob/master/resources/images/src/nebulae.svg">source inkscape document</a>.

<img height='600' width='800' alt='the_entire_galaxy' src='{{ BASE_PATH }}/img/screenshots/2012-10-13/milestone-3/the_entire_galaxy.png' />
