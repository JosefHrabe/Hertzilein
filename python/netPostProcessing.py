import os
import netBase as nb
import compress_json as cj


def strip( itemPath ):

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

        if not os.path.exists( dest ):
            print('{0:>8} : {1}'.format('Strip',fn))
            data = nb.loadDict( fn )
            flt = nb.Filter()
            resData = flt.calcArithmetics(data , asTimeObject=False)
            cj.dump( resData , dest )
            # nb.saveDict( dest+'.txt' , resData)
            pass
        # else:
        #     print('{0:>8} : {1}'.format('Exists',fn))

def pack( itemPath ):

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

def calcTraces( itemPath ):

    strippedPath = itemPath+nb.pathItemStripped
    outFile = itemPath + nb.mainTraces

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
        sumData['min'].extend( data['min'] )
        sumData['max'].extend( data['max'] )
        sumData['avg'].extend( data['avg'] )
        sumData['t'].extend( data['t'] )
    print()

    m_x , m_y = makeMinuteData( sumData['t'] , sumData['avg'] , dtObj=False )
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

    nb.saveDict( outFile , traces )



if __name__ == '__main__':
    sets=[ nb.slopePath , nb.scopePath ]
    for dataset in sets:
        print('{0:>8} : {1}'.format('PP',dataset))
        pack( dataset )
        strip( dataset )
        calcTraces( dataset )