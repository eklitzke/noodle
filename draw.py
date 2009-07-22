import cairo
import math

class Settings(object):
	pass

class DataSettings(Settings):
	"""This represents the settings for a line of data points."""

	def __init__(self, data):

		self.data = data

		self.line_color = (0, 0, 0)

		self.dots_enabled = True
		self.dots_color = (0, 0, 1)
		self.dots_opacity = 0.6

class DiagramSettings(Settings):

	def __init__(self):
		self.title = '(untitled)'

class NoodleDiagram(object):

	WIDTH, HEIGHT = 800, 600

	# Add an extra 10% of vertical space to the top of the graph
	VERTICAL_FUDGE = 1.10

	# Add an extra 3% horizontal space
	HORIZONTAL_FUDGE = 1.03

	def __init__(self, settings):

		self.settings = settings

		self.margin = 30
		self.tau = 0.20

		self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.WIDTH, self.HEIGHT)
		self.cr = cairo.Context(self.surface)

		self.data_sets = []

	def add_data(self, data_set):
		assert isinstance(data_set, DataSettings)
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
		for i in range(1, int(math.ceil(self.y_max / y_spacing)) + 1):
			_, y_pos = self.mat.transform_point(0, i * y_spacing)
			y_pos = int(round(y_pos))
			self.cr.move_to(-4, y_pos)
			self.cr.line_to(4, y_pos)
		self.cr.stroke()
		
		x_spacing = get_spacing(self.x_max - self.x_min)
		for i in range(1, int(math.ceil((self.x_max - self.x_min)/ x_spacing)) + 1):
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

		self.x_min = min(float(data.data[0][0]) for data in self.data_sets)
		self.x_max = max(float(data.data[-1][0]) for data in self.data_sets) * self.HORIZONTAL_FUDGE

		self.y_min = 0
		self.y_max = 0
		for data_set in self.data_sets:
			self.y_max = max(self.y_max, max(float(point[1]) for point in data_set.data))
		
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
		self.cr.move_to(100, 8)
		self.cr.set_font_size(16)

		# set the font antialiasing
		font_opts = cairo.FontOptions()
		font_opts.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
		self.cr.set_font_options(font_opts)

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
	
		sample_data = [self.mat.transform_point(x, y) for x, y in data.data]

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
	
		rgba_settings = list(data.dots_color) + [data.dots_opacity]
		self.cr.set_source_rgba(*rgba_settings)
		for x, y in sample_data:
			self.cr.move_to(x, y)
			self.cr.arc(x, y, 4, 0, 2 * math.pi)
			self.cr.fill()
	
	def write(self, fname):
		return self.surface.write_to_png(fname)

diagram_settings = DiagramSettings()
diagram_settings.title = 'Hello World Graph'
diagram = NoodleDiagram(diagram_settings)

data_one = DataSettings([(0,1.5618), (1,1.6181), (2,1.7533), (3,1.6211), (4,1.8151) , (5,1.6225) , (6,1.6746) , (7,1.6423) , (8,1.6083) , (9,1.7178) , (10,1.7609) , (11,1.8334) , (12,1.7215) , (13,1.7473) , (14,1.7602) , (15,1.8741) , (16,1.6417) , (17,1.7281) , (18,1.6502) , (19,1.4890)])

data_two = DataSettings([(0,1.1997) , (1,1.2902) , (2,1.5996) , (3,2.1451) , (4,2.1546) , (5,1.8481) , (6,1.6872) , (7,1.4629) , (8,1.4289) , (9,1.4704) , (10,1.5064) , (11,1.5799) , (12,1.5030) , (13,1.4658) , (14,1.5674) , (15,1.5623) , (16,1.1632) , (17,1.3055) , (18,1.1015) , (19,0.8648)])
data_two.dots_color = (1, 0, 0)

data_three = DataSettings([(0,0.0515) , (1,0.0484) , (2,0.0466) , (3,0.0461) , (4,0.0458) , (5,0.0479) , (6,0.0502) , (7,0.0547) , (8,0.0673) , (9,0.0793) , (10,0.0940) , (11,0.1109) , (12,0.1028) , (13,0.1060) , (14,0.1139) , (15,0.0922) , (16,0.0658) , (17,0.0732) , (18,0.0639) , (19,0.0582)])
data_three.dots_color = (0, 0.8, 0)

data_four = DataSettings([(0,0.6827) ,(1,0.6462) ,(2,0.6970) ,(3,0.7730) ,(4,0.7807) ,(5,0.5742) ,(6,0.6657) ,(7,0.6655) ,(8,0.7226) ,(9,0.7417) ,(10,0.7879) ,(11,0.8237) ,(12,0.7946) ,(13,0.7802) ,(14,0.8187) ,(15,0.8032) ,(16,0.7454) ,(17,0.7487) ,(18,0.7384) ,(19,0.6760)])
data_four.dots_color = (0.8, 0, 0.9)


diagram.add_data(data_one)
diagram.add_data(data_two)
diagram.add_data(data_three)
diagram.add_data(data_four)
diagram.draw()
diagram.write('noodle.png')
