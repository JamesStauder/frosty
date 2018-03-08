##################################
#Creator: James Stauder
#Creation Date: 1/30/18
#Last edit Date: 2/05/18
#Purpose: Class to make Dataset objects
#Parameters: 
#name -> name of dataset
#pen -> color of pen to use in plotting
#Attributes:
#name -> name of dataset
#pen -> color of pen to use in plotting
#interp -> interpolator based 
#
#
##################################


import h5py
import pyqtgraph as pg
from ..constants import *
from ..createColorMaps import *
from pylab import sqrt, linspace
from scipy.interpolate import RectBivariateSpline
import numpy as np
import time

class Dataset():
    def __init__(self, name, pen):
        self.name = name
        self.pen = pen


        #TODO can these be changed to globals? Takes no time to do but it is done on repeat
        bed_xarray = linspace(map['proj_x0'], map['proj_x1'], map['x1'], endpoint=True)
        bed_yarray = linspace(map['proj_y1'], map['proj_y0'], map['y1'], endpoint=True)


        if self.name == 'velocity':
            self.data, self.vx, self.vy = self.setData(name)
            self.vxInterp = RectBivariateSpline(bed_xarray, bed_yarray, np.flipud(self.vx).transpose())
            self.vyInterp = RectBivariateSpline(bed_xarray, bed_yarray, np.flipud(self.vy).transpose())

        else:
            self.data = self.setData(name)

        self.interp   = RectBivariateSpline(bed_xarray, bed_yarray, np.flipud(self.data).transpose())

        #Only create color map if we wish to render possible in the future where we wish to create Dataset for backend web
        if render and name != 'VX' and name != 'VY':
            createColorMap(self)
            self.pathPlotItem = pg.PlotDataItem([0,0], pen=self.pen)


    def setData(self, name):
        dataFile = h5py.File(dataFileName, 'r')
        if name == 'velocity':
            vx = dataFile['VX'][:]
            vy = dataFile['VY'][:]
            data = sqrt(vx**2 + vy**2)
            dataFile.close()
            return data, vx, vy
        else:
            data = dataFile[name][:]
            dataFile.close()
            return data

    def getInterpolatedValue(self, xPosition, yPosition):
        return self.interp(xPosition, yPosition)

    
        
