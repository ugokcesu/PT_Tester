import enum


class SampleTypes(enum.Enum):
    Time = 1
    Pressure = 2
    Temperature = 3


class SampleNames:
    names = dict()
    names[SampleTypes.Time] = "Time"
    names[SampleTypes.Pressure] = "Pressure"
    names[SampleTypes.Temperature] = "Temperature"


class Sample:
    def __init__(self, sample_type, value):
        self.type = sample_type
        self.value = value
