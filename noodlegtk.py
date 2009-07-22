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

import draw

try:
    import cairo
except ImportError:
    pass

if gtk.pygtk_version < (2,3,93):
    print "PyGtk 2.3.93 or later required"
    raise SystemExit

TEXT = 'TeamCA'
BORDER_WIDTH = 10

class NoodleWidget(gtk.Widget):

	__gsignals__ = { 'realize': 'override',
					 'expose-event' : 'override',
					 'size-allocate': 'override',
					 'size-request': 'override',}

	def __init__(self):
		gtk.Widget.__init__(self)
		self.draw_gc = None
		self.layout = self.create_pango_layout(TEXT)
		self.layout.set_font_description(pango.FontDescription("sans serif 8"))

		self.epoch = 0

		def progress_timeout(obj):
			x, y, w, h = obj.allocation
			obj.window.invalidate_rect((0,0,w,h),False)
			self.epoch += 1
			if (self.epoch >= len(self.json_data)):
				self.epoch = 0
			return True

		# Draw the simulation at 24 fps
		#gobject.timeout_add(1000 / 24.0, progress_timeout, self)

	def do_realize(self):
		self.set_flags(self.flags() | gtk.REALIZED)
		self.window = gdk.Window(self.get_parent_window(),
								 width=self.allocation.width,
								 height=self.allocation.height,
								 window_type=gdk.WINDOW_CHILD,
								 wclass=gdk.INPUT_OUTPUT,
								 event_mask=self.get_events() | gdk.EXPOSURE_MASK)
		if not hasattr(self.window, "cairo_create"):
			self.draw_gc = gdk.GC(self.window,
								  line_width=5,
								  line_style=gdk.SOLID,
								  join_style=gdk.JOIN_ROUND)

		self.window.set_user_data(self)
		self.style.attach(self.window)
		self.style.set_background(self.window, gtk.STATE_NORMAL)
		self.window.move_resize(*self.allocation)

	def do_size_request(self, requisition):
		width, height = self.layout.get_size()
		requisition.width = (width // pango.SCALE + BORDER_WIDTH*4)* 1.45
		requisition.height = (3 * height // pango.SCALE + BORDER_WIDTH*4) * 1.2

	def do_size_allocate(self, allocation):
		self.allocation = allocation
		if self.flags() & gtk.REALIZED:
			self.window.move_resize(*allocation)

	def _expose_gdk(self, event):
		x, y, w, h = self.allocation
		self.layout = self.create_pango_layout('no cairo')
		fontw, fonth = self.layout.get_pixel_size()
		self.style.paint_layout(self.window, self.state, False,
								event.area, self, "label",
								(w - fontw) / 2, (h - fonth) / 2,
								self.layout)

	def do_expose_event(self, event):
		self.chain(event)
		try:
			cr = self.window.cairo_create()
		except AttributeError:
			return self._expose_gdk(event)

		diagram_settings = draw.DiagramSettings()
		diagram_settings.title = 'Hello World Graph'
		diagram = draw.NoodleDiagram(diagram_settings, cr=cr)
		diagram.WIDTH = self.allocation.width
		diagram.HEIGHT = self.allocation.height

		for data in draw.example_data:
			diagram.add_data(data)

		diagram.draw()
	
	def do_size_request(self, requisition):
		requisition.height = 600
		requisition.width = 800

win = gtk.Window()
win.set_title('Noodle 0.1')
win.connect('delete-event', gtk.main_quit)

event_box = gtk.EventBox()

win.add(event_box)

w = NoodleWidget()
event_box.add(w)

win.show_all()

gtk.main()
