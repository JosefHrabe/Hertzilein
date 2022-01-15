import os
import time
import matplotlib.pylab as plt
import argparse
from pyfirmata import Arduino, util
import pyfirmata
import netBase as nb
import threading
import signal
import matplotlib.pyplot as plt
from copy import deepcopy

import pyvisa as vs
from netBaseSampler import BaseSampler


runState=True

class ScopeSampler(BaseSampler):

    def __init__(self , ip , logPath, interval=1.0):
        super( ScopeSampler , self).__init__( logPath=logPath )

        self.__ip=ip
        self.__interval=interval
        self.__rm = vs.ResourceManager()
        print( self.__rm.list_resources())
        try:
            self.dut = self.__rm.open_resource('TCPIP::192.168.2.107::INSTR')
        except:
            self.dut=None
            self.valid=False
        self.dut.timeout = 10000
        self.dut.clear()
        self.runState=True
        self.__recentFreq=0.0
        self.__ID='Undefined'
        self.__init()
        #threading.Thread(target=self.saveTask).start()
        threading.Thread(target=self.__logTask).start()


    def __init(self):
        if self.dut is not None:
            idnStr=self.dut.query('*IDN?')
            idnDump=idnStr.split(',')
            self.__ID = '{0},{1}'.format(idnDump[0] , idnDump[1])

            print(idnStr)
            print(self.dut.query('*RST;*OPC?'))
            print(self.dut.query('tco:enab 1;ENAB?'))
            print(self.dut.query('trig:a:sour line;sour?'))

    def stop(self):
        self.runState = False
        super(ScopeSampler, self).stop()
        print('CloseDut')

        self.dut.clear()
        self.dut.close()

    def getRecentFreq(self):
        return self.__recentFreq

    def getID(self):
        return self.__ID

    def __logTask(self):

        while self.runState==True:
            start = time.time()
            res=self.dut.query('tco:res:FREQ?')
            res=float(res.strip())

            self.__recentFreq=res
            # print(res)
            while self.saveOperationRunning:
                print('wait for saving')
                time.sleep(0.1)

            self.data.append(   {
                't':nb.getStamp(precise=True , addMilliseconds=True),
                'f':res
                }
            )

            duration=time.time()-start
            wait = self.__interval-duration

            if wait>0:
                time.sleep( wait )







def signal_handler(sig, frame):
    global runState
    print('Abort received')
    runState = False



def mainFunc(ip=''):

    global runState

    signal.signal(signal.SIGINT, signal_handler)

    if ip =='':
        ip = '192.168.2.107'

    ss=ScopeSampler( ip , nb.scopeDataPath )

    while runState and ss.valid:
        nb.clearConsole()

        print()
        print('Scope Sampler')
        print('{0:<10}:{1}'.format('Scope' , ss.getID()))
        print('{0:<10}:{1}'.format('Save' , ss.getRemain()))
        print()
        nb.banner( '{0:.3f}'.format(ss.getRecentFreq()) )
        time.sleep(1)

    if ss.valid:
        print('Stop Sampler')
        ss.stop()


    print('Fertsch')






if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    # parser.add_argument('-plot'  , dest='plotFunc', required=False , action='store_true',
    #                     help='plot test samples')
    # parser.set_defaults(plotFunc=False)

    # parser.add_argument('-samples'    , type=float, default=10    , required=False  ,
    #                     help='{0}Sa, samples to be taken'.format( 10 ))
    # parser.add_argument('-until'    , type=str, default=''    , required=False  ,
    #                     help='date &| time yyyy-mm-dd hh-mm')

    parser.add_argument('-port'    , type=str, default=''    , required=False  ,
                        help='port')
    args = parser.parse_args()

    mainFunc( ip='' )