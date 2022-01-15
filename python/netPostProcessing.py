import os
from netBase import makePackedPath , packFile , slopeDataPath , scopeDataPath


def pack( dataPath ):

    packetPath = makePackedPath( dataPath )

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
        packFile( fn , dataPath , packetPath )


if __name__ == '__main__':
    sets=[ slopeDataPath , scopeDataPath ]
    for dataset in sets:
        pack( dataset )