---
layout: post
title: "Python Virtual Env"
description: ""
category: 
tags: [meta]
---
{% include JB/setup %}

Well that was easy. I now have python virtual env working, which allowed me to switch away from my 32-bit macports python. The latter was problematic for installing python packages, so one less headache is a good thing.

The <a href="http://twistedpairdevelopment.wordpress.com/2012/02/21/installing-pyglet-in-mac-os-x/">instructions for installing 64-bit pyglet on OS X Lion</a> required that I switch to pyglet 1.2 beta though, and this introduced at least two bugs. The nebulae are now too dark, and vertical scrolling is backwards. These should be easy enough to fix.

I had thought virtual envs would somehow give me an installable stand-alone package, but this appears to be incorrect. I think I need to work on this next. There needs to be an easy way to download and run NotOrion!
