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




def plot( fCount=10 ):


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

        _p = itemSet['path'] + nb.pathItemTraces

        infiles = nb.fileList( _p)

        infiles = infiles[ -fCount:]

        m_x, m_y, p_y, sp_y  = [], [], [], []
        for fn in infiles:
            data = nb.loadDict( fn )
            m_x.extend(  data['minuteData']['t']      )
            m_y.extend(  data['minuteData']['m']      )
            p_y.extend(  data['minuteData']['ph']     )
            sp_y.extend( data['minuteData']['ph_sum'] )

        # mainTraces = itemSet['path'] + nb.mainTraces
        # traces = nb.loadDict( mainTraces )

        # sumData = traces['sumData']
        # m_x = traces['minuteData']['t']
        # m_y = traces['minuteData']['m']
        # p_y = traces['minuteData']['ph']
        # sp_y = traces['minuteData']['ph_sum']

        for i,t in enumerate(m_x):
            m_x[i]=nb.getDateObject(t)


        ax1.plot(m_x, m_y,
                       label='Average (1min)', marker='', linestyle='-',
                       color=itemSet['fColor'], alpha = 0.9, linewidth=0.7, zorder=3)


        ax2.plot(m_x, p_y,
                       label='Phase (1min)', marker='', linestyle='-',
                       color=itemSet['phaseColor'], alpha = 0.2, linewidth=1, zorder=3)
        ax2.plot(m_x, sp_y,
                       label='Phase (1min)', marker='', linestyle='-',
                       color=itemSet['phaseColor'], alpha = 0.5, linewidth=1, zorder=3)
        ax2.set_ylim((-2,6))


        #mean= sum(sumData['avg'])/len(sumData['avg'])
        mean= sum( m_y )/len( m_y )
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




def plot3d( fCount=10 ):

    x,y,z=[],[],[]
    infiles= nb.fileList(nb.slopeTracesPath)

    infiles = infiles[ -fCount : ]

    for f in infiles:
        print('Add : ' + f )
        data = nb.loadDict( f )

        for i,t in enumerate( data['minuteData']['t']):
            _x , _y = nb.dataToXY( t )

            x.append( _x )
            y.append( _y )
            z.append( data['minuteData']['m'][i] )


    clr='#008ff5'
    cmap = plt.cm.nipy_spectral
    norm = colors.Normalize(vmin=min(z), vmax=max(z))
    clr=cmap(norm(z))
#
    fig = plt.figure(num=None , figsize=(imgSizeX*0.6,imgSizeY*0.6) , dpi=150 )
    ax = plt.subplot(111, projection='3d')

    ax.scatter( x, y, z, marker='.' , color=clr)
    plt.show()

    pass



def plotDate( dates=[] ):

    allFiles = []
    dirList = os.listdir( nb.slopePackedPath )
    for d in dirList :
        fList = os.listdir( nb.slopePackedPath + d )

        for f in fList:
            fn = nb.slopePackedPath+d+'/'+f

            for flt in dates:
                if flt in fn:
                    allFiles.append( fn)

    allFiles.sort()
    _f=[]
    _t=[]
    for af in allFiles:
        print(af)
        data = nb.loadDict( fn )
        for d in data:
            _f.append(d['f'])
            # _t.append( nb.getDateObject(d['t']))

    plt.plot(  _f )
    plt.show()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-3d'  , dest='plot3d', required=False , action='store_true',
                        help='plot 3D')

    parser.add_argument('-days'  , type=int , default=7 , required=False)

    args = parser.parse_args()

    days = args.days
    fCount = days * 24

    if args.plot3d:
        plot3d( fCount=fCount )
    else:
        plot( fCount=fCount )

    pass