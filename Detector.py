from typing import Dict, List
import numpy as np
import pprint as pp
import math


class Detector:
    def __init__(self, rangeStart, rangeEnd, numberOfSensors, timeGranularity) -> None:
        self.__eventStorage: List(Event) = []
        self.__rangeStart: float = rangeStart
        self.__rangeEnd: float = rangeEnd
        self.__rangeSize: float = rangeEnd - rangeStart
        self.numberOfSensors: int = numberOfSensors
        self.__bucketSize: float = self.__rangeSize / numberOfSensors
        self.timeGranularity: float = timeGranularity
        self.__largestTime: float = -math.inf
        self.__smallestTime: float = math.inf
        self.__buckets: List(List(int)) = list([]
                                               for _ in range(numberOfSensors))

    def __bucketIndexForValue(self, value: float) -> int:
        if not (self.__rangeStart <= value <= self.__rangeEnd):
            return -1
        return int((value - self.__rangeStart) / self.__bucketSize)

    def event(self, value: float, timestamp: float) -> None:
        self.__eventStorage.append(Event(timestamp, value))

    def processData(self, reductionVelocity: float = 0) -> None:
        for bucket in self.__buckets:
            bucket.clear()
        self.__largestTime: float = -math.inf
        self.__smallestTime: float = math.inf

        for event in self.__eventStorage:
            bucketIndex = self.__bucketIndexForValue(event.value)
            if bucketIndex == -1:
                continue

            reducedTimestamp = event.timestamp
            if reductionVelocity != 0:
                reducedTimestamp -= event.value/reductionVelocity
            # FIXME: this only rounds down
            alignedTimestamp = reducedTimestamp - reducedTimestamp % self.timeGranularity
            if alignedTimestamp < self.__smallestTime:
                self.__smallestTime = alignedTimestamp
            if alignedTimestamp > self.__largestTime:
                self.__largestTime = alignedTimestamp
            self.__buckets[bucketIndex].append(alignedTimestamp)

    def data(self) -> np.ndarray:
        numberOfTimesteps = int((self.__largestTime -
                                 self.__smallestTime) / self.timeGranularity + 1)
        data = np.zeros((self.numberOfSensors, numberOfTimesteps))

        for bucketIndex, bucket in enumerate(self.__buckets):
            for eventTimestamp in bucket:
                data[bucketIndex][int((eventTimestamp - self.__smallestTime) /
                                  self.timeGranularity)] += 1
        return data

    # Returns the extend of the data
    def extend(self) -> Dict:
        return {'rangeStart': self.__rangeStart, 'rangeEnd': self.__rangeEnd, 'smallestTime': self.__smallestTime, 'largestTime': self.__largestTime}

    def dump(self) -> None:
        pp.pp(self.__buckets)


class Event:
    def __init__(self, timestamp: float, value: float) -> None:
        self.timestamp = timestamp
        self.value = value
