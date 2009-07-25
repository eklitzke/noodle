#!/usr/bin/env python

import pygtk
pygtk.require('2.0')

import gobject
import pango
import gtk
import math
import time
import random
import threading
from gtk import gdk

from noodle import util
from noodle import diagram
from noodle import color

try:
    import cairo
except ImportError:
    pass

if gtk.pygtk_version < (2,3,93):
    print "PyGtk 2.3.93 or later required"
    raise SystemExit

gobject.threads_init()

import diagram
import gtk
import threading
import gobject
from collections import defaultdict

import util

class NoodleWidget(gtk.DrawingArea):

	def __init__(self):
		gtk.DrawingArea.__init__(self)
		self.connect('expose_event', self.expose)

		diagram_settings = diagram.DiagramSettings()
		diagram_settings.title = 'Noodle Graph'
		noodle_diagram = diagram.NoodleDiagram(diagram_settings)

		self.data = {}

		self.diagram = noodle_diagram

	def expose(self, widget, event):
		cr = widget.window.cairo_create()
		cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
		cr.clip()
		self.diagram.WIDTH = self.allocation.width
		self.diagram.HEIGHT = self.allocation.height
		self.diagram.draw(cr)

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
		r, g, b = color.hsv_to_rgb(h, s, v)

		dgram = diagram.DataSettings(data)
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

def main():
	window = gtk.Window()
	window.set_title('Noodle 0.1')

	def wakeup(widget, event):
		if event.state & gtk.gdk.CONTROL_MASK and event.keyval == ord('w'):
			window.destroy()
			gtk.main_quit()
	window.connect('key-press-event', wakeup)
	window.resize(800, 600)

	noodle_widget = NoodleWidget()
	window.add(noodle_widget)
	window.connect('delete-event', gtk.main_quit)

	window.show_all()

	collector = TestDataCollector(noodle_widget)
	collector.start()

	gtk.main()

if __name__ == '__main__':
	main()
