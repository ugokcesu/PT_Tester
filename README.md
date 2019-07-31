# PT_Tester
A python program with a pyqt interface for reading pressure and temperature data from arduino and
plotting it on a graph and table.

# Running the Code
Check out <a href="https://www.youtube.com/watch?v=2KEuVRwzcRc"> this youtube video </a> for a short demo, then follow 
the <b>Installation Notes</b>.

# Installation Notes 
## For Python
See requirements.txt for a full list of modules and corresponding versions. The Anaconda environment makes the list bloated,
the 2 libraries used are pyfirmata for connecting to the Arduino and PyQt5 for the graphical interface.

To install all packages run <b>pip install -r requirements.txt</b>

## For Arduino
From the Arduino utility go to <b>File > Examples > Firmata > StandardFirmata</b> and upload it onto your Arduino.
Disconnect and connect your Arduino.
The Arduino is now ready to send receive data through pyfirmata python module

## Finally:
run <b>main.py</b>

# Screenshots
