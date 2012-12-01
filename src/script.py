import pyglet

class Script(object):
	def schedule_exit(self, dt=None):
		"""Simple script method to exit after a fixed time."""
		if dt is None:
			dt = 0.01
		pyglet.clock.schedule_interval(pyglet_app_exit, dt)

# Preconfigured events that can be invoked by Script objects.
def pyglet_app_exit(dt):
	pyglet.app.exit()
