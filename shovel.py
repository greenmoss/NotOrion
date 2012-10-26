import os
import sys
import shutil
from subprocess import call

from shovel import task

def allow_bytecode():
	if os.environ.get('PYTHONDONTWRITEBYTECODE'):
		os.environ.pop('PYTHONDONTWRITEBYTECODE')

def calls(str):
	return call(str.split())

def package_os_x(alias):
	try:
		import py2app
	except:
		print 'missing required module: py2app'
		sys.exit

	rmdir('build')
	rmdir('dist')

	allow_bytecode()

	if alias:
		calls('python setup.py py2app -A')
		print "Ready to run: './dist/NotOrion.app/Contents/MacOS/NotOrion'"
	else:
		calls('python setup.py py2app')
		print "Ready to run: 'open dist/NotOrion.app'"

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

@task
def clean(alias = None):
	'''Remove locally-created artifacts.'''
	rmdir('build')
	rmdir('dist')
	rm_ext('pyc')
	rm_ext('pyo')

@task
def package(alias = None):
	'''Build a NotOrion package.'''
	# http://stackoverflow.com/questions/2933/an-executable-python-app
	package_os_x(alias)

@task
def test(test_file = None):
	'''Runs a named test, or all tests.'''
	call('nosetests')
