import matplotlib
from matplotlib import markers
from RayTracer import RayTracer
import sys
import numpy as np
import matplotlib.pyplot as mpl
from Detector import Detector
from Model import Model
from PathTracker import PathTracker, PathType
matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['figure.dpi'] = 300


def main():

    timeGranularity = .02
    widthOfStructure = 200e3
    numberOfSensors = 600
    anglesForReflection = 10000
    numberOfPathsPerFlavor = 5

    colors = ["r", "g", "b", "y", "c", "m"]

    d = Detector(rangeStart=0, rangeEnd=widthOfStructure,
                 numberOfSensors=numberOfSensors, timeGranularity=timeGranularity)

    pt = PathTracker()

    m = Model()
    m.addLayer(20000, 6000)  # upper crust
    m.addLayer(10000, 6800)  # lower crust
    # -- Moho
    m.addLayer(0, 8200)  # upper mantle

    rt = RayTracer(m, d, pt)

    # surface wave
    surfaceSpeed = 6000  # m/s
    for x in range(int(widthOfStructure/100)):
        d.event(x*100, (x*100)/surfaceSpeed)

    rt.runReflections(anglesForReflection)
    rt.runRefractions(timestepForHeadWave=timeGranularity/10,
                      maximumDistance=widthOfStructure)

    cm = 1/2.54

    # Unreduced Seismogram

    d.processData()
    e = d.extend()
    normalizedUnreducedData = np.where(d.data() > 0, 1, 0)

    # 1cm = 10km, 1cm=2s
    fig, usualPlot = mpl.subplots(1, 1, figsize=(
        ((e['rangeEnd']-e['rangeStart'])/10000)*cm + 2, ((e['largestTime']-min(e['smallestTime'], 0))/2)*cm + 2))
    usualPlot.imshow(np.fliplr(normalizedUnreducedData).T, extent=[e['rangeStart'], e['rangeEnd'], min(e['smallestTime'], 0), e['largestTime']],
                     interpolation='none', aspect='auto', cmap='binary')
    usualPlot.set_xlabel('Distance in m')
    usualPlot.set_ylabel('TWT in s')
    usualPlot.set_title(
        'Usual distance-time-diagram')
    usualPlot.ticklabel_format(axis='x', style='sci',
                               scilimits=(3, 3), useMathText=True)
    usualPlot.grid(visible=True, which='major', linestyle='-', alpha=0.5)
    usualPlot.minorticks_on()
    usualPlot.grid(visible=True, which='minor', linestyle='--', alpha=0.25)
    mpl.savefig('output/seismogram-usual.png')

    # Reduced Seismogram

    d.processData(reductionVelocity=6000)
    e = d.extend()
    fig, reducedPlot = mpl.subplots(1, 1, figsize=(
        ((e['rangeEnd']-e['rangeStart'])/10000)*cm + 2, ((e['largestTime']-min(e['smallestTime'], 0))/2)*cm + 2))
    normalizedReducedData = np.where(d.data() > 0, 1, 0)
    reducedPlot.imshow(np.fliplr(normalizedReducedData).T, extent=[e['rangeStart'], e['rangeEnd'], min(e['smallestTime'], 0), e['largestTime']],
                       interpolation='none', aspect='auto', cmap='binary')
    reducedPlot.set_xlabel('Distance in m')
    reducedPlot.set_ylabel('Reduced travel time in s')
    reducedPlot.set_title(
        r'time-distance-diagram with $v_{red} = 6000\ ms^{-1}$')
    reducedPlot.ticklabel_format(axis='x', style='sci',
                                 scilimits=(3, 3), useMathText=True)
    reducedPlot.grid(visible=True, which='major', linestyle='-', alpha=0.5)
    reducedPlot.minorticks_on()
    reducedPlot.grid(visible=True, which='minor', linestyle='--', alpha=0.25)
    mpl.savefig('output/seismogram-reduced.png')

    # Paths
    allThePaths = pt.relevantPaths(widthOfStructure)

    fig, pathWays = mpl.subplots(1, 1, figsize=(14, 8))

    # Surface
    pathWays.plot([0, widthOfStructure], [0, 0], "k-")

    # Model
    for k in range(m.numberOfLayers() - 1):
        depth = -m.depthAtBoundary(k)
        pathWays.plot([0, widthOfStructure], [depth, depth], "k-")

    # Paths
    reflectedFlavors = list([] for _ in range(m.numberOfLayers()))
    refractedFlavors = list([] for _ in range(m.numberOfLayers()))

    for i in range(len(allThePaths)):
        path = allThePaths[i]
        if path.type() == PathType.REFLECTED:
            reflectedFlavors[path.flavor()].append(path)
        else:
            refractedFlavors[path.flavor()].append(path)
    for i in range(1, m.numberOfLayers()):
        reflectedFlavors[i]
        refractedFlavors[i]

        reflectedIndices = np.round(np.linspace(
            0, len(reflectedFlavors[i]) - 1, numberOfPathsPerFlavor)).astype(int)
        refractedIndices = np.round(np.linspace(
            0, len(refractedFlavors[i]) - 1, numberOfPathsPerFlavor)).astype(int)

        selectedReflections = np.array(reflectedFlavors[i])[reflectedIndices]
        selectedRefractions = np.array(refractedFlavors[i])[refractedIndices]

        for ray in selectedReflections:
            xs = [j[0] for j in ray.points()]
            ys = [j[1] for j in ray.points()]
            pathWays.plot(xs, ys, "-", marker='None',
                          color=colors[i-1], linewidth=.5)

        for ray in selectedRefractions:
            xs = [j[0] for j in ray.points()]
            ys = [j[1] for j in ray.points()]
            pathWays.plot(xs, ys, "-", marker='None',
                          color=colors[i - 1 + m.numberOfLayers()], linewidth=.5)

    pathWays.ticklabel_format(axis='both', style='sci',
                              scilimits=(3, 3), useMathText=True)
    pathWays.set_xlabel("Distance in m")
    pathWays.set_ylabel("Depth in m")

    mpl.savefig('output/paths.png')


if __name__ == '__main__':
    main()
