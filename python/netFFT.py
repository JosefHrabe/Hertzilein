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

class Sampler:
    """
    Handles the communication between python and arduino
    AttachTo: ""
    """

    def __init__(self, port, maxSample=4):
        self.valid=False
        print('Init Sampler : ... ' , end='\r')
        try:
            self.board = Arduino(port)
        except Exception as __e:
            print(__e)
            nb.logException( __e , 'Sampler')
            return


        it = util.Iterator(self.board)
        it.start()
        self.board.add_cmd_handler(pyfirmata.pyfirmata.STRING_DATA, self._messageHandler)
        self.maxSample=maxSample
        self.data=[]
        self.valid=True
        print('Init Sampler : Done ' )

    def _messageHandler(self, *args, **kwargs):

        sample=int(util.two_byte_iter_to_str(args))
        if len( self.data ) >=self.maxSample:
            self.data.pop(0)

        self.data.append( sample )


def signal_handler(sig, frame):
    global runState
    print('Abort received')
    runState = False
    dumper.stop()

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

def _calcStd( data ):

    __min = min(data)
    __max = max(data)
    __avg = sum(data)/len(data)

    sq_sum=0
    for d in data:
        sq_sum += d*d

    sq_sum /= len(data)
    __rms = sqrt(sq_sum)

    return __min, __max , __avg, __rms

def strRemain( t=0 , unit=True ):
    t = int(t)
    _m = t/60
    m = int( _m)
    s = t-(m*60)
    log = '{0:02}'.format(m) + ':{0:02}'.format(s)
    if unit : log += 'min'
    return log

class Dumper:
    def __init__(self , interval=2*60):
        self.__last_file=''
        self.__interval = interval
        self.run=False
        self.__remain = 0

        self.makePathName()
        pass

    def stop(self):
        if self.run:
            print('Save Backup')
            self.__saveData()
        self.run=False

    def getRemain(self):

        return self.__remain

    def makePathName(self):
        stamp = nb.getStamp()
        fldr = stamp.split(' ')[0]
        fn = nb.getStamp(hourOnly=True)
        path = nb.logDataPath + fldr + '/' + fn + '.txt'
        self.__last_file = path


    def saveTask(self):
        self.run=True
        while True:
            self.__remain=self.__interval
            while self.__remain > 0:
                if not self.run : return

                self.__remain-=1
                time.sleep(1)

            self.makePathName()

            self.__saveData()

            print('save samples : {0}'.format(len(sampleData)))
            sampleData.clear()

        pass

    def __saveData(self):
        if self.__last_file=='': return


        resData = nb.loadDict( self.__last_file )

        if resData is None:
            print('newList')
            resData=[]

        for s in sampleData:
            resData.append( s )

        nb.saveDict( self.__last_file , resData )


iPolFactor_t=20
iPolFactor_f=20
dtSampler=2600e-6
dt = dtSampler/iPolFactor_t
timeSamples = 2048#int(1/dt)*10

dumpFile = nb.logDataPath + nb.getStamp(precise=True) + '.txt'
runState=True
dbgLog=False
logRaw=False
showBanner=False
logMeas=False
fLogDeviation=0.3
until = ''
bugs=[]
sampleData=[]
minData=[]
maxData=[]
avgData=[]
rmsData=[]
rawData={}
cfg_logSamples=30
cfg_interval=1.0
bootTime=time.time()
dumper=None
defaultPort=nb.port

