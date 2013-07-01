import os
import sys
import shutil
import subprocess
import platform

from shovel import task

class LinuxHandler(object):
    def install(self):
        # broken as of Nov 3, 2012
        #check_calls('pip install pyglet')
        check_calls('pip install hg+https://pyglet.googlecode.com/hg/')

    def package(self):
        raise Exception, 'not yet supported'

class OSXHandler(object):
    def install(self):
        # since 10.6, pyglet compatibility issues must be worked around; see
        # http://twistedpairdevelopment.wordpress.com/2012/02/21/installing-pyglet-in-mac-os-x/
        check_calls('pip install hg+https://pyglet.googlecode.com/hg/')
        check_calls('pip install pyobjc==2.2')

        check_calls('pip install py2app')

        # attempts to install as 32-bit result in "wrong architecture" messages:
        # hack to force 32-bit arch; see
        # http://stackoverflow.com/questions/7663852/running-non-system-python-with-virtualenv-in-32bit-mode-on-os-x
        #sed -ie 's/unset pydoc/unset pydoc; unset python/' ~/.virtualenvs/NotOrion/bin/activate
        #sed -ie 's/alias pydoc/alias python="arch -i386 python"; alias pydoc/' ~/.virtualenvs/NotOrion/bin/activate
        #pip install pyglet

    def package(self):
        try:
            import py2app
        except:
            print 'missing required module: py2app'
            sys.exit

        rmdir('build')
        rmdir('dist')

        allow_bytecode()

        if alias:
            check_calls('python setup.py py2app -A')
            print "Ready to run: './dist/NotOrion.app/Contents/MacOS/NotOrion'"
        else:
            check_calls('python setup.py py2app')
            print "Ready to run: 'open dist/NotOrion.app'"

def detect_os():
    '''Get handler for supported OS, or exit.'''
    # we currently naively assume all versions of supported OSes are supported :p
    if platform.system() == 'Darwin':
        return OSXHandler()
    elif platform.system() == 'Linux':
        return LinuxHandler()
    else:
        raise Exception, 'unsupported OS: %s'%platform.system()

def allow_bytecode():
    if os.environ.get('PYTHONDONTWRITEBYTECODE'):
        os.environ.pop('PYTHONDONTWRITEBYTECODE')

def check_calls(str):
    return subprocess.check_call(str.split())

def rmdir(dir):
    if os.path.isdir(dir):
        shutil.rmtree(dir)

def rm_ext(ext):
    '''Remove files by extension name.

    For removing pesky files that get in the way during development, such as *.pyc'''
    for dir_path, dir_names, file_names in os.walk(os.getcwd()):
        for file_name in file_names:
            if file_name.endswith('.%s'%ext):
                os.remove(os.path.join(dir_path, file_name))

os_handler = detect_os()

@task
def clean(alias = None):
    '''Remove locally-created artifacts.'''
    rmdir('build')
    rmdir('dist')
    rm_ext('pyc')
    rm_ext('pyo')
    os.remove(os.path.join(os.getcwd(), '.coverage'))
    rmdir('cover')

@task
def package(alias = None):
    '''Build a NotOrion package.'''
    # http://stackoverflow.com/questions/2933/an-executable-python-app
    os_handler.package(alias)

@task
def test_coverage(test_file = None):
    '''Run nose tests with a coverage report.'''
    #subprocess.call('nosetests --with-cover --cover-html --cover-package=src --cover-inclusive --cover-branches'.split())
    subprocess.call('nosetests --with-cover --cover-html --cover-package=src --cover-branches'.split())

@task
def test(test_file = None):
    '''Run nose tests.'''
    subprocess.call('nosetests')

@task
def install():
    '''Install all prerequisites for NotOrion.

    Includes modules for testing, building, and running NotOrion.'''
    allow_bytecode()
    os_handler.install()
    check_calls('pip install jsonpickle kytten coverage nose PyWavefront')
