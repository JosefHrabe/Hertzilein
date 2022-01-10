import os
import netBase as nb
import compress_json as cj
import matplotlib.pylab as plt
import argparse

cfg_showLegend=True
cfg_ylim = ( 49.75,50.15 )
imgSizeX=16
imgSizeY=9
cfg_plot=False


def  makeMinuteData( xList , yList ):

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
        __x[i] = nb.getDateObject(x)

    pass
    return __x , __y


def plot():


    fig = plt.figure(num=None , figsize=(imgSizeX*0.6,imgSizeY*0.6) , dpi=150 )
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
        data = nb.loadDict( fn )
        sumData['min'].extend( data['min'] )
        sumData['max'].extend( data['max'] )
        sumData['avg'].extend( data['avg'] )
        sumData['t'].extend( data['t'] )
    print()

    m_x , m_y = makeMinuteData( sumData['t'] , sumData['avg'])
    plt.plot( m_x , m_y ,
              label='Minute Average', marker='', linestyle='-',
              color='#000000' , alpha = 0.9 , linewidth=0.7 , zorder=3)


    mean= sum(sumData['avg'])/len(sumData['avg'])
    mean_50 = [ 50.0,50.0 ]
    mean_y = [ mean,mean ]
    mean_x = [ nb.getDateObject( nb.getStamp(offset=-1e8) ) ,nb.getDateObject( nb.getStamp(offset=+1e8) ) ]

    for i in range( len(sumData['t'])):
        print( 'Convert: {0:.2f}%'.format( ((i+1)/len(sumData['t']))*100 ) , end='\r' )
        sumData['to'].append( nb.getDateObject(sumData['t'][i]) )

    plt.plot( sumData['to'] , sumData['avg'] ,
              label='Mittelwert {0:.3f}Hz'.format(mean), marker='', linestyle='-',
              color='#008000' , alpha = 0.4 , linewidth=0.7 , zorder=2)


    plt.plot(mean_x, mean_y, label='Mittelwert {0:.3f}Hz'.format(mean), marker='', linestyle=':',
             color='#008ff5' , linewidth=1 , zorder=2)

    plt.plot(mean_x, mean_50, label='Mittelwert {0:.3f}Hz'.format(50), marker='', linestyle=':',
             color='#ff0000' , linewidth=1 , zorder=2)

    if cfg_showLegend:
        #plot esctions
        #normal area
        dev = 0.02
        mean_base = 50.0
        dMin = [ mean_base-dev,mean_base-dev ]
        dMax = [ mean_base+dev,mean_base+dev ]
        plt.plot(mean_x, dMin, marker='', linestyle=':', linewidth=1 , color='#00aa00' , label='Normalbereich')
        plt.plot(mean_x, dMax, marker='', linestyle=':', linewidth=1 , color='#00aa00')
        plt.fill_between( mean_x , dMin , dMax , color='#00a00040')

        #area with short distortion w/o prim. regulation
        dev = 0.8
        dMin = [ mean_base-dev,mean_base-dev ]
        dMax = [ mean_base+dev,mean_base+dev ]
        plt.plot(mean_x, dMin, marker='', linestyle='-.', linewidth=1 , color='#00aa00' , label='Kurzfr. Störungen\nohne Regulierung')
        plt.plot(mean_x, dMax, marker='', linestyle='-.', linewidth=1 , color='#00aa00')
        plt.fill_between( mean_x , dMin , dMax , color='#00a00020')

        # prim reg.
        dMin = [ mean_base-0.2,mean_base-0.2 ]
        dMax = [ mean_base-0.8,mean_base-0.8 ]
        plt.plot(mean_x, dMin, marker='', linestyle='-', linewidth=1 , color='#606060' , alpha=0.5, label='Aktivierung Leistungsreserve\nt<10')
        plt.fill_between( mean_x , dMin , dMax , color='#ffff00' , alpha=0.1)

        # Abwurf Speicherpumpen
        dMin = [ mean_base-0.8,mean_base-0.8 ]
        dMax = [ mean_base-1.0,mean_base-1.0 ]
        plt.plot(mean_x, dMin, marker='', linestyle='-', linewidth=1 , color='#606060' , alpha=0.6, label='Abwurf Speicherpumpen\nunverzögert')
        plt.fill_between( mean_x , dMin , dMax , color='#ffff00' , alpha=0.2)

        # Lastabwurf Stufe 1
        dMin = [ mean_base-1.0,mean_base-1.0 ]
        dMax = [ mean_base-1.2,mean_base-1.2 ]
        plt.plot(mean_x, dMin, marker='', linestyle='-', linewidth=1 , color='#ffff00' , alpha=0.7, label='Lastabwurf Stufe 1\nca. 12.5%')
        plt.fill_between( mean_x , dMin , dMax , color='#ffff00' , alpha=0.3)

        # Lastabwurf Stufe 2
        dMin = [ mean_base-1.2,mean_base-1.2 ]
        dMax = [ mean_base-1.4,mean_base-1.4 ]
        plt.plot(mean_x, dMin, marker='', linestyle='-', linewidth=1 , color='#ff8000' , alpha=0.7, label='Lastabwurf Stufe 2\nca. 25.0%')
        plt.fill_between( mean_x , dMin , dMax , color='#ff8000' , alpha=0.4)

        # Lastabwurf Stufe 3
        dMin = [ mean_base-1.4,mean_base-1.4 ]
        dMax = [ mean_base-1.6,mean_base-1.6 ]
        plt.plot(mean_x, dMin, marker='', linestyle='-', linewidth=1 , color='#ff4000' , alpha=0.7, label='Lastabwurf Stufe 3\nca. 37.5%')
        plt.fill_between( mean_x , dMin , dMax , color='#ff4000' , alpha=0.5)

        # Lastabwurf Stufe 4
        dMin = [ mean_base-1.6,mean_base-1.6 ]
        dMax = [ mean_base-2.5,mean_base-2.5 ]
        plt.plot(mean_x, dMin, marker='', linestyle='-', linewidth=1 , color='#ff0000' , alpha=0.7, label='Lastabwurf Stufe 4\nmind. 50%')
        plt.fill_between( mean_x , dMin , dMax , color='#ff0000' , alpha=0.6)


        # Blackout
        dMin = [ mean_base-2.5,mean_base-2.5 ]
        dMax = [ 0,0 ]
        plt.plot(mean_x, dMin, marker='', linestyle='-', linewidth=1 , color='#000000' , alpha=1.0, label='Trennung Kraftwerke\nvon Netz')
        plt.fill_between( mean_x , dMin , dMax , color='#000000' , alpha=0.6)

    plt.grid()

    plt.ylim( cfg_ylim )

    plt.xlim(( nb.getDateObject( nb.getStamp( -24*60*60)),
               nb.getDateObject( nb.getStamp( 2*60*60 ))))
    plt.legend( bbox_to_anchor=(0., 1.005, 1., .102), loc='lower left',
                ncol=6, mode="expand", borderaxespad=0. ,
                fontsize=5)


    fig.subplots_adjust(top=0.87)
    fig.subplots_adjust(bottom=0.05)
    fig.subplots_adjust(left=0.05)
    fig.subplots_adjust(right=0.95)
    plt.xticks( fontsize=5)
    plt.yticks( fontsize=5)

    title = 'Netzfrequenz'

    plt.title( title , size=9, y=1.09)

    if cfg_plot:
        plt.savefig( nb.plotsPath+nb.getStamp()+'.png')
    else:
        plt.show()


if __name__ == '__main__':
    # cfg_plot=True
    plot()