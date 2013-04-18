---
layout: page
title: "Installation Instructions"
---
{% include JB/setup %}
Currently you must install from source; there are not yet any OS packages available. The following has been tested on Mac OS 10.7 (Lion) and Ubuntu 12.04 (Precise):

    git clone https://github.com/greenmoss/NotOrion.git 
       # Download the code.
    cd NotOrion 
       # Change to the NotOrion directory.
    ./bootstrap.sh 
       # This installs all prerequisites.
    source Env/bin/activate 
       # Activate the NotOrion environment. 
       # If you are using virtualenvwrapper, run "workon NotOrion" instead.
    ./NotOrion.py

To report problems, create an [issue on the Github project](https://github.com/greenmoss/NotOrion/issues).

Technical notes: bootstrap.sh is a bash script (plain shell will not work). It installs into a [virtualenv](http://pypi.python.org/pypi/virtualenv), either standalone or via [virtualenvwrapper](http://www.doughellmann.com/projects/virtualenvwrapper/). The bootstrap.sh script then installs and hands control to [shovel](https://github.com/seomoz/shovel), which installs other Python modules. 

Shovel handles all operational tasks. Run `shovel help` to see what is available.
