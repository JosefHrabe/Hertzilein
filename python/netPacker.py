#from events.EventDispatcherClass import Event
#import datetime
import dataclasses
import multiprocessing
import os
import random
import time, sys
import matplotlib.pylab as plt
import argparse

from pyfirmata import Arduino, util
import pyfirmata
import netBase as nb
import scipy as sy
import scipy.fftpack as syfp
from math import sqrt
import threading
import signal
import matplotlib.pyplot as plt
import sys, psutil
from copy import deepcopy



def pack():

    dList = os.listdir( nb.slopeDataPath )
    infiles=[]
    for d in dList:
        _dir = nb.slopeDataPath + d + '/'
        fList = os.listdir( _dir )

        for f in fList:
            fn = _dir+f
            infiles.append(fn)

    infiles.sort()
    infiles.pop( len(infiles)-1)

    for fn in infiles:

        nb.packFile( fn )



if __name__ == '__main__':

    pack()