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

import util
import diagram

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

	def __init__(self, widget):
		threading.Thread.__init__(self)
		self.widget = widget
	
	def run(self):

		randcolor = lambda: 0.25 + random.random() * 0.7

		buffering_data_sets = {}

		data_input = open('/home/evan/20090708.tab')
		for line in data_input:
			servlet, t, val = line.split(' ')
			point = util.DataPoint(t, val)

			if servlet in self.widget.diagram.data_sets:
				self.widget.diagram.data_sets[servlet].data.append(point)
				def redraw(widget):
					x, y, w, h = widget.allocation
					widget.window.invalidate_rect((0, 0, w, h), False)
				gobject.idle_add(redraw, self.widget)
				#time.sleep(0.01)
			
			else:
				if servlet not in buffering_data_sets:
					buffering_data_sets[servlet] = util.TimeDataSet(300, 1500, 30)
				data = buffering_data_sets[servlet]
				data.append(point)
				if len(data) >= 30:
					dgram = diagram.DataSettings(data)
					dgram.dots_color = (randcolor(), randcolor(), randcolor())
					self.widget.diagram.add_data_set(servlet, dgram)
					del buffering_data_sets[servlet]

def main():
	window = gtk.Window()
	window.set_title('Noodle 0.1')

	noodle_widget = NoodleWidget()
	window.add(noodle_widget)
	window.connect('delete-event', gtk.main_quit)

	window.show_all()

	collector = DataCollector(noodle_widget)
	collector.start()

	gtk.main()

if __name__ == '__main__':
	main()
