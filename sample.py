import enum


class SampleTypes(enum.Enum):
    Time = 1
    Pressure = 2
    Temperature = 3


class SampleNames:
    names = dict()
    names[SampleTypes.Time] = "Time"
    names[SampleTypes.Pressure] = "Pressure (psi)"
    names[SampleTypes.Temperature] = "Temperature (F)"


class Sample:
    NDV = -99999

    def __init__(self, p, t):
        self.values = dict()
        self.values[SampleTypes.Pressure] = p
        self.values[SampleTypes.Temperature] = t

