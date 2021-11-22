from typing import List
import numpy as np


class Model:

    def __init__(self) -> None:
        self.__layers = []
        self.__boundaryDepths: List(float) = []

    def numberOfLayers(self) -> int:
        return len(self.__layers)

    def addLayer(self, height: float, speed: float) -> None:
        self.__layers.append(Layer(height, speed))
        if len(self.__boundaryDepths) == 0:
            self.__boundaryDepths.append(height)
        else:
            self.__boundaryDepths.append(self.__boundaryDepths[-1] + height)

    def layer(self, index: int) -> 'Layer':
        if not (0 <= index < self.numberOfLayers()):
            return None
        return self.__layers[index]

    def criticalAngleOfBoundary(self, bottomLayer: int) -> float:
        if bottomLayer > self.numberOfLayers() - 1:
            return -1
        return np.arcsin(self.layer(bottomLayer - 1).speed / self.layer(bottomLayer).speed)

    def depthAtBoundary(self, boundaryIndex):
        if boundaryIndex > len(self.__boundaryDepths):
            return -1
        return self.__boundaryDepths[boundaryIndex]


class Layer:
    def __init__(self, height, speed):
        self.height = height
        self.speed = speed
