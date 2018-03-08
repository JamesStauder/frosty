import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

class FlowlinePath(pg.PlotDataItem):

    def __init__(self):
        # Index of point being dragged
        self.drag_index = None
        # How far to translate dragged point from original position
        self.drag_offset = None
        # Brush for highlighted point
        self.selected_brush = pg.mkBrush('r')
        # Brush for default points
        self.default_brush = pg.mkBrush('k')
        # Number of points
        self.num_points = 0
        # Index of selected point
        self.selected_indexes = set([])
        # Extend mode?
        self.extend_mode = False
        # Moving point
        self.moving_point_index = None
        # Control button pressed
        self.ctrl_pressed = False

        pg.PlotDataItem.__init__(self)

        ### Event handling
        # Triggered when a point is clicked
        self.scatter.sigClicked.connect(self.pointClicked)


    ### Sets the initial data
    def setData(self, **kwds):
        self.data = kwds

        # Check to make sure we have all required fields
        if 'x' in kwds and 'y' in kwds:
            # Set positions
            self.setPositionData(self.data.pop('x'), self.data.pop('y'))
            # Set data for each point
            self.setPointData()
            # Refresh list of symbol brushes
            self.setSymbolBrushes()
            # Update graph
            self.updateGraph()


    ### Set position data
    def setPositionData(self, xs, ys):
        self.num_points = len(xs)
        self.data['x'] = xs
        self.data['y'] = ys


    ### Gets the position of a point with the given index
    def getPosition(self, index):
        return np.array([self.data['x'][index], self.data['y'][index]])


    ### Sets coordinates of point with given index
    def setPointCoords(self, index, coords):
        self.data['x'][index] = coords[0]
        self.data['y'][index] = coords[1]


    ### Get coordinates of point with given index
    def getPointCoords(self, index):
        return np.array([self.data['x'][index], self.data['y'][index]])


    ### Set additional data associated with each point
    def setPointData(self):
        self.data['data'] = np.empty(self.num_points, dtype=[('index', int)])
        self.data['data']['index'] = np.arange(self.num_points)


    ### Sets symbol brushes after points have been inserted or removed
    def setSymbolBrushes(self):
        brushes = np.empty(self.num_points, dtype=object)
        brushes[:] = self.default_brush
        self.data['symbolBrush'] = brushes


    ### Insert a point at given index
    def insertPoint(self, index, coords):
        self.num_points += 1

        # Insert position data
        self.data['x'] = np.insert(self.data['x'], index, coords[0])
        self.data['y'] = np.insert(self.data['y'], index, coords[1])

        # Update point data
        self.data['data'] = np.append(self.data['data'], np.array((self.num_points - 1,), self.data['data'].dtype))

        # Update symbol brushes
        self.data['symbolBrush'] = np.append(self.data['symbolBrush'], self.default_brush)


    ### Adds a point at beginning of path
    def addPointStart(self, coords):
        self.insertPoint(0, coords)


    ### Adds a point at end of path
    def addPointEnd(self, coords):
        self.insertPoint(self.num_points, coords)


    ### Remove points with given indexes
    def removePoints(self, indexes):
        self.num_points -= len(indexes)

        # Update point data
        self.data['x'] = np.delete(self.data['x'], indexes)
        self.data['y'] = np.delete(self.data['y'], indexes)

        # Reset point data, brushes, selected indexes
        self.setPointData()
        self.setSymbolBrushes()
        self.selected_indexes.clear()


    ### Indicates a point is selected by usnig a different brush
    def addSelectedPoint(self, index):
        self.selected_indexes.add(index)
        self.data['symbolBrush'][index] = self.selected_brush


    ### Deselect all currently selected point
    def deselectAll(self):
        for index in self.selected_indexes:
            self.data['symbolBrush'][index] = self.default_brush
        self.selected_indexes.clear()


    ### Respond to a mouse drag
    def mouseDragEvent(self, ev):

        self.selectFlowline(self)

        if ev.button() != QtCore.Qt.LeftButton:
            ev.ignore()
            return

        if ev.isStart():
            # We are already one step into the drag. Find the point(s) at the mouse
            # cursor when the button was first pressed:
            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)

            if len(pts) == 0:
                ev.ignore()
                return

            # Get the index of the dragged point
            self.drag_index = pts[0].data()[0]
            # Offset from the original position
            self.drag_offset = self.getPointCoords(self.drag_index) - pos
            # Select only this point
            self.deselectAll()
            self.addSelectedPoint(self.drag_index)

        elif ev.isFinish():
            self.drag_index = None
            return
        else:
            if self.drag_index is None:
                ev.ignore()
                return

        # In the midst of a drag
        self.setPointCoords(self.drag_index, ev.pos() + self.drag_offset)
        self.updateGraph()
        ev.accept()


    ### Dumb setter function for extend mode so I can keep track of when
    ### extend mode is toggled
    def setExtendMode(self, mode):
        print "extend mode", mode
        self.extend_mode = mode


    ### Respond to a click that's not on a point
    def offPointClick(self):
        if self.extend_mode:
            self.extend()
        else :
            self.deselectAll()

        self.updateGraph()


    ### Respond to mouse movement
    def mouseMove(self, pos):
        # Get mouse coordinates
        coords = np.array([pos.x(), pos.y()])

        # Check if we're in extend mode
        if self.extend_mode:
            # Move the first or last point + associated boundary points to mouse coordinates
            self.setPointCoords(self.moving_point_index, coords)
            self.updateGraph()


    ### Extend the current path
    def extend(self):
        self.deselectAll()
        pos = self.getPointCoords(self.moving_point_index)

        if self.moving_point_index == 0:
            self.addPointStart(pos)
        else :
            self.addPointEnd(pos)
            self.moving_point_index += 1


    ### Event called when a point is clicked
    def pointClicked(self, p, pts):
        self.selectFlowline(self)

        if self.extend_mode:
            # If we're in extend mode, keep extending the path
            self.extend()
        else :
            # Otherwise selec a point
            if not self.ctrl_pressed:
                self.deselectAll()
            self.addSelectedPoint(pts[0].data()[0])

        self.updateGraph()


    ### Respond to delete key press
    def deleteKeyPressed(self):
        # If there is a selected point, and we're not in extend mode, delete it
        if (not self.extend_mode) and (not len(self.selected_indexes) == 0):
            self.removePoints(np.array(list(self.selected_indexes)))
            self.updateGraph()


    ### Triggers when e key is pressed for extend mode
    def extendKeyPressed(self):

        # Check if there's one selected point and it's either the first or last

        # One point is selected
        one_selected = len(self.selected_indexes) == 1
        # First center point is selected
        first_selected = 0 in self.selected_indexes
        # Last center point is selected
        last_selected =  self.num_points - 1 in self.selected_indexes

        # Combined conditional
        cond = one_selected and (last_selected or first_selected)

        if (not self.extend_mode) and cond:
            # Enable extend mode
            self.setExtendMode(True)
            self.deselectAll()

            # If selected point is at beginning of path, add points starting from
            # there. If selected point is at end, add points from there.

            if first_selected:
                pos = self.getPointCoords(0)
                # Add a point + children
                self.addPointStart(pos)
                # Set moving index to the index of the newly added center point
                self.moving_point_index = 0
            else :
                pos = self.getPointCoords(self.num_points - 1)
                self.addPointEnd(pos)
                self.moving_point_index = self.num_points - 1

        else :
            # Disable extend mode
            self.setExtendMode(False)
            self.deselectAll()

        self.updateGraph()


    ### Triggered when the subdivide key is pressed
    def subdivideKeyPressed(self):
        # If we're not in extend mode, check if there are two points selected
        if not self.extend_mode and len(self.selected_indexes) == 2:
            indexes = list(self.selected_indexes)

            # Check if two adjacent points are selected
            if abs(indexes[0] - indexes[1]) == 1:
                # Insert a new center point between the two selected center points
                pos1 = self.getPointCoords(indexes[0])
                pos2 = self.getPointCoords(indexes[1])

                new_pos = (pos1 + pos2) / 2.

                self.deselectAll()
                self.insertPoint(min(indexes) + 1, new_pos)
                self.updateGraph()


    ### Update the graph data so the graph is redrawn
    def updateGraph(self):
        pg.PlotDataItem.setData(self, **self.data)


    ### Several Necessary inherited function

    def shape(self):
        # Inherit shape from the curve item
        return self.scatter.shape()


    def boundingRect(self):
        # All graphics items require this method (unless they have no contents)
        return self.shape().boundingRect()


    def paint(self, p, *args):
        # All graphics items require this method (unless they have no contents)
        return

