import os
import random

import netBase as nb
import compress_json as cj
from matplotlib import pylab as plt , colors
import argparse
import numpy as np

cfg_showLegend=True
cfg_ylim = ( 49.75,50.15 )
imgSizeX=16
imgSizeY=9
cfg_plot=False


def  makeMinuteData( xList , yList , dtObj=True):

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


def  makePhaseData( yList ):

    __y=[]
    __sum=[]
    sum = 0

    for i,y in enumerate(yList):
        if i==0:
            __y.append(0)
            __sum.append(0)
        else:
            _y=yList[i-1]

            phase=((_y/y)*360)-360
            sum += phase
            __y.append( phase )
            __sum.append(sum)
            pass
    return __y, __sum



def plot(  ):


    fig = plt.figure(num=None , figsize=(imgSizeX*0.6,imgSizeY*0.6) , dpi=150 )
    ax1=plt.subplot()
    ax2 = ax1.twinx()
    mean_50 = [ 50.0,50.0 ]
    mean_x = [ nb.getDateObject( nb.getStamp(offset=-1e8) ) ,nb.getDateObject( nb.getStamp(offset=+1e8) ) ]

    itemSets=[
        { 'path':nb.slopePath , 'fColor':'#000000' , 'phaseColor':'#0000ff' },
        { 'path':nb.scopePath , 'fColor':'#ff4000' , 'phaseColor':'#ff4000' },
    ]

    for itemSet in itemSets:
        mainTraces = itemSet['path'] + nb.mainTraces
        traces = nb.loadDict( mainTraces )

        sumData = traces['sumData']
        m_x = traces['minuteData']['t']
        m_y = traces['minuteData']['m']
        p_y = traces['minuteData']['ph']
        sp_y = traces['minuteData']['ph_sum']

        for i,t in enumerate(m_x):
            m_x[i]=nb.getDateObject(t)


        # m_x , m_y = makeMinuteData( sumData['t'] , sumData['avg'])
        ax1.plot(m_x, m_y,
                       label='Average (1min)', marker='', linestyle='-',
                       color=itemSet['fColor'], alpha = 0.9, linewidth=0.7, zorder=3)


        # p_y, sp_y = makePhaseData( m_y )
        ax2.plot(m_x, p_y,
                       label='Phase (1min)', marker='', linestyle='-',
                       color=itemSet['phaseColor'], alpha = 0.2, linewidth=1, zorder=3)
        ax2.plot(m_x, sp_y,
                       label='Phase (1min)', marker='', linestyle='-',
                       color=itemSet['phaseColor'], alpha = 0.5, linewidth=1, zorder=3)
        ax2.set_ylim((-2,6))


        mean= sum(sumData['avg'])/len(sumData['avg'])
        mean_y = [ mean,mean ]

        # for i in range( len(sumData['t'])):
        #     print( 'Convert: {0:.2f}%'.format( ((i+1)/len(sumData['t']))*100 ) , end='\r' )
        #     sumData['to'].append( nb.getDateObject(sumData['t'][i]) )
        #
        # ax1.plot(sumData['to'], sumData['avg'],
        #                label='Average (1s)', marker='', linestyle='-',
        #                color='#008000', alpha = 0.4, linewidth=0.7, zorder=2)


        # mean of item
        ax1.plot(mean_x, mean_y, label='Measured Mean {0:.3f}Hz'.format(mean), marker='', linestyle=':',
                       color='#008ff5', linewidth=1, zorder=2)


    # 50Hz line
    ax1.plot(mean_x, mean_50, label='Setpoint {0:.3f}Hz'.format(50), marker='', linestyle=':',
                   color='#ff0000', linewidth=1, zorder=2)

    if cfg_showLegend:
        #plot esctions
        #normal area
        dev = 0.02
        mean_base = 50.0
        dMin = [ mean_base-dev,mean_base-dev ]
        dMax = [ mean_base+dev,mean_base+dev ]
        ax1.plot(mean_x, dMin, marker='', linestyle=':', linewidth=1, color='#00aa00', label='Regular Area')
        ax1.plot(mean_x, dMax, marker='', linestyle=':', linewidth=1, color='#00aa00')
        ax1.fill_between( mean_x , dMin , dMax , color='#00a00040')

        #area with short distortion w/o prim. regulation
        dev = 0.8
        dMin = [ mean_base-dev,mean_base-dev ]
        dMax = [ mean_base+dev,mean_base+dev ]
        ax1.plot(mean_x, dMin, marker='', linestyle='-.', linewidth=1, color='#00aa00', label='Short-term disruptions\nw/o regulation')
        ax1.plot(mean_x, dMax, marker='', linestyle='-.', linewidth=1, color='#00aa00')
        ax1.fill_between( mean_x , dMin , dMax , color='#00a00020')

        # prim reg.
        dMin = [ mean_base-0.2,mean_base-0.2 ]
        dMax = [ mean_base-0.8,mean_base-0.8 ]
        ax1.plot(mean_x, dMin, marker='', linestyle='-', linewidth=1, color='#606060', alpha=0.5, label='Activation 1st power reserve\nt<10s')
        ax1.fill_between( mean_x , dMin , dMax , color='#ffff00' , alpha=0.1)

        # Abwurf Speicherpumpen
        dMin = [ mean_base-0.8,mean_base-0.8 ]
        dMax = [ mean_base-1.0,mean_base-1.0 ]
        ax1.plot(mean_x, dMin, marker='', linestyle='-', linewidth=1, color='#606060', alpha=0.6, label='Dump storage pumps\nwithout delay')
        ax1.fill_between( mean_x , dMin , dMax , color='#ffff00' , alpha=0.2)

        # Lastabwurf Stufe 1
        dMin = [ mean_base-1.0,mean_base-1.0 ]
        dMax = [ mean_base-1.2,mean_base-1.2 ]
        ax1.plot(mean_x, dMin, marker='', linestyle='-', linewidth=1, color='#ffff00', alpha=0.7, label='Load shedding Level 1\n~12.5% load')
        ax1.fill_between( mean_x , dMin , dMax , color='#ffff00' , alpha=0.3)

        # Lastabwurf Stufe 2
        dMin = [ mean_base-1.2,mean_base-1.2 ]
        dMax = [ mean_base-1.4,mean_base-1.4 ]
        ax1.plot(mean_x, dMin, marker='', linestyle='-', linewidth=1, color='#ff8000', alpha=0.7, label='Load shedding Level 2\n~25.0% load')
        ax1.fill_between( mean_x , dMin , dMax , color='#ff8000' , alpha=0.4)

        # Lastabwurf Stufe 3
        dMin = [ mean_base-1.4,mean_base-1.4 ]
        dMax = [ mean_base-1.6,mean_base-1.6 ]
        ax1.plot(mean_x, dMin, marker='', linestyle='-', linewidth=1, color='#ff4000', alpha=0.7, label='Load shedding Level 3\n~37.5% load')
        ax1.fill_between( mean_x , dMin , dMax , color='#ff4000' , alpha=0.5)

        # Lastabwurf Stufe 4
        dMin = [ mean_base-1.6,mean_base-1.6 ]
        dMax = [ mean_base-2.5,mean_base-2.5 ]
        ax1.plot(mean_x, dMin, marker='', linestyle='-', linewidth=1, color='#ff0000', alpha=0.7, label='Load shedding Level 4\n50% load minimum')
        ax1.fill_between( mean_x , dMin , dMax , color='#ff0000' , alpha=0.6)


        # Blackout
        dMin = [ mean_base-2.5,mean_base-2.5 ]
        dMax = [ 0,0 ]
        ax1.plot(mean_x, dMin, marker='', linestyle='-', linewidth=1, color='#000000', alpha=1.0, label='Separation of\npower plants')
        ax1.fill_between( mean_x , dMin , dMax , color='#000000' , alpha=0.6)

    ax1.grid()

    ax1.set_ylim( cfg_ylim )

    ax1.set_xlim(( nb.getDateObject( nb.getStamp( -24*60*60)),
               nb.getDateObject( nb.getStamp( 2*60*60 ))))

    ax1.legend( bbox_to_anchor=(0., 1.005, 1., -.5102), loc='lower left',
                ncol=6, mode="expand", borderaxespad=0. ,
                fontsize=5)
    # ax2.legend( bbox_to_anchor=(0., 1.005, 1., .102), loc='lower left',
    #             ncol=6, mode="expand", borderaxespad=0. ,
    #             fontsize=5)

    # ax1.tick_params(axis='x', labelsize=10 )
    # ax2.tick_params(axis='x', labelsize=10 )
    ax1.tick_params(axis='y', labelsize=5 )
    ax2.tick_params(axis='y', labelsize=5 )

    fig.subplots_adjust(top=0.82)
    fig.subplots_adjust(bottom=0.05)
    fig.subplots_adjust(left=0.05)
    fig.subplots_adjust(right=0.95)
    plt.xticks( fontsize=5)
    # plt.yticks( fontsize=5)

    title = 'Power frequency'

    plt.title( title , size=9, y=1.09)

    if cfg_plot:
        plt.savefig( nb.plotsPath+nb.getStamp()+'.png')
    else:
        plt.show()


