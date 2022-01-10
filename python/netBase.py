import datetime,os
import platform
import json as js
import sys

import compress_json as cj
import subprocess
import time

import pyfiglet as pf
from scipy.interpolate import interp1d
import numpy as np

from math import sin, pi
import traceback

default_port_raspi = '/dev/ttyACM0'
default_port_pc    = 'COM3'
encode = 'utf-8'
rootPath  = os.getcwd().replace('\\','/').replace('python','')
logPath   = rootPath + 'logs/'
logDataPath   = rootPath + 'data/'
debugPath = logDataPath + 'debug/'
plotsPath = rootPath + 'plots/'
exceptionPath = logPath + 'exceptions/'
slopePath   = rootPath + 'slope/'
slopeDataPath   = slopePath + 'data/'
slopePackedPath   = slopePath + 'packed/'
slopeStrippedPath   = slopePath + 'stripped/'
compressFormats= [ 'gz' , 'bz' , 'lzma']

if 'Windows' in platform.system():
    isWindows = True
    port= default_port_pc
else:
    isWindows = False
    port= default_port_raspi

def calcSamples( d ):
    try:
        now  = datetime.datetime.now( )
        than = getDateObject( d )
        ofs=than-now
        secs= ofs.total_seconds()
        return int(secs+0.5)
    except Exception as e:
        logException( e , '')

    return 0


def getStamp( offset=0.0, dateOnly=False, precise=False , addMilliseconds=False , hourOnly=False):
    now=datetime.datetime.now( )
    ofs=datetime.timedelta(seconds=offset)
    t = now+ofs

    if dateOnly :
        return t.strftime("%Y-%m-%d")
    if addMilliseconds:
        return t.strftime("%Y-%m-%d %H-%M-%S.%f")
    if hourOnly:
        return t.strftime("%Y-%m-%d %H")
    if precise:
        return t.strftime("%Y-%m-%d %H-%M-%S")
    else:
        return t.strftime("%Y-%m-%d %H-%M")

def getDateObject( s ):

    if len(s) ==5:
        d = getStamp( dateOnly=True)
        s = d + ' ' + s

    for f in  [ "%Y-%m-%d %H-%M-%S.%f" ,
                "%Y-%m-%d %H-%M-%S" ,
                "%Y-%m-%d %H-%M"  ,
                "%Y-%m-%d"
                ]:
        try:
            do = datetime.datetime.strptime( s, f)
            return do
        except Exception as e:
            #logException( e , 'getDateObj')
            pass

    return None

def prepareFilePath( filename ):
    os.makedirs(os.path.dirname(filename), exist_ok=True)

def toCompressFileName(fn, compress):

    if compress in compressFormats:

        dump = fn.split('.')
        dest = '.'.join( dump[:-1])
        dest += '.'+compress

    return dest


def packFile( fn ):

    dest = toCompressFileName( fn , 'gz')
    dest = dest.replace( slopeDataPath , slopePackedPath )
    print('Pack : {0}'.format(fn))
    if not os.path.exists( dest ):
        data = loadDict(fn)
        prepareFilePath(dest)
        cj.dump( data , dest )


def saveDict( f , d , indent=1 , compress='' , override=True):
    __start=time.time()
    prepareFilePath(f)

    if compress != '':
        if compress not in compressFormats:
            print( 'Unsupported Compress format')
            return
        try:
            _fn = toCompressFileName( f , compress )
            exists =os.path.exists(_fn)
            if ( exists and override) or not exists:
                cj.dump( d, _fn )

        except Exception as e:
            pass
    else:
        exists =os.path.exists( f )
        if ( exists and override) or not exists:
            with open ( f , 'w' , encoding=encode) as outfile:
                outfile.write(js.dumps(d,indent=indent))

    print('save {0:<40} {2:<4}   in {1:.3f}s'.format(f , time.time()-__start , compress ) )

def loadDict( f ):
    __start=time.time()
    if not os.path.exists(f):
        return None

    try:
        ending = f.split('.')[-1]
        if ending in compressFormats:
            mydict = cj.load( f )
        else:
            with open(f, 'r' ,  encoding=encode ) as infile:
                mydict = js.loads(infile.read())
    except :
        return None

    # print('load {0:<40} in {1:.3f}s'.format(f , time.time()-__start) )
    return mydict

def clearConsole( restartLabel=''):
    if not isWindows:
        # check and make call for specific operating system
        try:
            _ = subprocess.call('clear' if os.name =='posix' else 'cls')
            if restartLabel != '':
                print(restartLabel)
        except Exception as e:
            try:    print(e)
            except: pass

def banner( s ):
    _s = pf.figlet_format( s , font='univers')
    dump= _s.split('\n')
    _d=[]
    for d in dump:
        if d.strip()!='':
            _d.append(d)

    _s = '\n'.join(_d)

    print( _s )



def iPolSpline(data_in, factor=10):
    size=len(data_in)
    x = np.linspace(0, size-1, num=size, endpoint=True)
    y = np.array(data_in)
    f2 = interp1d(x, y, kind='cubic')
    xnew = np.linspace(0, size-1, num=size*factor, endpoint=True)
    yNew=f2(xnew)
    yNew=yNew.tolist()

    return yNew

