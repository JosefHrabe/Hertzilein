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

runState=True

class Sampler:

    def __init__(self, port, maxSample=4):
        self.valid=False
        self.logTime=time.time()
        print('Init Sampler : ... ' , end='\r')
        try:
            self.board = Arduino(port)
            self.__logTime( 'BoardInit')
        except Exception as e:
            print(e)
            return


        it = util.Iterator(self.board)
        it.start()
        self.board.add_cmd_handler(pyfirmata.pyfirmata.STRING_DATA, self._messageHandler)
        self.maxSample=maxSample
        self.data=[]
        self.firstSample=False
        self.lastFreq=0
        self.yMin=0
        self.yMax=0
        self.__logTime( 'InitDone')
        self.__last_file=''
        self.__interval = 2*60
        self.run=False
        self.__remain = 0
        self.makePathName()
        self.runSave=False
        self.saveOp=False

        threading.Thread(target=self.saveTask).start()
        self.valid=True

    def __logTime(self , topic=''):
        print('{0:<15}{1:.3f}s'.format(topic , time.time()-self.logTime))

    def _messageHandler(self, *args, **kwargs):

        if not self.firstSample:
            self.__logTime( 'FirstSample')
            self.firstSample=True

        #sample=int(util.two_byte_iter_to_str(args))
        r = util.two_byte_iter_to_str(args)

        # print(r)
        if 'y' in r:    self.yMin = int(r.replace('y',''))
        if 'Y' in r:    self.yMax = int(r.replace('Y',''))


        if 'x' in r:
            T = float(r.replace('x',''))/1000000.0
            f=1/T
            t = nb.getStamp(precise=True , addMilliseconds=True)
            self.lastFreq=f

            # while self.saveOp:
            #     time.sleep(0.1)

            self.data.append(
                {
                    'f' : f,
                    't' : t
                }
            )

    def stop(self):
        if self.runSave:
            print('Save Backup')
            self.__saveData()
        self.runSave=False

    def getRemain(self):
        return self.__remain

    def makePathName(self):
        stamp = nb.getStamp()
        fldr = stamp.split(' ')[0]
        fn = nb.getStamp(hourOnly=True)
        path = nb.slopeDataPath + fldr + '/' + fn + '.txt'
        self.__last_file = path

    def saveTask(self):
        self.runSave=True
        while True:
            self.__remain=self.__interval
            while self.__remain > 0:
                if not self.runSave : return

                self.__remain-=1
                time.sleep(1)

            self.makePathName()

            self.saveOp=True
            # self.logTime=time.time()
            self.__saveData()
            print('save samples : {0}'.format(len( self.data )))
            # self.__logTime('save file')
            self.saveOp=False

        pass

    def __saveData(self):
        if self.__last_file=='': return

        resData = nb.loadDict( self.__last_file )

        if resData is None:
            print('newList')
            resData=[]

        self.logTime=time.time()
        dc = deepcopy( self.data)
        self.__logTime('dc')
        self.data.clear()

        for s in dc:
            resData.append( s )

        nb.saveDict( self.__last_file , resData )





def signal_handler(sig, frame):
    global runState
    print('Abort received')
    runState = False
    # dumper.stop()

def __wait(t , prefix='Wait'):
    """
    Sleeps with console response
    :param t: time
    :return:
    """
    while t > 0:
        time.sleep(1)
        t-=1
        if prefix != '':
            print('{1} : {0}'.format(t , prefix) , end='\r')

    if prefix != '':
        print()



def mainFunc():

    signal.signal(signal.SIGINT, signal_handler)
    nb.clearConsole()
    port=''
    if nb.isWindows:
        port = 'COM5'
    else:
        port = '/dev/ttyACM1'

    s = Sampler( port , maxSample=1000)
    # plt.ion()
    loops=1
    while runState:
        loops+=1

        if s.firstSample:
            nb.clearConsole()
            print('\n\nSlope Sample')
            print('\n')
            print('  {0:<10}{1}'.format('port' , port))
            print('  {0:<10}{1}'.format('yMin' , s.yMin))
            print('  {0:<10}{1}'.format('yMax' , s.yMax))
            print('  {0:<10}{1}'.format('Save in' , s.getRemain()))
            print('\n')
            nb.banner( '{0:.3f}'.format(s.lastFreq))
            # print( '{0:.2f}'.format(s.lastFreq ))
        # if loops%120==0:
        #     print('save')
        #     nb.saveDict( nb.slopePath+'test.txt' , s.data )
        time.sleep(1)
        pass

    s.stop()




def plot():

    dList = os.listdir( nb.slopeDataPath )
    infiles=[]
    for d in dList:
        _dir = nb.slopeDataPath + d + '/'
        fList = os.listdir( _dir )

        for f in fList:
            fn = _dir+f
            infiles.append(fn)

    infiles.sort()

    while len(infiles) > 5:
        infiles.pop(0)

    f,t=[],[]
    dataSum=[]
    for fn in infiles:
        data=None
        try:
            retry=30
            while retry:
                data = nb.loadDict( fn )
                if data is not None:
                    retry=0
                else:
                    print('retry read data')
                    retry -= 1
                    time.sleep(1)
        except:pass

        if data is not None:
            for i,sample in enumerate(data):
                # if i > 1000: break
                print( 'collect : {0:.3f}%'.format( 100*((i+1)/len(data))) , end='\r')
                # f.append( sample['f'])
                # t.append( nb.getDateObject(sample['t']))
                dataSum.append( sample )
            print()

    flt = nb.Filter()

    resData = flt.calcArithmetics(dataSum)

    # fsmooth = flt.smooth( f , k=20)
    # plt.plot( t , f , marker='.' , label='original' , color = '#000000' , alpha=0.1)
    # plt.plot( t , fsmooth , marker='.' , label='smoothed 1s' , color='#008ff5' , alpha=0.2)

    # plt.plot( resData['t'] , resData['min'] , marker=',' , label='min' , color='#800000' )
    # plt.plot( resData['t'] , resData['max'] , marker=',' , label='max' , color='#800000' )
    plt.plot( resData['t'] , resData['avg'] , marker=',' , label='avg' , color='#a04000' )

    plt.ylim((48,52))
    plt.legend()
    plt.show()
    pass

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-plot'  , dest='plotFunc', required=False , action='store_true',
                        help='plot test samples')
    parser.set_defaults(plotFunc=False)

    # parser.add_argument('-samples'    , type=float, default=10    , required=False  ,
    #                     help='{0}Sa, samples to be taken'.format( 10 ))
    # parser.add_argument('-until'    , type=str, default=''    , required=False  ,
    #                     help='date &| time yyyy-mm-dd hh-mm')
    # parser.add_argument('-port'    , type=str, default=''    , required=False  ,
    #                     help='port')

    args = parser.parse_args()

    if args.plotFunc:
        plot()
    else:
        mainFunc()