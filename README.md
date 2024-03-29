# PT_Tester
A python program with a pyqt interface for reading pressure and temperature data from arduino and
plotting it on a graph and table as well as storing the data in a csv file. Check out <a href="https://youtu.be/STYHo8Lq0Qw"> this youtube video</a> for a short demo

<b> Features</b>
<ul> 
  <li>The plot, table, and the csv file are interactively filled as each sample is recorded.</li>
<li>The arduino connection is done in a seperate thread so that the GUI remains active for manipulating the plot and table.</li>
  <li>While taking recordings, the software can detect whether the arduino was disconnected or if the stop button was pressed, and terminates the second thread gracefully.</li>

# Screenshots
<img src="Screen Shot 1.png"> </img>

# Running the Code / Installation Notes 
## For Python
See requirements.txt for a full list of modules and corresponding versions. Mainly, the libraries used are <b>pyfirmata</b> for connecting to the Arduino, <b>PyQt5</b> for the graphical interface and <b>matplotlib</b> for plotting the graph.

## For Arduino
From the Arduino utility go to <b>File > Examples > Firmata > StandardFirmata</b> and upload it onto your Arduino.
Disconnect and connect your Arduino.
The Arduino is now ready to send receive data through pyfirmata python module

## Finally:
run <b>main.py</b>

