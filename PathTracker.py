from enum import Enum
from typing import List, Tuple


class PathType(Enum):
    REFRACTED = 1
    REFLECTED = 2


class Path:
    def __init__(self, type: PathType):
        self.__way: tuple[float, float] = []
        self.__type = type
        self.__finalized = False
        self.__flavor = 0

    def add_point(self, point: tuple[float, float]):
        self.__way.append(point)

    def points(self):
        return self.__way

    def numberOfPoints(self):
        return len(self.__way)

    def type(self):
        return self.__type

    def finalize(self, flavor: int):
        self.__finalized = True
        self.__flavor = flavor
        endX = self.__way[-1][0]
        if self.__type == PathType.REFLECTED:
            for i in reversed(range(0, len(self.__way) - 1)):
                point = self.__way[i]
                self.__way.append((endX + (endX - point[0]), point[1]))
        else:
            enterBoundaryX = self.__way[-2][0]
            for i in reversed(range(0, len(self.__way) - 2)):
                point = self.__way[i]
                self.__way.append(
                    (endX + (enterBoundaryX - point[0]), point[1]))

    def flavor(self):
        return self.__flavor

    def isFinalized(self) -> bool:
        return self.__finalized

    def __str__(self) -> str:
        out = "<Path>" + str(self.__type)
        for p in self.__way:
            out += "\n\t" + str(p)
        return out


class PathTracker:
    def __init__(self) -> None:
        self.__paths: List(Path) = []

    def newPath(self, type: PathType) -> int:
        self.__paths.append(Path(type))
        return len(self.__paths)-1

    def addPoint(self, pathIndex: int, point: tuple[float, float]):
        if pathIndex > len(self.__paths):
            print("No!")
            exit()
        self.__paths[pathIndex].add_point(point)

    def clonePath(self, pathIndex: int) -> int:
        path = self.__paths[pathIndex]
        newPathIndex = self.newPath(path.type())
        for p in path.points():
            self.addPoint(newPathIndex, p)
        return newPathIndex

    def finalize(self, pathIndex: int, flavor: int) -> None:
        path = self.__paths[pathIndex]
        path.finalize(flavor)

    def relevantPaths(self, maximumX: float):
        paths = []
        for p in self.__paths:
            if p.points()[-1][0] > maximumX:
                continue
            paths.append(p)
        return paths

    def dump(self):
        count = 0
        finalized = 0
        unfinalized = 0
        for p in self.__paths:
            count += p.numberOfPoints()
            if p.isFinalized():
                finalized += 1
            else:
                unfinalized += 1
        print(str(count) + " Points")
        print(str(finalized) + " Paths finalized")
        print(str(unfinalized) + " Paths unfinalized")

        print(self.__paths[25000])
        print(self.__paths[1001])
