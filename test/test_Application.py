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
	window_aspect_ratios = (
		(640, 480, 1.3333333333333333),
		(500, 1000, 0.5),
		(1423, 955, 1.4900523560209424))
	fields_of_view = (
		(640, 480, 7.5),
		(500, 1000, 15.625),
		(1423, 955, 14.921875))
	absolute_and_window_coordinates = (
		(640, 480, 2.1, (0, 0), (0, 0)), 
		(923, 561, 0.34, (-5, 3), (-11294.117647058822, 6776.470588235294)), 
		(1024, 768, 8, (15, -2), (1440.0, -192.0)))

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

	def testAspectRatio(self):
		"Given test window dimensions, aspect ratio for new windows should return known test values."
		for width, height, ratio in self.window_aspect_ratios:
			new_window = Application.GalaxyWindow(width, height)
			self.assertEqual(new_window.window_aspect_ratio, ratio)
			new_window.close()

	def testResizeAspectRatio(self):
		"Given test window dimensions, aspect ratio for resized windows should return known test values."
		galaxy_window = Application.GalaxyWindow()
		for width, height, ratio in self.window_aspect_ratios:
			galaxy_window.on_resize(width, height)
			self.assertEqual(galaxy_window.window_aspect_ratio, ratio)
		galaxy_window.close()

	def testFieldOfView(self):
		"Given test window dimensions, field of view for new windows should return known test values."
		for width, height, fov in self.fields_of_view:
			new_window = Application.GalaxyWindow(width, height)
			self.assertEqual(new_window.field_of_view, fov)
			new_window.close()

	def testResizeFieldOfView(self):
		"Given test window dimensions, field of view for resized windows should return known test values."
		galaxy_window = Application.GalaxyWindow()
		for width, height, fov in self.fields_of_view:
			galaxy_window.on_resize(width, height)
			self.assertEqual(galaxy_window.field_of_view, fov)
		galaxy_window.close()

	def testScaledWindow(self):
		"Given test window dimensions, scaled_window ratio for new windows should return known test values."
		scaled_window_values = (
			(640, 480, 96.0),
			(500, 1000, 200.0),
			(1423, 955, 191.0))
		for width, height, ratio in scaled_window_values:
			new_window = Application.GalaxyWindow(width, height)
			self.assertEqual(new_window.scaled_window, ratio)
			new_window.close()

	def testResizeRescaleScaledWindow(self):
		"Given test window dimensions, scaled_window ratio for resized, rescaled windows should return known test values."
		rescaled_scaled_window_values = (
			(640, 480, 0.2, 3840.0),
			(500, 1000, 1.0, 768.0),
			(1423, 955, 7.4, 103.78378378378378))
		galaxy_window = Application.GalaxyWindow()
		for width, height, new_scale, ratio in rescaled_scaled_window_values:
			galaxy_window.on_resize(width, height)
			galaxy_window.derive_from_scale(new_scale)
			self.assertEqual(galaxy_window.scaled_window, ratio)
		galaxy_window.close()

	def testInverseForegroundScale(self):
		"Given test window dimensions, inverse foreground scale for new windows should return known test values."
		inverse_foreground_scale_values = (
			(5.0, 0.2),
			(10.0, 0.1),
			(0.2, 5.0))
		galaxy_window = Application.GalaxyWindow()
		for scale, inverse_scale in inverse_foreground_scale_values:
			galaxy_window.derive_from_scale(scale)
			self.assertEqual(galaxy_window.inverse_foreground_scale, inverse_scale)
		galaxy_window.close()
	
	def testScaleOutOfBounds(self):
		"Scale should raise an exception if it is set to 0 or less"
		for scale in (0, -10):
			new_window = Application.GalaxyWindow(640, 480)
			self.assertRaises(Application.RangeException, new_window.derive_from_scale, scale)
			new_window.close()
	
	def testAbsoluteToWindow(self):
		"For predefined window dimensions, scale level, and absolute coordinates, should convert to known window coordinates."
		galaxy_window = Application.GalaxyWindow()
		for width, height, scale_level, absolute_coordinates, window_coordinates in self.absolute_and_window_coordinates:
			galaxy_window.on_resize(width, height)
			galaxy_window.derive_from_scale(scale_level)
			self.assertEqual(galaxy_window.absolute_to_window(absolute_coordinates), window_coordinates)
		galaxy_window.close()
	
	def testWindowToAbsolute(self):
		"For predefined window dimensions, scale level, and window coordinates, should convert to known absolute coordinates."
		galaxy_window = Application.GalaxyWindow()
		for width, height, scale_level, absolute_coordinates, window_coordinates in self.absolute_and_window_coordinates:
			galaxy_window.on_resize(width, height)
			galaxy_window.derive_from_scale(scale_level)
			self.assertEqual(galaxy_window.window_to_absolute(window_coordinates), absolute_coordinates)
		galaxy_window.close()
	
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

	def testAbsoluteCenterAfterPanAndZoom(self):
		"When panning, zooming in or out, then panning, absolute center should match known test values."
		pan_zoom_end_coordinates = (
			(40, -40, 20, (-4.702815778966123, -2.669165712386178)),
			(90, 0, -30, (-3.245912765318668, -1.9320909317373023)),
			(-1, 420, 1, (-3.4613541666666667, -7.048958333333333)))
		for pan_x, pan_y, scroll_y, test_absolute_center in pan_zoom_end_coordinates:
			new_window = Application.GalaxyWindow(640, 480)
			new_window.on_mouse_drag(0, 0, 10, 10, None, None)
			new_window.on_mouse_scroll(0, 0, 0, scroll_y)
			new_window.on_mouse_drag(0, 0, pan_x, pan_y, None, None)
			self.assertEqual(new_window.absolute_center, test_absolute_center)
			new_window.close()

if __name__ == "__main__":
	unittest.main()

