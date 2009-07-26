import threading
import gobject
from collections import defaultdict

import noodle.color
import noodle.diagram

from noodle import util

class DataCollector(threading.Thread):
	"""A DataCollector is something that accumulates data and feed it into a
	NoodleWidget.
	"""

	def __init__(self, widget):
		threading.Thread.__init__(self)
		self.widget = widget
		self.next_color = (0, .8, .8)
	
	def new_diagram(self, data):
		h, s, v = self.next_color
		self.next_color = (h + 60, s, v)
		r, g, b = noodle.color.hsv_to_rgb(h, s, v)

		dgram = noodle.diagram.DataSettings(data)
		dgram.dots_color = (r, g, b)
		return dgram
	
	def redraw_widget(self):
		def redraw(widget):
			x, y, w, h = widget.allocation
			widget.window.invalidate_rect((0, 0, w, h), False)
		gobject.idle_add(redraw, self.widget)

class TabDataCollector(DataCollector):

	DATA_PATH = '/home/evan/20090708.tab'
	
	def run(self):

		buffering_data_sets = {}

		data_input = open(self.DATA_PATH)
		for line in data_input:
			servlet, t, val = line.split(' ')
			point = util.DataPoint(t, val)

			if servlet in self.widget.diagram.data_sets:
				self.widget.diagram.data_sets[servlet].data.append(point)
				self.redraw_widget()
				#time.sleep(0.01)
	
			else:
				if servlet not in buffering_data_sets:
					buffering_data_sets[servlet] = util.TimeDataSet(300, 60 * 60, 30)
				data = buffering_data_sets[servlet]
				data.append(point)
				if len(data) >= 30:
					dgram = self.new_diagram(data)
					self.widget.diagram.add_data_set(servlet, dgram)
					del buffering_data_sets[servlet]

class TestDataCollector(DataCollector):
	"""A static data collector, for testing.

	This just loads data from a static file, and renders it once. This is good
	for testing, since the widget isn't animated, and the data stays the same.
	"""

	DATA_PATH = '/home/evan/20090708.csv'

	def run(self):
		data_sets = defaultdict(list)
		data_input = open(self.DATA_PATH)

		for line in data_input:
			servlet, xval, count, yval = line.split(',')
			data_sets[servlet].append(util.DataPoint(xval, yval))
		

		for servlet, data in data_sets.iteritems():
			dgram = self.new_diagram(data)
			self.widget.diagram.add_data_set(servlet, dgram)
		self.redraw_widget()
