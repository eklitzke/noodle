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

import widget

try:
    import cairo
except ImportError:
    pass

if gtk.pygtk_version < (2,3,93):
    print "PyGtk 2.3.93 or later required"
    raise SystemExit

if __name__ == '__main__':
	window = gtk.Window()
	window.set_title('Noodle 0.1')

	noodle_widget = widget.NoodleWidget()
	window.add(noodle_widget)
	window.connect('delete-event', gtk.main_quit)

	window.show_all()

	gtk.main()
