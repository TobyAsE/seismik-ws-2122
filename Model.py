import numpy as np


class Model:

    def __init__(self) -> None:
        self.__layers = []

    def numberOfLayers(self) -> int:
        return len(self.__layers)

    def addLayer(self, height: float, speed: float) -> None:
        self.__layers.append(Layer(height, speed))

    def layer(self, index: int) -> 'Layer':
        if not (0 <= index < self.numberOfLayers()):
            return None
        return self.__layers[index]

    def criticalAngleOfBoundary(self, bottomLayer: int) -> float:
        if bottomLayer > self.numberOfLayers() - 1:
            return -1
        return np.arcsin(self.layer(bottomLayer - 1).speed / self.layer(bottomLayer).speed)


class Layer:
    def __init__(self, height, speed):
        self.height = height
        self.speed = speed
