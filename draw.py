import cairo
import math

class Settings(object):
	pass

class DataSettings(Settings):
	"""This represents the settings for a line of data points."""

	def __init__(self):
		self.line_color = (0, 0, 0)

		self.dots_enabled = True
		self.dots_color = (0, 0, 1)
		self.dots_opacity = 0.8

class NoodleDiagram(object):

	WIDTH, HEIGHT = 800, 600

	def __init__(self):
		self.margin = 30
		self.tau = 0.25

		self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.WIDTH, self.HEIGHT)
		self.cr = cairo.Context(self.surface)

		self.data_sets = []

	def add_data(self, data_set):
		self.data_sets.append(data_set)
	
	def draw_frame(self):
		"""This draws the frame around the stuff"""

		# First, draw a blank white canvas
		self.cr.set_source_rgb(1, 1, 1)
		self.cr.rectangle(0, 0, self.WIDTH, self.HEIGHT)
		self.cr.fill()

		# Now draw the margins
		self.cr.set_source_rgb(0, 0, 0)
		self.cr.move_to(self.margin, self.HEIGHT - self.margin)
		self.cr.line_to(self.margin, 0)
		self.cr.move_to(self.margin, self.HEIGHT - self.margin)
		self.cr.line_to(self.WIDTH, self.HEIGHT - self.margin)
	
	def draw(self):

		self.draw_frame()
		self.cr.translate(self.margin, -self.margin)

		x_min = min(float(data[0][0]) for data in self.data_sets)
		x_max = max(float(data[-1][0]) for data in self.data_sets)

		y_min = 0
		y_max = 0
		for data_set in self.data_sets:
			y_max = max(y_max, max(float(point[1]) for point in data_set))

		width = float(x_max - x_min)

		rel_width = self.WIDTH - self.margin
		rel_height = self.HEIGHT - self.margin

		xx = rel_width / width
		xy = 0
		x0 = -x_min * xx
		yx = 0
		yy = -rel_height / y_max
		y0 = rel_height + 2*self.margin

		self.mat = cairo.Matrix(xx, yx, xy, yy, x0, y0)

		for data_set in self.data_sets:
			self.draw_data_set(data_set)

	def draw_data_set(self, data):

		control_data = []
	
		sample_data = [self.mat.transform_point(x, y) for x, y in data]

		# The first and last points are special cases... since we're traversing
		# throught the data in order, we start with the first point. For the
		# first point, the initial control point is directly on the path between
		# the first point and the second point.
		x, y = sample_data[0]
		x1, y1 = sample_data[1]
		qx = self.tau * (x1 - x)
		qy = self.tau * (y1 - y)
		control_data.append((qx, qy))

		for i in xrange(1, len(sample_data) - 1):
			x0, y0 = sample_data[i-1]
			x1, y1 = sample_data[i]
			x2, y2 = sample_data[i+1]

			qx = self.tau * (x2 - x0)
			qy = self.tau * (y2 - y0)

			control_data.append((qx, qy))

		self.cr.set_source_rgb(0, 0, 0)
		self.cr.move_to(*sample_data[0])
		for i in xrange(0, len(sample_data) - 2):
			x0, y0 = sample_data[i]
			x1, y1 = sample_data[i+1]

			qx0, qy0 = control_data[i]
			qx1, qy1 = control_data[i+1]

			self.cr.curve_to(x0 + qx0, y0 + qy0, x1 - qx1, y1 - qy1, x1, y1)

		# Draw the final line segment
		self.cr.line_to(*sample_data[-1])

		# Render the line
		self.cr.stroke()
	
		self.cr.set_source_rgba(0, 0, 1, 0.6)
		for x, y in sample_data:
			self.cr.move_to(x, y)
			self.cr.arc(x, y, 4, 0, 2 * math.pi)
			self.cr.fill()
	
	def write(self, fname):
		return self.surface.write_to_png(fname)

diagram = NoodleDiagram()
diagram.add_data([(0,1.5618), (1,1.6181), (2,1.7533), (3,1.6211), (4,1.8151) , (5,1.6225) , (6,1.6746) , (7,1.6423) , (8,1.6083) , (9,1.7178) , (10,1.7609) , (11,1.8334) , (12,1.7215) , (13,1.7473) , (14,1.7602) , (15,1.8741) , (16,1.6417) , (17,1.7281) , (18,1.6502) , (19,1.4890)])
diagram.draw()
diagram.write('noodle.png')
