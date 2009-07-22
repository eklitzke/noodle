import diagram
import gtk

class NoodleWidget(gtk.DrawingArea):

	def __init__(self):
		gtk.DrawingArea.__init__(self)
		self.connect('expose_event', self.expose)

		diagram_settings = diagram.DiagramSettings()
		diagram_settings.title = 'Hello World Graph'
		noodle_diagram = diagram.NoodleDiagram(diagram_settings)

		for data in diagram.example_data:
			noodle_diagram.add_data(data)
		
		self.diagram = noodle_diagram

	def expose(self, widget, event):
		cr = widget.window.cairo_create()
		cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
		cr.clip()
		self.diagram.WIDTH = self.allocation.width
		self.diagram.HEIGHT = self.allocation.height
		self.diagram.draw(cr)
