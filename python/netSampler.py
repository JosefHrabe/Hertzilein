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

runState=True

class Sampler:

    def __init__(self, port , maxData):
        self.valid=False
        self.maxData=maxData
        self.logTime=time.time()
        print('Init Sampler : ... ' , end='\r')
        try:
            self.board = Arduino(port)
            self.__logTime( 'BoardInit')
        except Exception as e:
            nb.logException(e , 'Failed to init Sampler port:{0}'.format(port))
            # print(e)
            return


        it = util.Iterator(self.board)
        it.start()
        self.board.add_cmd_handler(pyfirmata.pyfirmata.STRING_DATA, self._messageHandler)
        self.valid=True
        self.logging=True
        self.xData=[]
        self.yData=[]
        self.lastX=0
        self.ignoreCount=4
        self.xSum=0
        self.packet=0
        self.samples=0

    def __logTime(self , topic=''):
        print('{0:<15}{1:.3f}s'.format(topic , time.time()-self.logTime))

    def _messageHandler(self, *args, **kwargs):

        if not self.logging : return
        #sample=int(util.two_byte_iter_to_str(args))
        r = util.two_byte_iter_to_str(args)
        # print(r)

        if '---' in r:
            self.packet+=1
            self.samples=0
            return

        if 'end' in r:
            self.logging=False
            print()
            return

        self.samples+=1
        dump = r.split(';')
        self.xSum += int(dump[1])

        self.xData.append(self.xSum)
        self.yData.append(int(dump[0]))

        print( 'Packet: {0:>5} :: {1:<5}'.format(self.packet , self.samples) , end='\r')



def mainFunc(port=''):

    nb.clearConsole()

    if port == '':
        if nb.isWindows:
            port = 'COM3'
        else:
            port = '/dev/ttyACM1'

    sampler = Sampler( port , 1000 )
    if not sampler.valid:
        return

    while sampler.logging:
        # nb.clearConsole()
        # print( 'Packet: {0:>5} :: {1}'.format(sampler.packet , sampler.samples))
        time.sleep(1)
        pass


    nb.saveDict( nb.packetTrace , {   'x_us':sampler.xData, 'adc':sampler.yData    })
    plt.plot( sampler.xData , sampler.yData , marker='.')
    plt.show()



if __name__ == '__main__':


    mainFunc( )