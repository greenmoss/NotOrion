# Installation #
To install NotOrion, run:
    cd NotOrion
    ./bootstrap.sh

# Running NotOrion #
Once bootstrap.sh has completed, run:
    source Env/bin/activate
    ./NotOrion.py

## Virtualenvwrapper ##
If bootstrap.sh detects that you are using virtualenvwrapper, it does *not* create virtualenv "Env" as above. Instead, bootstrap.sh invokes `mkvirtualenv NotOrion`. In this case, to run NotOrion:
    workon NotOrion
    ./NotOrion.py