def mainFunc():
    global bootTime

    print('Start Logger')
    saves=0
    sampler=Sampler( defaultPort, timeSamples)

    if not sampler.valid:
        if dumper is not None:
            dumper.stop()

        sys.exit(-1)

    __wait(5 , prefix='Wait for Sampler')
    sampler.data=[]


    print('Fill Buffer')
    while len(sampler.data) < (timeSamples - 1):
        time.sleep(1)

    nb.clearConsole()
    printArgs()

    bootTime= int( time.time() - bootTime )

    for xx in range(cfg_logSamples):


        if showBanner:
            nb.clearConsole()
            printArgs()

        start=time.time()
        data = nb.iPolSpline(sampler.data, factor=iPolFactor_t)

        if nb.isWindows:
            FFT = sy.fft.fft( data )
        else:
            FFT = sy.fft( data )



        freqs = syfp.fftfreq( len( data), d=dt )
        FFT=FFT.tolist()
        freqs=freqs.tolist()

        indexMin , indexMax=0,0
        for i,s in enumerate(freqs):
            if s > 45 and indexMin==0: indexMin=i
            if s > 55 and indexMax==0:
                indexMax=i
                break

        FFT_subset=FFT[ indexMin:indexMax ]
        freqs=freqs[ indexMin:indexMax ]

        absFFT=[]
        for i,cn in enumerate(FFT_subset):
            absFFT.append( abs(cn.real))



        # plt.plot(   absFFT , marker='.' , linestyle='-' , color='#ff600040')
        absFFT = nb.iPolSpline(absFFT, iPolFactor_f)
        freqs=nb.iPolLinear( freqs , iPolFactor_f )

        ampl=-99999
        f=0
        for ii , _a in enumerate( absFFT ):
            if ampl < _a:
                ampl=_a
                f=freqs[ii]



        # plt.plot(   freqs , absFFT , marker='.' , linestyle='-' , color='#008ff540')
        # plt.show()


        if showBanner:
            print( '{0:>8}|{2:<8}  {3:<5}     f: {1:.3f}'.format(xx+1, f, cfg_logSamples, saves) )
            print()
            print()
            nb.banner( '{0:.3f}'.format(f) )
        else:
            print( '{0:>8}|{2:<8}  {3:<5}     f: {1:.3f}'.format(xx+1, f, cfg_logSamples, saves), end='\r')


        thisStamp = nb.getStamp(precise=True , addMilliseconds=True)

        thisSample = {
            't' :thisStamp,
            'f' : f
        }

        __min,__max,__avg,__rms=_calcStd(data)

        if logMeas:
            thisSample['min'] = __min
            thisSample['max'] = __max
            thisSample['avg'] = __avg
            thisSample['rms'] = __rms

        if __min==0 or __max==1023 or dbgLog:
            try:
                plt.plot(   data , marker='.' , linestyle='-' , color='#ff6000')
                plt.xlim((200,800))
                plt.savefig( nb.debugPath + 't_' + thisStamp +'.png')
                plt.clf()
                plt.cla()
            except Exception as __e:
                nb.logException( __e , 'plot dbg t')
                pass

        testLog=False
        # if random.randint(0,100)%10==0:
        #     testLog=True

        if  f < (f-fLogDeviation) or f > (f+fLogDeviation)  or dbgLog   or testLog :
            try:
                bugs.append(f)
                plt.plot(   freqs , absFFT , marker='.' , linestyle='-' )
                plt.savefig( nb.debugPath + 'f_' + thisStamp +'.png')
                plt.clf()
                plt.cla()

                plt.plot(   data , marker='.' , linestyle='-' , color='#ff6000')
                plt.xlim((200,800))
                plt.savefig( nb.debugPath + 't_' + thisStamp +'.png')
                plt.clf()
                plt.cla()

            except Exception as __e:
                nb.logException( __e , 'plot dbg f')
                pass

        if logRaw:
            cpy=[]
            for _d in data:
                cpy.append(_d)

            rawData[thisStamp]=cpy
            del cpy

        sampleData.append( thisSample )

        duration = time.time()-start
        diff = cfg_interval-duration

        if diff>0.0:
            if not runState :
                return

            time.sleep( diff )

    print()
    pass


