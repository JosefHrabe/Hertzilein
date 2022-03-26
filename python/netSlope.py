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
initTime = time.time()
bootTime = 0.0
exitTime = 0.0

class Sampler:

    def __init__(self, port ):
        self.valid=False
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
    global exitTime
    exitTime=time.time()
    print('Abort received')
    runState = False

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



def mainFunc(port=''):

    global bootTime
    global runState

    signal.signal(signal.SIGINT, signal_handler)
    nb.clearConsole()
    jobMode=False
    runTime = (60.0*60.0 -( 8 + 5 +5))
    duration =0
    time_start = time.time()
    if port == '':
        if nb.isWindows:
            port = 'COM5'
        else:
            port = '/dev/ttyACM0'

    sampler = Sampler( port )
    if not sampler.valid:
        return

    loops=1
    while runState:

        loops+=1


        if sampler.firstSample and bootTime == 0.0:
            bootTime = time.time()-initTime

        if sampler.firstSample:
            nb.clearConsole()
            print('\n\nSlope Sample')
            print('\n')
            if not jobMode:
                print('  {0:<10}{1}'.format('port' , port))
                print('  {0:<10}{1}'.format('yMin' , sampler.yMin))
                print('  {0:<10}{1}'.format('yMax' , sampler.yMax))
                print('  {0:<10}{1}'.format('Save in' , sampler.getRemain()))
                print('  {0:<10}{1}'.format('boot' , '{0:.2f}s'.format(bootTime)))
            print('  {0:<10}{1}'.format('runTime' , '{0:.2f}s'.format( int(runTime))))
            print('  {0:<10}{1}'.format('duration' , '{0:.2f}s'.format( int(duration))))

            if not jobMode:
                print('\n')
                nb.banner( '{0:.3f}'.format(sampler.lastFreq))

        if jobMode:
            time.sleep(30)
        else:
            time.sleep(1)

        pass

        time_now = time.time()
        duration = time_now-time_start

        if jobMode and abs(duration)> runTime:
            runState = False

    sampler.stop()




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

    mainFunc( port=args.port )

    print('  {0:<10}{1}'.format('exit in' , '{0:.2f}s'.format( time.time()-exitTime )))
