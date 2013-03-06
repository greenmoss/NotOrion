---
layout: post
title: "Star System Scenery"
description: ""
category: 
tags: [updates]
---
{% include JB/setup %}
It's been several months since my last update. Instead of spending my limited free time on game improvements, I spent considerable time playing the original MoO2 game. This <strike>was because I was goofing off</strike> refreshed my memory about game mechanics and strategies.

Part of the delay/de-motivation for me has been due to not knowing how to approach the problem at hand: how should I model and import my star system view and "scenery"? I fixed the [asteroid rendering problem](https://github.com/greenmoss/pyglet_obj_test/commit/37f2933f3914266f56c644e0b9c591e34d2b986f), but was still unclear on how to fit even one asteroid into my star system popup view. So I started [reading](http://en.wikibooks.org/wiki/Blender_3D:_Noob_to_Pro) [anything](http://www.youtube.com/watch?v=OBJ_NP-Sm1M&noredirect=1) [I](http://livebm.com/play_video/VEY5HWdII10) [could](http://mygimptutorial.com/the-ultimate-gimp-planet-tutorial) [find](http://gamedev.stackexchange.com/questions/16585/how-do-you-programmatically-generate-a-sphere) [which](http://en.wikipedia.org/wiki/UV_mapping) [looked](http://www.packtpub.com/article/blender-creating-uv-texture) [related](http://www.blenderguru.com/videos/create-a-realistic-earth/) [to](http://www.wtv3d.org/t12795-blender-tutorial-making-planet-saturn-by-cgi-trainer) my goal.

I've concluded that I should mock up my star system view in Blender, including all elements of the star system popup window as they will appear in the game. I am not yet done, but what I have has already been hugely helpful for me. I have been able to see which considerations are most important, versus ones that I *thought* were important but turned out to be irrelevant. For example: I started to create a very detailed earth, but found that most of the intricate effects weren't even visible due to the planet's small size in the scene. The asteroid I started modelling also turns out to be too granular and detailed to be useful. Also, I can easily balance colors, animate planet rotations, test shading, and count vertices.

I'm still working on my Blender model, but I have completed enough to post various screenshots here. So my follow-on post (hopefully today) will be a gallery with more screenshots.

__Update:__ [the screenshots are online]({{ BASE_PATH }}/galleries/2013/03/05/modelling-the-star-system-view/)
