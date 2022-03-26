import os
import netBase as nb
import compress_json as cj
import argparse

def strip( itemPath ,_min , _max , recalc ):

    print('strip')
    packedPath = itemPath + nb.pathItemPacked
    strippedPath = itemPath + nb.pathItemStripped

    dList = os.listdir( packedPath )
    infiles=[]
    for d in dList:
        _dir = packedPath + d + '/'
        fList = os.listdir( _dir )

        for f in fList:
            fn = _dir+f
            infiles.append(fn)

    infiles.sort()

    for fn in infiles:

        dest = fn.replace( packedPath , strippedPath )

        if (not os.path.exists( dest )) or recalc:
            
            print('{0:>8} : {1}'.format('Strip',fn))
            data = nb.loadDict( fn )
            flt = nb.Filter()
            resData = flt.calcArithmetics(data , asTimeObject=False , _min=_min , _max=_max)
            cj.dump( resData , dest )
            # nb.saveDict( dest+'.txt' , resData)
            pass
        # else:
        #     print('{0:>8} : {1}'.format('Exists',fn))

def pack( itemPath ):

    print('Pack')
    dataPath = itemPath+ nb.pathItemData
    packedPath = itemPath+nb.pathItemPacked

    dList = os.listdir( dataPath )
    infiles=[]
    for d in dList:
        _dir = dataPath + d + '/'
        fList = os.listdir( _dir )

        for f in fList:
            fn = _dir+f
            infiles.append(fn)

    infiles.sort()
    infiles.pop( len(infiles)-1)

    for fn in infiles:

        dest = nb.toCompressFileName( fn , 'gz')
        #dest = dest.replace( slopeDataPath , slopePackedPath )
        dest = dest.replace( dataPath , packedPath )
        if not os.path.exists( dest ):
            print('{0:>8} : {1}'.format('Pack',fn))
            data = nb.loadDict(fn)
            nb.prepareFilePath(dest)
            cj.dump( data , dest )
        # else:
        #     print('{0:>8} : {1}'.format('Exists',fn))

def makeMinuteData( xList , yList , dtObj=True):

    data={}

    for i,x in enumerate(xList) :
        _x = '-'.join(x.split('-')[:-1])
        if _x not in data:
            data[_x]={ 'sum':0 , 'cnt':0}

        data[_x]['sum']+=yList[i]
        data[_x]['cnt']+=1

    __x,__y=[],[]
    for sample in data:
        __x.append( sample+'-30' )
        __y.append( data[sample]['sum'] / data[sample]['cnt'] )


    for i,x in enumerate(__x):
        if dtObj:
            __x[i] = nb.getDateObject(x)
        else:
            __x[i] = x

    pass
    return __x , __y

def makePhaseData( yList ):

    __y=[]
    __sum=[]
    __sumPhase = 0

    for i,y in enumerate(yList):
        if i==0:
            _y=50.0
        else:
            _y=yList[i-1]

        phase=((_y/y)*360)-360
        __sumPhase += phase
        __y.append( phase )
        __sum.append(__sumPhase)
        pass

    return __y, __sum

def calcTraces( itemPath='' , ozzfest_correction=0.0 , force=False ):

    if itemPath=='': return

    strippedPath = itemPath+nb.pathItemStripped
    #outFile = itemPath + nb.mainTraces

    dList = os.listdir( strippedPath )
    infiles=[]
    for d in dList:
        _dir = strippedPath + d + '/'
        fList = os.listdir( _dir )

        for f in fList:
            fn = _dir+f
            infiles.append(fn)

    infiles.sort()

    sumData={ 'min':[] , 'max':[], 'avg':[]  , 't':[], 'to':[]  }

    for i,fn in enumerate(infiles):
        print('Load: {0}'.format(fn) , end='\r')
        # if 1 > 5: continue
        data = nb.loadDict( fn )

        outFile = fn.replace( nb.pathItemStripped , nb.pathItemTraces )

        if not force and os.path.exists( outFile ): continue

        if ozzfest_correction != 0.0:
            for i in range(len( data['min'])):
                print('Ozzfest: {0:.2f}%'.format( 100*((i+1)/(len( data['min']))) ) , end='\r')
                data['min'][i] += ozzfest_correction
                data['max'][i] += ozzfest_correction
                data['avg'][i] += ozzfest_correction
            print()

        m_x , m_y = makeMinuteData( data['t'] , data['avg'] , dtObj=False )
        p_y, sp_y = makePhaseData( m_y )

        traces={
            'sumData' : sumData,
            'minuteData':{
                't':m_x,
                'm':m_y,
                'ph':p_y,
                'ph_sum':sp_y,
            }
        }

        # outFile = itemPath + nb.mainTraces
        nb.saveDict( outFile , traces ,  compress='gz')
    print()






if __name__ == '__main__':

    _min,_max = 48.0 , 52.0

    parser = argparse.ArgumentParser()
    parser.add_argument('-min'    , type=float, default=_min    , required=False  ,
                        help='minimum value for adding sample to tracedata')
    parser.add_argument('-max'    , type=float, default=_max    , required=False  ,
                        help='maximum value for adding sample to tracedata')
    parser.add_argument('-recalc'  , dest='recalc', required=False , action='store_true',
                        help='recalc stripped data')
    parser.set_defaults(recalc=False)

    parser.add_argument('-force'  , dest='force', required=False , action='store_true',
                        help='force calc data')
    parser.set_defaults(force=False)

    args = parser.parse_args()
    recalc = args.recalc

    sets=[      (nb.slopePath , 0.02315659363035383 )
            ,   (nb.scopePath , 0.0)
           ]

    for itempath, ozzfest in sets:
        print('{0:>8} : {1}'.format('PP', itempath))
        pack(itempath)
        strip(itempath, _min , _max , recalc )
        calcTraces(itempath, ozzfest , args.force)



