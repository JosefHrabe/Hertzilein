import os
import netBase as nb
import compress_json as cj


def strip():

    dList = os.listdir( nb.slopePackedPath )
    infiles=[]
    for d in dList:
        _dir = nb.slopePackedPath + d + '/'
        fList = os.listdir( _dir )

        for f in fList:
            fn = _dir+f
            infiles.append(fn)

    infiles.sort()

    for fn in infiles:
        print('Strip: {0}'.format(fn))
        dest = fn.replace( nb.slopePackedPath , nb.slopeStrippedPath )

        if not os.path.exists( dest ):
            data = nb.loadDict( fn )
            flt = nb.Filter()
            resData = flt.calcArithmetics(data , asTimeObject=False)
            cj.dump( resData , dest )
            # nb.saveDict( dest+'.txt' , resData)
            pass


if __name__ == '__main__':

    strip()