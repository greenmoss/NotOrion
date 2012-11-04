---
layout: post
title: "Bootstrapped"
description: ""
category: 
tags: [meta]
---
{% include JB/setup %}
I have created a respectable installation script, so now it should be possible on OS X or Linux to download NotOrion and try it out. It still requires a source installation, which will of course be a barrier for most users. However, for developers or people comfortable with the command line, see the [installation instructions]({{ BASE_PATH }}/installation.html).

Warnings, caveats, etc: this is the first time I've tried NotOrion on Linux, and I immediately found out there are some serious bugs. Also, my testing environment for the installer was limited to Mac OS 10.8 (Lion), and Ubuntu 12.04 (Precise). Installing on any other platform may or may not work. I've opened the [Github issue tracker](https://github.com/greenmoss/NotOrion/issues) if you'd like to report problems.

Technical notes: bootstrap.sh is a bash script (yes it needs bash, not just plain shell) which installs into a [virtualenv](http://pypi.python.org/pypi/virtualenv), either standalone or via [virtualenvwrapper](http://www.doughellmann.com/projects/virtualenvwrapper/). I like virtualenvs, because they decouple the game libraries and environment from the stock OS libraries. Thus, there should be no dependency conflicts with the rest of the system. The bootstrap.sh script then installs and hands control to [shovel](https://github.com/seomoz/shovel), which installs other Python modules. Shovel also handles all operational tasks; run `shovel help` to see what is available.
