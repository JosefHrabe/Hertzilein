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
### netPacker.py
- run as cronjob or manually
- runs through available data  and packs them into own directory
### netStripper.py
- run as cronjob or manually
- runs through packed data strips em into own directory
- by default all period data within one second are stripped down into a complex sample
 which includes timestamp, minimum, maximum and average data
### netPlot.py
- plots frequency trace over last 24 hours, scrolling and scaling if possible afterwards

### netBase.py
- common used functions for e.g. loading|saving or filtering

## netFFT
- deprecated
- sampler based on analog data - use AnalogSampler.ino


# Directories
## your repo 
storage path of your repository
### python
python files
### ino  
arduino files
### data
ignored, stores data of FFT logger, deprecated
### logs
ignored, hold logfiles for e.g. exceptions
### plots
ignored, default storage for plot files
### slope
ignored stores slope data
#### data
unpacked original captured data
#### packed
packed data
#### stripped
stripped data