def _cvtTimeToSecOfDay( s ):
    dump=s.split('-')
    h=int(dump[0])*60*60
    m=int(dump[1])*60
    s=int(dump[2])

    t=h+m+s
    return t

def _make3DData( indata ):
    # data=[]
    # for _x in range(20):
    #     data.append([])
    #     for _y in range(20):
    #         data[_x].append( random.randint(40,50))

    __x , __y , __z =[],[],[]
    _x=-1
    _stamp=''
    for i,stamp in enumerate( indata['t']):
        dump = stamp.split(' ')

        if _stamp != dump[0]:
            _stamp = dump[0]
            _x+=1
        _t=_cvtTimeToSecOfDay(dump[1])

        __x.append(_x)
        __y.append(_t)
        __z.append( indata['avg'][i] )

    pass
    return __x , __y , __z



def plot3d():


    dList = os.listdir( nb.slopeStrippedPath )
    infiles=[]
    for d in dList:
        _dir = nb.slopeStrippedPath + d + '/'
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

    m_x , m_y=makeMinuteData( sumData['t'] , sumData['avg'] , dtObj=False)
    del sumData
    sumData={ 't':m_x, 'avg':m_y  }

    x,y,z=_make3DData( sumData )

    cmap = plt.cm.nipy_spectral
    norm = colors.Normalize(vmin=min(z), vmax=max(z))
    clr=cmap(norm(z))

    fig = plt.figure(num=None , figsize=(imgSizeX*0.6,imgSizeY*0.6) , dpi=150 )
    ax = plt.subplot(111, projection='3d')

    ax.scatter( x, y, z, marker='.' , color=clr)
    plt.show()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-3d'  , dest='plot3d', required=False , action='store_true',
                        help='plot 3D')
    parser.set_defaults(plot3d=False)

    args = parser.parse_args()

    if args.plot3d:
        plot3d()
    else:
        plot(  )
