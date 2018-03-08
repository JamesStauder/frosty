import fenics as fc
from scipy.interpolate import interp1d
import numpy as np


'''
Function: dataToHDF5
Argument list: fileName,distanceData, thicknessPathData, bedPathData, surfacePathData, smbPathData, velocityPathData, 
resolution(ideal resolution is 1000 for our dataset)
Purpose: Write our data that is pre determined to an HDF5 File
Return types, values:
Dependencies: interp1d from scipy, fenics package
Creator: James Stauder
Date created:2/23/18
Last edited: 2/23/18
'''


def dataToHDF5(fileName,distanceData, thicknessPathData, bedPathData, surfacePathData, smbPathData, velocityPathData, resolution=1000):
    '''
    Create interps for each of our variables
    '''
    thickness1dInterp = interp1d(distanceData, thicknessPathData)
    bed1dInterp = interp1d(distanceData, bedPathData)
    surface1dInterp = interp1d(distanceData, surfacePathData)
    smb1dInterp = interp1d(distanceData, smbPathData)
    velocity1dInterp = interp1d(distanceData, velocityPathData)

    numberOfPoints = int(np.floor(distanceData[-1] / float(resolution)))

    x = np.arange(0, (numberOfPoints + 1) * resolution, resolution)

    mesh = fc.IntervalMesh(numberOfPoints, 0, resolution * numberOfPoints)

    thicknessModelData = thickness1dInterp(x)
    bedModelData = bed1dInterp(x)
    surfaceModelData = surface1dInterp(x)
    smbModelData = smb1dInterp(x)
    velocityModelData = velocity1dInterp(x)

    THICKLIMIT = 10  # Minimum thickness of the ice

    H = surfaceModelData - bedModelData

    surfaceModelData[H <= THICKLIMIT] = bedModelData[H <= THICKLIMIT]

    hdfName = fileName
    hfile = fc.HDF5File(mesh.mpi_comm(), hdfName, "w")
    V = fc.FunctionSpace(mesh, "CG", 1)

    functThickness = fc.Function(V, name="Thickness")
    functBed = fc.Function(V, name="Bed")
    functSurface = fc.Function(V, name="Surface")
    functSMB = fc.Function(V, name="SMB")
    functVelocity = fc.Function(V, name="Velocity")

    functThickness.vector()[:] = thicknessModelData
    functBed.vector()[:] = bedModelData
    functSurface.vector()[:] = surfaceModelData
    functSMB.vector()[:] = smbModelData
    functVelocity.vector()[:] = velocityModelData

    hfile.write(functThickness.vector(), "/thickness")
    hfile.write(functBed.vector(), "/bed")
    hfile.write(functSurface.vector(), "/surface")
    hfile.write(functSMB.vector(), "/smb")
    hfile.write(functVelocity.vector(), "/velocity")
    hfile.write(mesh, "/mesh")
    hfile.close()