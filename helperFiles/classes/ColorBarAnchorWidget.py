import pyqtgraph as pg
class ColorBarAnchorWidget(pg.PlotItem, pg.GraphicsWidgetAnchor):
    def __init__(self):
        pg.PlotItem.__init__(self)
        pg.GraphicsWidgetAnchor.__init__(self)

    def setParent(self, parent):
        self.parent = parent
