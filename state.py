import enum


class State (enum.Enum):
    ReadyNotRan = 1
    InProgress = 2
    Completed = 3
    Disconnected = 4
    Aborted = 5
    CannotConnect = 6


class StateMessages:
    messages = dict()
    messages[State.ReadyNotRan] = "Ready"
    messages[State.InProgress] = "Test in progress..."
    messages[State.Completed] = "Test Completed"
    messages[State.Disconnected] = "Connection to device lost"
    messages[State.Aborted] = "Test Aborted"
    messages[State.CannotConnect] = "Cannot connect to device"


class StateStyles:
    styles = dict()
    styles[State.ReadyNotRan] = "QLabel { background-color :darkgreen; color : white; border:2px solid rgb(0,0,0);}"
    styles[State.InProgress] = "QLabel { background-color : green; color : white; border:2px solid rgb(0,0,0);}"
    styles[State.Completed] = "QLabel { background-color :darkgreen; color : white; border:2px solid rgb(0,0,0);}"
    styles[State.Disconnected] = "QLabel { background-color : red; color : black; border:2px solid rgb(0,0,0);}"
    styles[State.Aborted] = "QLabel { background-color : red; color : black; border:2px solid rgb(0,0,0);}"
    styles[State.CannotConnect] = "QLabel { background-color : red; color : black; border:2px solid rgb(0,0,0);}"
