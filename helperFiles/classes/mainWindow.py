import sys
from PyQt4.QtGui import *
from pyqtgraph.Qt import QtGui
from Instructions import *
from FlowlinePath import *
from Dataset import *
from Marker import *


class mainWindow(QMainWindow):
    def __init__(self, parent=None):

        super(mainWindow, self).__init__(parent)
        self.setWindowTitle("Greenland")
        self.setMinimumHeight(1000)
        self.setMinimumWidth(1200)

        self.centralWidget = QtGui.QWidget()
        self.setCentralWidget(self.centralWidget)
        self.mainLayout = QtGui.QHBoxLayout()
        self.centralWidget.setLayout(self.mainLayout)

        # index of current map
        self.currentMap = 0

        # marker selected variables
        self.isMarkerSelected = False
        self.whichMarkerSelected = None
        self.selectedMarkerPosition = None

        self.flowlines = []

        '''
        Side widget with button
        '''
        self.maxWidth = 300

        self.buttonBoxWidget = QtGui.QWidget()
        self.buttonBox = QtGui.QVBoxLayout()
        self.buttonBoxWidget.setLayout(self.buttonBox)

        self.mapList = QtGui.QComboBox()
        self.maps = ['Velocity', 'Bed', 'Surface', 'SMB', 'Thickness', 't2m']
        self.mapList.addItems(self.maps)
        self.mapList.setMaximumWidth(self.maxWidth)
        self.buttonBox.addWidget(self.mapList)

        self.autoCorrectVpt = QtGui.QCheckBox('Auto-correct Marker pos.')
        self.autoCorrectVpt.setTristate(False)
        self.autoCorrectVpt.setCheckState(0)
        self.autoCorrectVpt.setMaximumWidth(self.maxWidth)
        self.buttonBox.addWidget(self.autoCorrectVpt)

        self.instructionButton = QtGui.QPushButton('Instructions')
        self.instructionButton.setEnabled(True)
        self.instructionButton.setMaximumWidth(self.maxWidth)
        self.buttonBox.addWidget(self.instructionButton)

        self.plotPathButton = QtGui.QPushButton('Plot Path')
        self.plotPathButton.setEnabled(False)
        self.plotPathButton.setMaximumWidth(self.maxWidth)
        self.buttonBox.addWidget(self.plotPathButton)

        self.runModelButton = QtGui.QPushButton('Run Model')
        self.runModelButton.setEnabled(False)
        self.runModelButton.setMaximumWidth(self.maxWidth)
        self.buttonBox.addWidget(self.runModelButton)

        self.generateMeshButton = QtGui.QPushButton('Generate Mesh')
        self.generateMeshButton.setEnabled(False)
        self.generateMeshButton.setMaximumWidth(self.maxWidth)
        self.buttonBox.addWidget(self.generateMeshButton)

        self.velocityWidthButton = QtGui.QPushButton('Velocity Width')
        self.velocityWidthButton.setEnabled(False)
        self.velocityWidthButton.setMaximumWidth(self.maxWidth)
        self.buttonBox.addWidget(self.velocityWidthButton)

        self.textOut = QtGui.QTextBrowser()
        self.textOut.setMaximumWidth(self.maxWidth)
        self.buttonBox.addWidget(self.textOut)

        self.leftSideWidget = QtGui.QWidget()
        self.leftSide = QtGui.QVBoxLayout()
        self.leftSideWidget.setLayout(self.leftSide)

        self.imageIconContainer = QtGui.QStackedWidget()

        self.leftSide.addWidget(self.imageIconContainer)

        self.mainLayout.addWidget(self.leftSideWidget)
        self.mainLayout.addWidget(self.buttonBoxWidget)

        self.buttonBoxWidget.setMaximumWidth(self.maxWidth + 12)

        self.connectButtons()

    def changeMap(self, index):
        vr = self.imageIconContainer.currentWidget().getPlotItem().getViewBox().viewRange()
        indexToDatasetDict = {
            0: 'velocity',
            1: 'bed',
            2: 'surface',
            3: 'smb',
            4: 'thickness',
            5: 't2m'}
        if index != self.currentMap:
            oldMap = self.currentMap
            self.currentMap = index
        self.imageIconContainer.setCurrentWidget(self.datasetDict[indexToDatasetDict[index]].plotWidget)

    def mouseClick(self, e):

        ##If no marker is selected
        if self.isMarkerSelected == False:

            ##Check to see if a marker is selected
            for flowline in self.flowlines:
                for marker in flowline:
                    if (marker.checkClicked(e.pos())):
                        self.isMarkerSelected = True
                        self.whichMarkerSelected = marker
                        self.displayMarkerVariables()

            for i in range(len(self.flowlines)):
                for j in range(len(self.flowlines[i])):
                    if (self.flowlines[i][j].checkClicked(e.pos())):
                        self.isMarkerSelected = True
                        self.whichMarkerSelected = self.flowlines[i][j]
                        self.selectedMarkerPosition = [i, j]
                        self.displayMarkerVariables()

            ##If no marker selected previously or currently create new flowline            
            if (len(self.flowlines) < 2) and self.isMarkerSelected == False:
                xClickPosition = e.pos().x()
                yClickPosition = e.pos().y()

                newFlowline = []
                self.lengthOfFlowline = 30
                for x in range(0, self.lengthOfFlowline):
                    newFlowline.append(None)

                dx, dy = colorToProj(xClickPosition, yClickPosition)
                newFlowline[0] = Marker(xClickPosition, yClickPosition, dx, dy, self.imageIconContainer.currentWidget())

                self.imageIconContainer.currentWidget().addItem(newFlowline[0].getCross()[0])
                self.imageIconContainer.currentWidget().addItem(newFlowline[0].getCross()[1])

                newFlowline = self.flowIntegrator.integrate(dx, dy, newFlowline, 0,
                                                            self.imageIconContainer.currentWidget())

                for i in range(1, len(newFlowline)):
                    self.imageIconContainer.currentWidget().addItem(newFlowline[i].getCross()[0])
                    self.imageIconContainer.currentWidget().addItem(newFlowline[i].getCross()[1])
                    xa = [newFlowline[i - 1].cx, newFlowline[i].cx]
                    ya = [newFlowline[i - 1].cy, newFlowline[i].cy]
                    newFlowline[i].setLine(pg.PlotDataItem(xa, ya, connect='all', pen=skinnyBlackPlotPen), 0)
                    newFlowline[i - 1].setLine(newFlowline[i].lines[0], 1)
                    self.imageIconContainer.currentWidget().addItem(newFlowline[i].lines[0])

                self.flowlines.append(newFlowline)

                if len(self.flowlines) == 2:
                    self.velocityWidthButton.setEnabled(True)

        ##Release the marker that was previously held
        else:
            self.isMarkerSelected = False
            self.whichMarkerSelected = None
            self.textOut.clear()

    ##Move marker. Need to finish
    def mouseMove(self, e):
        if self.isMarkerSelected:

            xPosition = e.pos().x()
            yPosition = e.pos().y()
            self.whichMarkerSelected.cx = xPosition
            self.whichMarkerSelected.cy = yPosition
            self.whichMarkerSelected.updateCross()

            whichFlowline = self.flowlines[self.selectedMarkerPosition[0]]
            whichMarker = whichFlowline[self.selectedMarkerPosition[1]]

            dx, dy = colorToProj(self.whichMarkerSelected.cx, self.whichMarkerSelected.cy)

            for i in range(self.selectedMarkerPosition[1] + 1, self.lengthOfFlowline):
              self.imageIconContainer.currentWidget().removeItem(whichFlowline[i])

            whichFlowline = self.flowIntegrator.integrate(dx, dy, whichFlowline, self.selectedMarkerPosition[1],
                                                          self.imageIconContainer.currentWidget())

            for i in range(self.selectedMarkerPosition[1] + 1, self.lengthOfFlowline):
                self.imageIconContainer.currentWidget().addItem(whichFlowline[i].getCross()[0])
                self.imageIconContainer.currentWidget().addItem(whichFlowline[i].getCross()[1])

                xa = [whichFlowline[i - 1].cx, whichFlowline[i].cx]
                ya = [whichFlowline[i - 1].cy, whichFlowline[i].cy]
                whichFlowline[i].setLine(pg.PlotDataItem(xa, ya, connect='all', pen=skinnyBlackPlotPen), 0)
                whichFlowline[i - 1].setLine(whichFlowline[i].lines[0], 1)

                self.imageIconContainer.currentWidget().addItem(whichFlowline[i].lines[0])

            self.displayMarkerVariables()

            if self.whichMarkerSelected.lines[0] is not None:
                self.whichMarkerSelected.lines[0].setData(
                    [self.whichMarkerSelected.lines[0].getData()[0][0], self.whichMarkerSelected.cx],
                    [self.whichMarkerSelected.lines[0].getData()[1][0], self.whichMarkerSelected.cy])

            if self.whichMarkerSelected.lines[1] is not None:
                self.whichMarkerSelected.lines[1].setData(
                    [self.whichMarkerSelected.cx, self.whichMarkerSelected.lines[1].getData()[0][1]],
                    [self.whichMarkerSelected.cy, self.whichMarkerSelected.lines[1].getData()[1][1]])

    def showInstructions(self):
        Instructions(self)

    def calcVelocityWidth(self):
        for i in range(len(self.flowlines[0])):
            xValues = [self.flowlines[1][i].cx, self.flowlines[0][i].cx, self.flowlines[2][i].cx]
            yValues = [self.flowlines[1][i].cy, self.flowlines[0][i].cy, self.flowlines[2][i].cy]
            self.flowlines[0][i].setLine(pg.PlotDataItem(xValues, yValues, connect='all', pen=skinnyBlackPlotPen), 0)
            self.imageIconContainer.currentWidget().addItem(self.flowlines[0][i].lines[0])

            velWidth = sqrt((self.flowlines[1][i].dx - self.flowlines[0][i].dx) ** 2 + (
            self.flowlines[1][i].dy - self.flowlines[0][i].dy) ** 2)
            velWidth = velWidth + sqrt((self.flowlines[2][i].dx - self.flowlines[0][i].dx) ** 2 + (
            self.flowlines[2][i].dy - self.flowlines[0][i].dy) ** 2)

            outString = "velocity width at line " + str(i) + " " + str(velWidth)

            self.textOut.append(outString)

    def calcVelocityWidth2(self):
        x1, y1 = self.flowlines[0][0].cx, self.flowlines[0][0].cy
        x2, y2 = self.flowlines[1][0].cx, self.flowlines[1][0].cy

        # print(x1, y1, x2, y2)
        # print(self.flowlines[0][0].dx, self.flowlines[0][0].dy,self.flowlines[1][0].dx, self.flowlines[1][0].dy )
        xMid = (x1 + x2) / 2
        yMid = (y1 + y2) / 2
        xProj, yProj = colorToProj(xMid, yMid)

        # print(xMid, yMid, xProj, yProj)

        newMarker = Marker(xMid, yMid, xProj, yProj, self.imageIconContainer.currentWidget().parent())
        self.imageIconContainer.currentWidget().addItem(newMarker.getCross()[0])
        self.imageIconContainer.currentWidget().addItem(newMarker.getCross()[1])


        midFlowline = []
        for i in range(self.lengthOfFlowline):
            midFlowline.append(None)

        midFlowline[0] = newMarker
        midFlowline = self.flowIntegrator.integrate(xProj, yProj, midFlowline, 0,
                                                      self.imageIconContainer.currentWidget().parent())


        #TODO make flowline drawing one function called
        for i in range(1, len(midFlowline)):
            self.imageIconContainer.currentWidget().addItem(midFlowline[i].getCross()[0])
            self.imageIconContainer.currentWidget().addItem(midFlowline[i].getCross()[1])
            xa = [midFlowline[i - 1].cx, midFlowline[i].cx]
            ya = [midFlowline[i - 1].cy, midFlowline[i].cy]
            midFlowline[i].setLine(pg.PlotDataItem(xa, ya, connect='all', pen=skinnyBlackPlotPen), 0)
            midFlowline[i - 1].setLine(midFlowline[i].lines[0], 1)
            self.imageIconContainer.currentWidget().addItem(midFlowline[i].lines[0])

        self.flowlines.append(midFlowline)

        for i in range(len(self.flowlines[0])):
            xValues = [self.flowlines[1][i].cx, self.flowlines[0][i].cx]
            yValues = [self.flowlines[1][i].cy, self.flowlines[0][i].cy]
            self.flowlines[0][i].setLine(pg.PlotDataItem(xValues, yValues, connect='all', pen=skinnyBlackPlotPen), 0)
            self.imageIconContainer.currentWidget().addItem(self.flowlines[0][i].lines[0])

            flowlinesX = [self.flowlines[0][i].dx, self.flowlines[1][i].dx, self.flowlines[2][i].dx]
            flowlinesY = [self.flowlines[0][i].dy, self.flowlines[1][i].dy, self.flowlines[2][i].dy]


            for j in range(2):
                print "Shear Margin " + str(j) + " Marker " + str(i)
                for x in self.maps:
                    dataString = str(self.datasetDict[x.lower()].getInterpolatedValue(flowlinesX[j], flowlinesY[j]))
                    print x + ": " + dataString[2:-2]
                print ""

            print "Mid Flowline - Marker: " + str(i)
            for x in self.maps:
                dataString = str(self.datasetDict[x.lower()].getInterpolatedValue(flowlinesX[2], flowlinesY[2]))
                print x + ": " + dataString[2:-2]
            print ""





    def displayMarkerVariables(self):
        self.textOut.clear()
        selectedMarkerX = self.whichMarkerSelected.dx
        selectedMarkerY = self.whichMarkerSelected.dy

        for x in self.maps:
            stringOut = str(self.datasetDict[x.lower()].getInterpolatedValue(selectedMarkerX, selectedMarkerY))
            self.textOut.append(x + ": " + stringOut[2:-2])

    def createIntegrator(self):
        vx = Dataset('VX', tealPlotPen)
        vy = Dataset('VY', tealPlotPen)
        self.flowIntegrator = FlowIntegrator(vx, vy)

    def connectButtons(self):
        self.mapList.currentIndexChanged.connect(self.changeMap)
        self.instructionButton.clicked.connect(self.showInstructions)
        self.velocityWidthButton.clicked.connect(self.calcVelocityWidth2)
