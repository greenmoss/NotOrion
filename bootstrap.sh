#!/usr/bin/env bash

# Options for venv:
export ENV_OPTS='--no-site-packages'

unset PYTHONDONTWRITEBYTECODE

# Bash functions can't return variables? Make this global:
virtualenvwrapper_path=''

function find_virtualenvwrapper {
	# no consistent way to find 'virtualenvwrapper.sh', so try various methods
	# http://stackoverflow.com/questions/13111881/scripting-virtualenvwrapper-mkvirtualenv
	# is it directly available in the path?
	virtualenvwrapper_path=$(which virtualenvwrapper.sh)
	if [ $? -eq 0 ]; then
		return
	fi
	# nope; how about something that looks like it in our path?
	# http://stackoverflow.com/questions/948008/linux-command-to-list-all-available-commands-and-aliases
	virtualenvwrapper_cmd=$(compgen -ac | grep -i 'virtualenvwrapper\.sh' | sort | uniq | head -1)
	if [ -n "$virtualenvwrapper_cmd" ]; then
		virtualenvwrapper_path=$(which $virtualenvwrapper_cmd)
		if [ $? -eq 0 ]; then
			return
		fi
	fi
	# still not; Debubuntu puts it in /etc/bash_completion.d
	virtualenvwrapper_path='/etc/bash_completion.d/virtualenvwrapper'
	if [ -e "$virtualenvwrapper_path" ]; then
		return
	fi
	# any other methods to find virtualenvwrapper can be added here
	echo "unable to find virtualenvwrapper.sh or anything that looks like it"
	exit 1
}

function create_virtualenvwrapper_venv {
	echo "installing into virtualenvwrapper directory"
	ENV_NAME=NotOrion
	find_virtualenvwrapper
	source $virtualenvwrapper_path
	mkvirtualenv $ENV_NAME
	workon $ENV_NAME
}

function create_standalone_venv {
	echo "installing new standalone virtualenv into current directory"

	# from http://stackoverflow.com/questions/4324558/whats-the-proper-way-to-install-pip-virtualenv-and-distribute-for-python
	# Select current version of virtualenv:
	VERSION=1.8.2
	URL_BASE="http://pypi.python.org/packages/source/v/virtualenv"
	# Set to whatever python interpreter you want for your first environment:
	PYTHON=$(which python)
	ENV_NAME=Env

	# --- Real work starts here ---
	curl -O $URL_BASE/virtualenv-$VERSION.tar.gz
	tar xzf virtualenv-$VERSION.tar.gz
	# Create the first "bootstrap" environment.
	$PYTHON virtualenv-$VERSION/virtualenv.py $ENV_OPTS $ENV_NAME
	# Don't need these anymore.
	rm -rf virtualenv-$VERSION
	rm virtualenv-$VERSION.tar.gz
	source $ENV_NAME/bin/activate
}

if [ -z "$WORKON_HOME" ]; then
	create_standalone_venv
else
	create_virtualenvwrapper_venv
fi

# Once we have our environment, install shovel and pass control to it
pip install shovel
shovel install
