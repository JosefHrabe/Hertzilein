import os, sys

import matplotlib.pylab as plt
import netBase as nb
import argparse

imgSizeX=16
imgSizeY=9
cfg_showLegend=True
cfg_showSamples=True
cfg_normalize=True
cfg_plot=True
cfg_avgSample=[0.0]
cfg_ylim= ( 0.0,0.0 )
cfg_limit=False


def mainFunc():
    inList=[]
    dList = os.listdir(nb.logDataPath)
    dList.sort(reverse=True)


    fig = plt.figure(num=None , figsize=(imgSizeX*0.6,imgSizeY*0.6) , dpi=150 )


    for d in dList:
        dn = nb.logDataPath + d
        if os.path.isdir( dn ):
            if '/202' in dn:
                fList = os.listdir( dn )
                for f in fList:
                    fn = dn + '/' + f
                    if os.path.isfile ( fn ):
                        inList.append( fn )


    inList.sort()
    # for i in inList:    print(i)

    if cfg_limit != 0:
        while len(inList) > cfg_limit:
            inList.pop(0)


    freqData=[]
    time_str=[]

    #fill raw data
    for fn in inList:
        resData = nb.loadDict( fn )

        for i,r in enumerate(resData):
            print('load {0}: {1:.2f}%'.format(fn.split('/')[-1] , ((i+1)/len(resData))*100) , end='\r')
            time_str.append( r['t'] )
            freqData.append( r['f'] )

    print()
    #convert time data
    timeData=[]
    for t_s in time_str:
        do = nb.getDateObject( t_s)
        if do is not None:
            timeData.append( do )
    del time_str

    print('Samples : {0}'.format(len(timeData)))

    mean_o= sum(freqData)/len(freqData)

    if cfg_normalize:
        offset = 50.0-mean_o

        for i,f in enumerate(freqData): freqData[i] = f+offset

    mean= sum(freqData)/len(freqData)

    mean_y = [ mean,mean ]


    mean_x = [ timeData[0] ,
               #timeData[-1]
               nb.getDateObject( nb.getStamp( offset=2*60*60 ) )
               ]

    flt = nb.Filter( )

    plt.plot(mean_x, mean_y, label='Mittelwert {0:.3f}Hz'.format(mean), marker='', linestyle=':',
             color='#008ff5' , linewidth=1 , zorder=2)
    #plot data
    if cfg_showSamples:
        plt.plot(timeData, freqData, label='Original', marker=',', linestyle=':', color='#008ff540', zorder=1)

    for avg in cfg_avgSample:
        print('Make Trace : {0}'.format(avg))
        outdata= flt.smooth(freqData, k=avg)
        plt.plot( timeData ,  outdata ,
                  label='Netzfrequenz ({0}Sa) - sym'.format(avg) , marker='' , linestyle='-' ,
                  color='#000000' , alpha=0.7 , linewidth=0.7 ,  zorder=3)

        # outdata= flt.smoothPast(freqData, k=avg*2)
        # plt.plot( timeData ,  outdata ,
        #           label='Netzfrequenz ({0}Sa) - past'.format(avg) , marker='' , linestyle='-' ,
        #           color='#ff0000' , alpha=0.5 , linewidth=0.6 ,  zorder=3)


    if cfg_showLegend:
        #plot esctions
        #normal area
        dev = 0.02
        dMin = [ mean-dev,mean-dev ]
        dMax = [ mean+dev,mean+dev ]
        plt.plot(mean_x, dMin, marker='', linestyle=':', color='#00aa00' , label='Normalbereich')
        plt.plot(mean_x, dMax, marker='', linestyle=':', color='#00aa00')
        plt.fill_between( mean_x , dMin , dMax , color='#00a00040')

        #area with short distortion w/o prim. regulation
        dev = 0.8
        dMin = [ mean-dev,mean-dev ]
        dMax = [ mean+dev,mean+dev ]
        plt.plot(mean_x, dMin, marker='', linestyle='-.', color='#00aa00' , label='Kurzfr. Störungen\nohne Regulierung')
        plt.plot(mean_x, dMax, marker='', linestyle='-.', color='#00aa00')
        plt.fill_between( mean_x , dMin , dMax , color='#00a00020')

        # prim reg.
        dMin = [ mean-0.2,mean-0.2 ]
        dMax = [ mean-0.8,mean-0.8 ]
        plt.plot(mean_x, dMin, marker='', linestyle='-', color='#606060' , alpha=0.5, label='Aktivierung Leistungsreserve\nt<10')
        plt.fill_between( mean_x , dMin , dMax , color='#ffff00' , alpha=0.1)

        # Abwurf Speicherpumpen
        dMin = [ mean-0.8,mean-0.8 ]
        dMax = [ mean-1.0,mean-1.0 ]
        plt.plot(mean_x, dMin, marker='', linestyle='-', color='#606060' , alpha=0.6, label='Abwurf Speicherpumpen\nunverzögert')
        plt.fill_between( mean_x , dMin , dMax , color='#ffff00' , alpha=0.2)

        # Lastabwurf Stufe 1
        dMin = [ mean-1.0,mean-1.0 ]
        dMax = [ mean-1.2,mean-1.2 ]
        plt.plot(mean_x, dMin, marker='', linestyle='-', color='#ffff00' , alpha=0.7, label='Lastabwurf Stufe 1\nca. 12.5%')
        plt.fill_between( mean_x , dMin , dMax , color='#ffff00' , alpha=0.3)

        # Lastabwurf Stufe 2
        dMin = [ mean-1.2,mean-1.2 ]
        dMax = [ mean-1.4,mean-1.4 ]
        plt.plot(mean_x, dMin, marker='', linestyle='-', color='#ff8000' , alpha=0.7, label='Lastabwurf Stufe 2\nca. 25.0%')
        plt.fill_between( mean_x , dMin , dMax , color='#ff8000' , alpha=0.4)

        # Lastabwurf Stufe 3
        dMin = [ mean-1.4,mean-1.4 ]
        dMax = [ mean-1.6,mean-1.6 ]
        plt.plot(mean_x, dMin, marker='', linestyle='-', color='#ff4000' , alpha=0.7, label='Lastabwurf Stufe 3\nca. 37.5%')
        plt.fill_between( mean_x , dMin , dMax , color='#ff4000' , alpha=0.5)

        # Lastabwurf Stufe 4
        dMin = [ mean-1.6,mean-1.6 ]
        dMax = [ mean-2.5,mean-2.5 ]
        plt.plot(mean_x, dMin, marker='', linestyle='-', color='#ff0000' , alpha=0.7, label='Lastabwurf Stufe 4\nmind. 50%')
        plt.fill_between( mean_x , dMin , dMax , color='#ff0000' , alpha=0.6)


        # Blackout
        dMin = [ mean-2.5,mean-2.5 ]
        dMax = [ 0,0 ]
        plt.plot(mean_x, dMin, marker='', linestyle='-', color='#000000' , alpha=1.0, label='Trennung Kraftwerke\nvon Netz')
        plt.fill_between( mean_x , dMin , dMax , color='#000000' , alpha=0.6)



    slpdata = nb.loadDict( nb.slopePath+'test.txt'  )
    slpWfm = flt.calcArithmetics( slpdata)

    plt.plot( slpWfm['t'] ,  slpWfm['avg'] ,
              label='avg' , marker=',' , linestyle='-' ,
              color='#6000a0' , alpha=0.7 , linewidth=0.5 ,  zorder=5)


    plt.grid()
    if cfg_ylim == ( 0.0,0.0 ):
        dev=0.022
        plt.ylim(( mean-dev , mean+dev))
    else:
        plt.ylim( cfg_ylim )

    plt.xlim(( nb.getDateObject( nb.getStamp( -24*60*60)),
               nb.getDateObject( nb.getStamp( 2*60*60 ))))
    plt.legend( bbox_to_anchor=(0., 1.005, 1., .102), loc='lower left',
                ncol=6, mode="expand", borderaxespad=0. ,
                fontsize=5)


    # snap_cursor = nb.SnappingCursor(ax, line , timeData )
    # fig.canvas.mpl_connect('motion_notify_event', snap_cursor.on_mouse_move)
    # cursor = nb.Cursor(ax)
    # fig.canvas.mpl_connect('motion_notify_event', cursor.on_mouse_move)

    fig.subplots_adjust(top=0.87)
    fig.subplots_adjust(bottom=0.05)
    fig.subplots_adjust(left=0.05)
    fig.subplots_adjust(right=0.95)
    plt.xticks( fontsize=5)
    plt.yticks( fontsize=5)

    title = 'Netzfrequenz'

    if cfg_normalize:
        title+=' - {0:.3f}Hz - Normiert'.format( mean_o )

    plt.title( title , size=9, y=1.09)

    if cfg_plot:
        plt.savefig( nb.plotsPath+nb.getStamp()+'.png')
    else:
        plt.show()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-hidelegend'  , dest='hidelegend', required=False , action='store_true',
                        help='Hide legend')
    parser.set_defaults(hidelegend=False)

    parser.add_argument('-samples'  , dest='samples', required=False , action='store_true',
                        help='Show samples')
    parser.set_defaults(samples=False)

    parser.add_argument('-norm'  , dest='norm', required=False , action='store_true',
                        help='Normalize mean to 50Hz')
    parser.set_defaults(norm=False)

    parser.add_argument('-avgTrace'  , type=int, default=120   , nargs = '+'   , required=False ,
                        help='120Sa, Average calc., samples BEFORE & AFTER current sample')

    parser.add_argument('-plot'  , dest='plot', required=False , action='store_true',
                        help='Plot output into file')
    parser.set_defaults(plot=False)

    parser.add_argument('-yLim', type=float, nargs=2 , default=0 , required=False  ,
                        help='vertical default limit in diagram')

    parser.add_argument('-limit'  , type=int, default=48  , required=False ,
                        help='48h, number of hours to be displayed')




    args = parser.parse_args()
    cfg_showLegend  = not args.hidelegend
    cfg_showSamples = args.samples
    cfg_normalize   = args.norm
    cfg_plot        = args.plot
    cfg_limit       = args.limit

    if type( args.avgTrace ) is list :
        cfg_avgSample   = args.avgTrace
    else:
        cfg_avgSample = [args.avgTrace]

    if type( args.yLim ) is list :
        cfg_ylim = ( min(args.yLim) , max(args.yLim) )
    mainFunc()


