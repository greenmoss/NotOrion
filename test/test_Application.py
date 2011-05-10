import unittest
import Application
import Stars
import pyglet

class TestGalaxyWindow(unittest.TestCase):
	out_of_bounds_window_dimensions = (
		(10000, 400), 
		(400, 10000),
		(10, 400), 
		(400, 10))

	def testWindowDimensionsOutOfBounds(self):
		"Should not allow width or height outside of boundary limits."
		for width, height in self.out_of_bounds_window_dimensions:
			self.assertRaises(Application.RangeException, Application.GalaxyWindow, width, height)
	
	def testResizeWindowDimensionsOutOfBounds(self):
		"Resize should not allow width or height outside of boundary limits."
		galaxy_window = Application.GalaxyWindow()
		for width, height in self.out_of_bounds_window_dimensions:
			self.assertRaises(Application.RangeException, galaxy_window.on_resize, width, height)
		galaxy_window.close()
	
	def testScaleOutOfBounds(self):
		"Scale should raise an exception if it is set to 0 or less"
		for scale in (0, -10):
			new_window = Application.GalaxyWindow(640, 480)
			self.assertRaises(Application.RangeException, new_window.derive_from_scale, scale)
			new_window.close()
	
#	def testFixedBackgroundWhenResizing(self):
#		"Background stars should remain in the same position when the window is resized."
#		data = Application.DataContainer()
#		data.stars = Stars.All( [], [ Stars.BackgroundStar((0, 0), (0, 0, 255)) ])
#		new_window = Application.GalaxyWindow(640, 480, data)
#		new_window.on_draw()
#		buffer = (pyglet.gl.GLubyte * (3*new_window.width*new_window.height))(0)
#		pyglet.gl.glReadPixels(0, 0, new_window.width, new_window.height, pyglet.gl.GL_RGB, pyglet.gl.GL_UNSIGNED_BYTE, buffer)
#		# PIL; what to import?
#		image = Image.fromstring(mode="RGB", size=(new_window.width, new_window.height), data=buffer)
#		image.transpose(Image.FLIP_TOP_BOTTOM)
#		image.save('/Users/kyoder/Desktop/notorion.png')
#		for y in range(new_window.height):
#			left_x = y * new_window.width * 3
#			for x in range(new_window.width):
#				x_offset = left_x + (x * 3)
#				rgb = (buffer[x_offset], buffer[x_offset + 1], buffer[x_offset + 2])
#				if not (rgb[0] == 0) and (rgb[1] == 0) and (rgb[2] == 0):
#					print ((x, y), rgb)
#		new_window.close()

#	def testFixedForegroundWhenResizing(self):
#		"Foreground objects should remain in the same position when the window is resized."

if __name__ == "__main__":
	unittest.main()

