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

		self.title = '(untitled)'

class NoodleDiagram(object):

	WIDTH, HEIGHT = 800, 600

	# Add an extra 10% of vertical space to the top of the graph
	VERTICAL_FUDGE = 1.10

	# Add an extra 3% horizontal space
	HORIZONTAL_FUDGE = 1.03

	def __init__(self, data_settings):

		self.settings = data_settings

		self.margin = 30
		self.tau = 0.25

		self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.WIDTH, self.HEIGHT)
		self.cr = cairo.Context(self.surface)

		self.data_sets = []

	def add_data(self, data_set):
		self.data_sets.append(data_set)
	
	def draw_frame(self):
		"""This draws the frame around the stuff"""

		def get_spacing(max_val):
			exponent = math.floor(math.log10(self.y_max))
			mantissa = max_val * math.pow(10, -exponent)
			if mantissa <= 4:
				spacing = math.pow(10, exponent - 1)
			else:
				spacing = 0.5 * math.pow(10, exponent)
			return spacing

		y_spacing = get_spacing(self.y_max)
		for i in range(0, int(math.ceil(self.y_max / y_spacing)) + 1):
			_, y_pos = self.mat.transform_point(0, i * y_spacing)
			y_pos = int(round(y_pos))
			self.cr.move_to(-4, y_pos)
			self.cr.line_to(4, y_pos)
		self.cr.stroke()
		
		x_spacing = get_spacing(self.x_max - self.x_min)
		for i in range(0, int(math.ceil((self.x_max - self.x_min)/ x_spacing)) + 1):
			x_pos, _ = self.mat.transform_point(self.x_min + i * x_spacing, 0)
			x_pos = int(round(x_pos))
			self.cr.move_to(x_pos, -4)
			self.cr.line_to(x_pos, 4)
			self.cr.stroke()
	
	def get_scale(self):
		"""Figure out the scale of the graph."""

		# Set the basic transformation matrix. This puts the logical point (0,
		# 0) in the lower-left corner, at the intersection of the two axes. The
		# point (10, 0) would be a point 10 pixels out on the x-axis, and the
		# point (0, 10) would be a point 10 pixels up on the y-axis.
		draw_matrix = cairo.Matrix(1, 0, 0, -1, self.margin, self.HEIGHT - self.margin)
		self.cr.transform(draw_matrix)

		self.x_min = min(float(data[0][0]) for data in self.data_sets)
		self.x_max = max(float(data[-1][0]) for data in self.data_sets) * self.HORIZONTAL_FUDGE

		self.y_min = 0
		self.y_max = 0
		for data_set in self.data_sets:
			self.y_max = max(self.y_max, max(float(point[1]) for point in data_set))
		
		self.y_max *= self.VERTICAL_FUDGE
		
		width = float(self.x_max - self.x_min)
	
		rel_width = self.WIDTH - self.margin
		rel_height = self.HEIGHT - self.margin

		xx = rel_width / width
		xy = 0
		x0 = -self.x_min * xx
		yx = 0
		yy = rel_height / self.y_max
		y0 = 0

		self.mat = cairo.Matrix(xx, yx, xy, yy, x0, y0)
	
	def draw_title(self):
		self.cr.set_source_rgb(0, 0, 0)
		self.cr.move_to(100, 20)
		self.cr.set_font_size(16)
		self.cr.select_font_face('sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

		_, _, text_width, text_height, _, _ = self.cr.text_extents(self.settings.title)

		# Note: the x_pos is not offset by self.margin
		x_pos = int(round((self.WIDTH / 2.0) - (text_width / 2.0)))
		y_pos = int(round(5 + text_height))
		self.cr.move_to(x_pos, y_pos)
		self.cr.show_text(self.settings.title)
		self.cr.stroke()

	def draw(self):

		# First, draw a blank white canvas
		self.cr.set_source_rgb(1, 1, 1)
		self.cr.rectangle(0, 0, self.WIDTH, self.HEIGHT)
		self.cr.fill()

		# Draw the title
		self.draw_title()

		# Now draw the margins
		self.cr.set_source_rgb(0, 0, 0)
		self.cr.move_to(self.margin, self.HEIGHT - self.margin)
		self.cr.line_to(self.margin, 0)
		self.cr.move_to(self.margin, self.HEIGHT - self.margin)
		self.cr.line_to(self.WIDTH, self.HEIGHT - self.margin)
	

		self.get_scale()
		self.draw_frame()

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

settings = DataSettings()
settings.title = 'Servlet Response Time'

diagram = NoodleDiagram(settings)
diagram.add_data([(0,1.5618), (1,1.6181), (2,1.7533), (3,1.6211), (4,1.8151) , (5,1.6225) , (6,1.6746) , (7,1.6423) , (8,1.6083) , (9,1.7178) , (10,1.7609) , (11,1.8334) , (12,1.7215) , (13,1.7473) , (14,1.7602) , (15,1.8741) , (16,1.6417) , (17,1.7281) , (18,1.6502) , (19,1.4890)])
diagram.draw()
diagram.write('noodle.png')
