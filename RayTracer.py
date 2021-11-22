import numpy as np
from Detector import Detector
from Model import Model
from PathTracker import PathTracker, PathType


class TimeDistanceTuple:
    def __init__(self, time: float, distance: float) -> None:
        self.time = time
        self.distance = distance

    def __repr__(self) -> str:
        return "TimeDistanceTuple: t " + str(self.time) + " d " + str(self.distance)


class RayTracer:
    def __init__(self, model: Model, detector: Detector, pathTracker: PathTracker):
        self.__model = model
        self.__detector = detector
        self.__pathTracker = pathTracker

    def runReflections(self, numberOfAngles: int) -> None:
        angles = np.linspace(0, np.pi/2, numberOfAngles)

        for angle in angles:
            lastDistances = self.__runSingleReflection(angle)
            if all(d > self.__detector.extend()["rangeEnd"] for d in lastDistances):
                break

    def __runSingleReflection(self, angle: float) -> float:
        slownessVectorX: float = np.sin(angle)/self.__model.layer(0).speed

        pt: PathTracker = self.__pathTracker
        endXs = []
        # Reflections:
        for boundaryIndex in range(1, self.__model.numberOfLayers()):
            pathIndex = self.__pathTracker.newPath(PathType.REFLECTED)
            pt.addPoint(pathIndex, (0, 0))

            timedistance = self.__reflectAtBoundary(
                boundaryIndex, slownessVectorX, pathIndex)
            self.__detector.event(timedistance.distance, timedistance.time)

            pt.finalize(pathIndex, boundaryIndex)
            endXs.append(timedistance.distance)
        return endXs

    def __reflectAtBoundary(self, boundaryIndex: int, slownessVectorX: float, pathTrackerIndex: int) -> TimeDistanceTuple:
        model = self.__model
        pt: PathTracker = self.__pathTracker

        if boundaryIndex > model.numberOfLayers() - 1:
            return None

        x = 0
        t = 0
        for k in range(boundaryIndex):
            layer = model.layer(k)
            sini = slownessVectorX * layer.speed
            if sini >= 1:
                continue
            squarerootFactor = np.sqrt(1 - np.square(sini))
            x += layer.height * slownessVectorX * layer.speed / squarerootFactor
            t += layer.height / (layer.speed * squarerootFactor)
            depth = self.__model.depthAtBoundary(k)
            pt.addPoint(pathTrackerIndex, (x, -depth))

        x *= 2
        t *= 2

        return TimeDistanceTuple(t, x)

    def runRefractions(self, timestepForHeadWave: float, maximumDistance: float):
        for boundaryIndex in range(1, self.__model.numberOfLayers()):
            self.__runSingleRefraction(
                boundaryIndex, timestepForHeadWave, maximumDistance)

    def __runSingleRefraction(self, boundaryIndex: int, timestepForHeadWave: float, maximumDistance: float):
        lowerSpeed = self.__model.layer(boundaryIndex).speed
        criticalSlownessVectorX = 1 / lowerSpeed

        pt: PathTracker = self.__pathTracker
        pathIndex = self.__pathTracker.newPath(PathType.REFRACTED)
        pt.addPoint(pathIndex, (0, 0))

        reflectionPart = self.__reflectAtBoundary(
            boundaryIndex, criticalSlownessVectorX, pathIndex)

        depth = self.__model.depthAtBoundary(boundaryIndex - 1)

        distanceAsHeadWave = 0
        timeAsHeadWave = 0
        while(reflectionPart.distance + distanceAsHeadWave <= maximumDistance):
            timeAsHeadWave += timestepForHeadWave
            distanceAsHeadWave = lowerSpeed * timeAsHeadWave
            x = reflectionPart.distance + distanceAsHeadWave
            self.__detector.event(x, reflectionPart.time + timeAsHeadWave)

            newPathIndex = pt.clonePath(pathIndex)
            pt.addPoint(newPathIndex, (x, -depth))
            pt.finalize(newPathIndex, boundaryIndex)