def printArgs():

    print()
    print('-----------------------------------------------------------')
    print()
    print('\nConfiguration')
    print()
    print( '  {0:<20}{1}'.format( 'Until' , until ))
    print( '  {0:<20}{1}'.format( 'f samples' , cfg_logSamples ))
    print( '  {0:<20}{1}'.format( 'interval'  , cfg_interval ))
    print( '  {0:<20}{1}'.format( 'time samples'  , timeSamples ))
    # print( '  {0:<20}{1}'.format( 'iPol t'  , iPolFactor_t ))
    # print( '  {0:<20}{1}'.format( 'iPol f'  , iPolFactor_f ))
    # print( '  {0:<20}{1}'.format( 'fLogDeviation'  , fLogDeviation ))

    # print( '  {0:<20}{1}'.format( 'log basic meas'  , logMeas ))
    # print( '  {0:<20}{1}'.format( 'log diagrams'  , dbgLog ))
    # print( '  {0:<20}{1}'.format( 'log raw data'  , logRaw ))
    # print( '  {0:<20}{1}'.format( 'outFile'  , dumpFile ))
    # print( '  {0:<20}{1}'.format( 'show banner'  , showBanner ))
    # print( '  {0:<20}{1}'.format( 'bugs'  , bugs ))
    print( '  {0:<20}{1}'.format( 'boot time'  , bootTime ))

    if dumper is not None:
        print( '  {0:<20}{1}'.format( 'Saving in '  , strRemain( dumper.getRemain() ) ))

    print()
    print('-----------------------------------------------------------')
    print()



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-samples'    , type=float, default=10    , required=False  ,
                        help='{0}Sa, samples to be taken'.format( 10 ))
    parser.add_argument('-until'    , type=str, default=''    , required=False  ,
                        help='date &| time yyyy-mm-dd hh-mm')
    parser.add_argument('-interval'   , type=float, default=1.0    , required=False  ,
                        help='{0}s, interval between samples'.format( 1.0 ))
    parser.add_argument('-t_size'    , type=int, default=385    , required=False  ,
                        help='{0}Sa, size of time samples ring buffer 1sec=385Sample '.format( 2048 ))
    parser.add_argument('-iPol_t'  , type=int, default=20      , required=False ,
                        help='{0}, Factor for interpolating time data'.format(20))
    parser.add_argument('-iPol_f'  , type=int, default=20      , required=False ,
                        help='{0}, Factor for interpolating frequency data'.format(20))

    parser.add_argument('-fLogDeviation'  , type=float, default=0.2      , required=False ,
                        help='{0}Hz, deviation for exceeding f range, auto logging diagrams'.format(0.3))

    parser.add_argument('-banner'  , dest='banner', required=False , action='store_true',
                        help='shows banner with recent value')
    parser.set_defaults(banner=False)

    parser.add_argument('-dbgLog'  , dest='dbgLog', required=False , action='store_true',
                        help='log diagram for f and t data for each logger sample')
    parser.set_defaults(feature=False)

    parser.add_argument('-logRaw'  , dest='logRaw', required=False , action='store_true',
                        help='log raw time data - might result in high memory usage')
    parser.set_defaults(logRaw=False)

    parser.add_argument('-logMeas'  , dest='logMeas', required=False , action='store_true',
                        help='logs measurements min, max , mean , rms')
    parser.set_defaults(logMeas=False)


    parser.add_argument('-port'    , type=str, default=''    , required=False  ,
                        help='com port as long as defatls dont fit\n'+
                             'raspi={0}\n'.format( nb.default_port_raspi)+
                             'pc={0}\n'.format( nb.default_port_pc)
                        )


    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    try:
        cfg_logSamples= int(args.samples)
        cfg_interval = args.interval

        if args.until == '' :
            offset = int(cfg_logSamples/cfg_interval)
            until = 't(Sa) ~ {0}'.format(nb.getStamp( precise=True ))

        timeSamples = args.t_size
        iPolFactor_t = args.iPol_t
        iPolFactor_f = args.iPol_f
        dbgLog = args.dbgLog
        logRaw = args.logRaw
        showBanner = args.banner
        logMeas = args.logMeas
        fLogDeviation = args.fLogDeviation

        if args.port != '':
            defaultPort = args.port

        if args.until != '':
            until = args.until
            secs = nb.calcSamples( args.until )
            cfg_logSamples = int( secs / cfg_interval )

    except Exception as __e:
        nb.logException( __e , 'parse args')
        sys.exit(1)


    signal.signal(signal.SIGINT, signal_handler)
    dumper = Dumper()
    threading.Thread(target=dumper.saveTask).start()

    nb.clearConsole()
    printArgs()

    try:
        mainFunc()
    except Exception as __e:
        nb.logException( __e , 'Crash' )

    dumper.stop()
    sys.exit(0)
