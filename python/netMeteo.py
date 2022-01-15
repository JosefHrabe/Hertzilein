

from datetime import datetime
import matplotlib.pyplot as plt
from meteostat import Point
#from meteostat import Daily as Sampler
from meteostat import Hourly as Sampler


def meteo():
    # Set time period
    start = datetime(2021, 6, 1)
    end = datetime(2022, 1, 6)

    # Create Point for Vancouver, BC
    location = Point( 50.50, 12.55)#, 70)

    # Get daily data for 2018
    data = Sampler(location, start, end)
    data = data.fetch()

    # Plot line chart including average, minimum and maximum temperature
    # data.plot(y=['tavg', 'prcp', 'wspd' , 'wdir' , 'snow' , 'tsun'])
    data.calcTraces(y=['temp', 'prcp', 'wspd' , 'wdir' , 'snow' , 'tsun'])
    plt.show()

    # 'date',
    # 'tavg',
    # 'tmin',
    # 'tmax',
    # 'prcp',
    # 'snow',
    # 'wdir',
    # 'wspd',
    # 'wpgt',
    # 'pres',
    # 'tsun'

    # response = requests.get( url='https://wttr.in/')
    # print( response.text )


meteo()

