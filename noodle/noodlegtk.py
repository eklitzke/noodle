#!/usr/bin/env python

import pygtk
pygtk.require('2.0')

import gobject
import pango
import gtk
import math
import time
import random
from gtk import gdk

from noodle import util
from noodle import diagram

from noodle.collector import *
try:
	from noodle.yelp import *
except ImportError:
	pass

if gtk.pygtk_version < (2,3,93):
    print "PyGtk 2.3.93 or later required"
    raise SystemExit

gobject.threads_init()

import diagram
import gtk
import gobject

import optparse

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

def main():

	parser = optparse.OptionParser()
	opts, args = parser.parse_args()
	if len(args) >= 2:
		print 'Only one collector may be specified!'
		sys.exit(0)
	args = args or ['TestDataCollector']
	collector_cls = globals()[args[0]]

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

	collector = collector_cls(noodle_widget)
	collector.start()

	gtk.main()

if __name__ == '__main__':
	main()
