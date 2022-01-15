# Hertzilein 50Hz power frequency logger

- analog sampler with Arduino UNO
- logger with python on raspberry pi
- plotter with display of critical areas of net frequency,
based on european criterias

# Setup
- connect Arduino Uno with raspberry pi or PC via USB
- on windows  check for real COM port to which the Arduino is connected
- on raspberry pi 
 - goto console
 - type   ls /dev/tty* 
 - plug in Arduino
 - type   ls /dev/tty*  again an check new device - this is the port to be used
 
## Arduino UNO
- use blank Arduino Uno or maybe other device
- use about 10cm wire antenna  on pin A0
- place Adruino on a good spot - next to a power line at home
- sampler is setup up to expect a sine shaped wave over whole 10bit ADC range ( 0-1023 )
- sampler uses high hysteresis to detect slopes an d prevent unwanted transitions
- LED shows indication if the slope detection works


## SlopeSampler
### netSlope.py
- receives period data from Arduino and puts them into buffer
- saving data occures every 2 minutes
- every day gets new directory, every hour gets new file - to prevent amount of possible lost data

### netScope.py
- Sampler with Rohde&Schwarz RTC1002
- Sampling ans storage same as Slope Sampler
- using line trigger and trigger counter
- communication via VISA, SCPI port and TCPIP

### netPlot.py
- plots frequency trace over last 24 hours, scrolling and scaling if possible afterwards
- plots both samplers, slope and scope

### netBase.py
- common used functions for e.g. loading|saving or filtering