def iPolLinear(data_in, factor=10):
    size=len(data_in)
    x = np.linspace( data_in[0], data_in[-1], num=size*factor, endpoint=True)
    yNew=x.tolist()
    return yNew


class Filter:
    def __init__( self , fg=1,fs=1 , FIR_kMax=50):

        self.__fg=fg
        self.__fs=fs
        self.__fg_by_fs = self.__fg / self.__fs
        self.__FIR_kMax=FIR_kMax
        self.__FIRcoeff=[]
        self.__initFIRCoeff()


    def __initFIRCoeff(self):
        for k in range(self.__FIR_kMax):
            self.__FIRcoeff.append(self.__calcFIRCoeff(k))

    def __sinx(self, x):
        if x==0: return 1.0

        return sin(x)/x

    def __calcFIRCoeff(self, k):
        c = 2.0*self.__fg_by_fs * self.__sinx(k * 2.0 * pi * self.__fg_by_fs)
        # print( 'k:{0:<4}    c:{1:<.5f}'.format( k , c ))
        return c

    def setFrequency( self , fg=1,fs=1 , FIR_kMax=50):
        self.__fg=fg
        self.__fs=fs
        self.__fg_by_fs = self.__fg / self.__fs
        self.__initFIRCoeff()

    def FIR(self, indata, k=3):
        size=len(indata)
        outData=[]
        for i,v in enumerate(indata):
            vSum=0.0
            _kmax= min( [ abs(0-i) , abs(size-1-i) , k ])
            print( 'FIR k={1}: {0:.3f}%'.format( ((i+1)/len(indata))*100 , k ) , end='\r')

            for _k_ in range(_kmax):
                idx = _k_+1
                f= self.__FIRcoeff[ idx]
                # add prev. sample
                vSum += indata[ i - idx ] * f
                # add nex sample
                vSum += indata[ i + idx ] * f

            vSum += indata[i]*self.__FIRcoeff[0]
            outData.append(vSum)
        print()
        return outData

    def smooth(self, indata, k=3):
        start = time.time()
        size=len(indata)
        outData=[]
        for i,v in enumerate(indata):
            print('Smoothing: {0:.2f}%'.format( ((i+1)/len(indata))*100) , end='\r')
            vSum=0.0
            _kmax= min( [ abs(0-i) , abs(size-1-i) , k ])
            # print(_kmax)

            for _k_ in range(_kmax):
                idx = _k_+1
                # add prev. sample
                vSum += indata[ i - idx ]
                # add nex sample
                vSum += indata[ i + idx ]

            vSum += indata[i]
            vSum /= (_kmax*2+1)
            outData.append(vSum)

        print()
        print( 'Duration : {0}s'.format( int(time.time()-start)))
        return outData

    def smoothPast(self, indata, k=3):
        #size=len(indata)
        start = time.time()
        outData=[]
        tmpSum=[]
        for i,v in enumerate(indata):
            print('Smoothing: {0:.2f}%'.format( ((i+1)/len(indata))*100) , end='\r')
            if len(tmpSum) >= k:
                tmpSum.pop(0)
            tmpSum.append( indata[i] )

            outData.append( sum(tmpSum)/len(tmpSum))

        print()
        print( 'Duration : {0}s'.format( int(time.time()-start)))

        return outData

    def calcArithmetics( self , data , asTimeObject=True):

        currentSample={ 't':'','min':100,'max':0,'sum':0    }

        newData = []
        resData={'min':[],'max':[],'avg':[] , 't':[] }
        for i,sample in enumerate(data):
            print( 'sum     : {0:.3f}%'.format( 100*((i+1)/len(data))) , end='\r')

            current_f = sample['f']

            if 30 < current_f < 70:

                stamp = sample['t'].split('.')[0]
                if stamp != currentSample['t']:
                    if currentSample['t'] != '': #store previous sample
                        newData.append(currentSample)

                    currentSample={
                        't':stamp,
                        'min':current_f,
                        'max':current_f,
                        'sum':current_f,
                        'cnt':1
                    }
                else:
                    if currentSample['min']  > current_f:
                        currentSample['min'] = current_f
                    if currentSample['max']  < current_f:
                        currentSample['max'] = current_f

                    currentSample['sum'] += current_f
                    currentSample['cnt'] += 1
        print()

        if currentSample['t'] !='' :
            newData.append(currentSample)

        for i,s in enumerate(newData):

            print( 'strip   : {0:.3f}%'.format( 100*((i+1)/len(newData))) , end='\r')

            resData['min'].append( s['min'] )
            resData['max'].append( s['max'] )
            if asTimeObject:
                resData['t'].append( getDateObject( s['t']) )
            else:
                resData['t'].append(  s['t'] )

            if s['cnt']:
                avg = s['sum'] / s['cnt']
            else:
                avg=0
            resData['avg'].append( avg )

        print()

        pass
        return resData


def logException( e , info ):

    try:
        now=datetime.datetime.now( )
        fn = exceptionPath + now.strftime("%Y-%m-%d") + '.txt'
        prepareFilePath(fn)

        formatted_lines = traceback.format_exc().splitlines()

        data = loadDict( fn )

        if data is None:
            data={}

        _e = str(e)
        if _e not in data:
            data[_e]=[]

        data[_e].append(
            {
                't':getStamp(precise=True),
                'info':info,
                'TB':formatted_lines
            }
        )

        saveDict( fn , data)

    except:
        pass


