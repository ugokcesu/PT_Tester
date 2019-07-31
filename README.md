# PT_Tester
A python program with a pyqt interface for reading pressure and temperature data from arduino and
plotting it on a graph and table as well as storing the data in a csv file.

# Running the Code
Check out <a href="https://youtu.be/VpyWUxri6Gs"> this youtube video </a> for a short demo, then follow 
the <b>Installation Notes</b>.

# Installation Notes 
## For Python
See requirements.txt for a full list of modules and corresponding versions. The Anaconda environment makes the list bloated,
mainly, the libraries used are <b>pyfirmata</b> for connecting to the Arduino, <b>PyQt5</b> for the graphical interface and <b>matplotlib</b> for plotting the graph.

To install all packages run <code>pip install -r requirements.txt</code>

## For Arduino
From the Arduino utility go to <b>File > Examples > Firmata > StandardFirmata</b> and upload it onto your Arduino.
Disconnect and connect your Arduino.
The Arduino is now ready to send receive data through pyfirmata python module

## Finally:
run <b>main.py</b>

# Screenshots
<img src="Screen Shot 1.png"> </img>
