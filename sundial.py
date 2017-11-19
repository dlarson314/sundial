import ephem

import numpy as np
import matplotlib.pyplot as mpl
import scipy.optimize


def projection_function(sun):
    # Angles are in radians
    # (east, north, up) makes a unit vector pointing toward the sun
    east = np.sin(sun.az) * np.cos(sun.alt)
    north = np.cos(sun.az) * np.cos(sun.alt)
    up = np.sin(sun.alt)

    # Shadow on horizontal surface
    x = -east/up
    y = -north/up

    return x, y 


def get_analemma_data(here, gmt_hour, projection_function, year=2017):
    sun = ephem.Sun()

    first_date = ephem.Date(ephem.Date('%04d/01/01 00:00:00' % year) + ephem.hour * gmt_hour)
    here.date = first_date

    keys = ['az', 'alt', 'x', 'y', 'date', 'year', 'month', 'day_of_month', 
        'gmt_hour', 'isoweekday']
    data = {}
    for key in keys:
        data[key] = []

    sun.compute(here)
    while here.date.tuple()[0] == year:
        sun.compute(here)
        data['az'].append(sun.az)
        data['alt'].append(sun.alt)
        x, y = projection_function(sun)
        data['x'].append(x)
        data['y'].append(y)
        data['date'].append(here.date)

        t = here.date.tuple()
        data['year'].append(t[0])
        data['month'].append(t[1])
        data['day_of_month'].append(t[2])
        data['gmt_hour'].append(t[3])
        
        pydate = here.date.datetime()
        data['isoweekday'].append(pydate.isoweekday())
            
        here.date = here.date + 24 * ephem.hour 

    for key in keys:
        if key != 'date':
            data[key] = np.array(data[key])

    data['location'] = here

    return data


def plot_analemma_rainbow(data, ticklength=0.005, linewidth=1):
    month_colors = ['darkblue', 'blue', 'teal', 'green', 'lime', 'y',
                    'gold', 'orange', 'darkorange', 'red', 'magenta', 'purple']

    x = data['x']
    y = data['y']
    month = data['month']
    isoweekday = data['isoweekday']

    dx = x[2:] - x[0:-2]
    dy = y[2:] - y[0:-2]

    dx = np.hstack((dx[0], dx, dx[-1]))
    dy = np.hstack((dy[0], dy, dy[-1]))

    norm = np.sqrt(dx**2 + dy**2)
    dx = dx / norm
    dy = dy / norm

    for m in range(1, 13):
        color = month_colors[m - 1]
        g = np.where(month == m)
        mpl.plot(x[g], y[g], color, zorder=3, linewidth=linewidth)

    for i in range(len(dx)):
        x0 = x[i]
        y0 = y[i]
        scale = 1
        if isoweekday[i] == 7:   # Give Sundays longer ticks
            scale = 3
        x1 = x0 - dy[i] * ticklength * scale
        y1 = y0 + dx[i] * ticklength * scale
        color = month_colors[month[i] - 1]
        mpl.plot([x0, x1], [y0, y1], color, zorder=3, linewidth=linewidth)


def plot_analemma_gray(data, color=(0.7,0.7,0.7), linewidth=1):
    x = data['x']
    y = data['y']
    mpl.plot(x, y, '-', color=color, zorder=1, linewidth=linewidth)


def plot_dayline(here, day, hours, projection_function, color=(0.5,0.5,0.5), linewidth=1, linestyle='-'):
    offsets = np.linspace(0, hours, 100)
    sun = ephem.Sun()

    xlist = []
    ylist = []
    for offset in offsets:
        here.date = ephem.Date(day) + offset * ephem.hour
        sun.compute(here)

        x, y = projection_function(sun)
        xlist.append(x)
        ylist.append(y)

    mpl.plot(xlist, ylist, color=color, linewidth=linewidth,
        linestyle=linestyle, zorder=2) 


def get_observer():
    # Approximate location of the flag pole near the Statue of Liberty, 
    # based on Google Earth
    here = ephem.Observer()
    here.lat = '40.690574'    # Latitude, decimal degrees, in a string
    here.lon = '-76.045686'   # Longitude, decimal degrees, in a string
    here.elev = 3.0           # Elevation in meters above sea level
    return here


def set_gnomon_height(ax, width=11, height=8.5, gnomon_height=2.717, pos=(0.07, 0.03, 0.9, 0.97)): 
    ax.set_aspect('equal')

    dx_frac = pos[2]
    dy_frac = pos[3]

    dx = dx_frac * width / gnomon_height
    dy = dy_frac * height / gnomon_height

    ylim = ax.get_ylim()
    dy_orig = ylim[1] - ylim[0]
    ylim = (ylim[0] * dy / dy_orig, ylim[1] * dy / dy_orig)

    print pos, tuple(pos)
    print ylim
    mpl.ylim(ylim[0], ylim[1])
    mpl.xlim(-0.5 * dx, 0.5 * dx)

    ax.set_position(pos)

    pos2 = ax.get_position()
    print 'pos = ', pos2
    print 'xlim = ', ax.get_xlim()
    print 'ylim = ', ax.get_ylim()


def set_paper_axes(width=11, height=8.5, pos=(0.07, 0.08, 0.90, 0.85)):
    ax = mpl.gca()
    ax.set_aspect('equal')
    ax.set_position(pos)

    xlim = (pos[0] * width, (pos[0] + pos[2]) * width)
    ylim = (pos[1] * height, (pos[1] + pos[3]) * height)

    mpl.xlim(xlim[0], xlim[1])
    mpl.ylim(ylim[0], ylim[1])


def foo1():
    here = get_observer()

    height = 8.5          # paper height, inches
    width = 11            # paper width, inches
    gnomon_height = 2.5   # height of gnomon, inches
    year = 2017

    mpl.figure(1, figsize=(width, height))
    ax = mpl.gca()

    linewidth = 0.5
    color = (0.7, 0.7, 0.7)
    plot_dayline(here, ephem.Date('2017/12/21 14:00:00'), 6, projection_function, color=color, linewidth=linewidth)
    plot_dayline(here, ephem.Date('2017/03/20 14:00:00'), 6, projection_function, color=color, linewidth=linewidth)
    plot_dayline(here, ephem.Date('2017/06/21 14:00:00'), 6, projection_function, color=color, linewidth=linewidth)

    # Plot the half-hour analemmas in gray
    for hour in np.arange(14.5, 20, 1.0):
        data = get_analemma_data(here, hour, projection_function, year=year)
        plot_analemma_gray(data, color=(0.7,0.7,0.7), linewidth=linewidth)

    # Plot the hour analemmas as rainbows
    for gmt_hour in [14, 15, 16, 17, 18, 19, 20]:
        data = get_analemma_data(here, gmt_hour, projection_function, year=year)
        plot_analemma_rainbow(data, linewidth=linewidth)

    days = [i*7 for i in range(180/7)]
    for day in days:
        plot_dayline(here, data['date'][day] - 6 * ephem.hour, 6, projection_function,
            color=color, linewidth=linewidth, linestyle='--')

    set_gnomon_height(ax, width=width, height=height, gnomon_height=gnomon_height, pos=(0.07, 0.07, 0.9, 0.85))
    mpl.title('Latitude = %s, Longitude = %s, Year = %d' % (here.lat, here.lon, year))
    mpl.xlabel('Easting (units of gnomon height)')
    mpl.ylabel('Northing (units of gnomon height)')

    mpl.savefig('test_analemmas_%d.pdf' % year)
    mpl.savefig('test_analemmas_%d.png' % year)
    mpl.show()


def get_times_of_az(here, start_date, stop_date, target_az=(180,), sun=ephem.Sun()):
    times = np.arange(start_date, stop_date, ephem.hour)

    az_list = np.zeros(len(times)) 

    for i, t in enumerate(times):
        here.date = t
        sun.compute(here)
        az_list[i] = sun.az * 180 / np.pi;

    bags = []

    for target in target_az:
        time_list = [] 
        g = np.where((az_list[0:-1] < target) * (az_list[1:] > target))[0]
        time_pairs = [(times[i], times[i+1]) for i in g] 

        def f(t):
            here.date = t
            sun.compute(here)
            return sun.az * 180 / np.pi - target
                
        for i, p in enumerate(time_pairs):
            date1 = scipy.optimize.brentq(f, p[0], p[1]) 
        
            # 10 seconds before time of desired azimuth
            here.date = date1 - 10 * ephem.second
            sun.compute(here)
            az0 = sun.az
            alt0 = sun.alt

            # Time of desired azimuth
            here.date = date1 
            sun.compute(here)
            az1 = sun.az
            alt1 = sun.alt

            # 10 seconds after time of desired azimuth
            here.date = date1 + 10 * ephem.second
            sun.compute(here)
            az2 = sun.az
            alt2 = sun.alt

            time_list.append((here.date, alt0, alt1, alt2, az0, az1, az2))

        bags.append(time_list)

    return bags


def angle_to_tuple(radians):
    degrees = abs(radians) * 180 / np.pi
    minutes = degrees * 60
    seconds = minutes * 60

    degrees = np.floor(degrees)
    if radians < 0:
        degrees = -degrees
    minutes = np.floor(minutes % 60)
    seconds = np.floor(seconds % 60 + 0.5)

    return degrees, minutes, seconds


def make_table(here, start_date, stop_date, filename='test.tex', target_az=(90, 180, 270)):

    bags = get_times_of_az(here, start_date, stop_date, target_az=target_az, sun=ephem.Sun())

    numaz = len(target_az)

    with open(filename, 'w') as f:
        f.write(r'\begin{center}' + '\n')
        form = 'r|' + '|'.join(['ccc' for i in range(numaz)])
        f.write(r'\begin{tabular}{%s}' % form + '\n')
        f.write(r'\hline' + '\n')
        f.write(r'\hline' + '\n')
        d1, m1, s1, = angle_to_tuple(here.lat)
        d2, m2, s2, = angle_to_tuple(here.lon)
        tup = (1+3*numaz, d1, m1, s1, d2, m2, s2)
        f.write(r"\multicolumn{%d}{c}{latitude $ = %d^\circ%d'%d''$, longitude $ = %d^\circ%d'%d''$} \\"  % tup + '\n')
        f.write(ephem.localtime(bags[0][0][0]).strftime('%B'))
        for az in target_az:
            f.write(r' & \multicolumn{3}{c}{$%d^\circ$}' % az)
        f.write(r'\\' + '\n')
        f.write(ephem.localtime(bags[0][0][0]).strftime('%Y'))
        for az in target_az:
            f.write(r' & Time & Alt & Rate')
        f.write(r'\\' + '\n')
        f.write(r'\hline' + '\n')

        for i in range(len(bags[0]) - 1):
            line = ''
            t = bags[0][i]
            line = ephem.localtime(t[0]).strftime('%a %d')
            for a in range(len(target_az)):
                t = bags[a][i]
                line = line + ' & ' + ephem.localtime(t[0]).strftime('%X') + \
                    ' & $%5.1f^\circ$ & %5.1f' % (t[3]*180/np.pi, (t[6] - t[5]) * 180 * 60 * 60 / np.pi / 10.0)
            line = line + '  \\\\\n'
            #print line,
            f.write(line)
        f.write(r'\hline' + '\n')
        f.write(r'\end{tabular}' + '\n')
        f.write(r'\end{center}' + '\n')

        f.write("""
Time is Eastern Standard Time or Eastern Daylight Time, as applicable.
Alt is the altitude of the center of the sun above the
horizon, in degrees.  Rate is the angular rate at which the shadow cast
by a vertical pole on a level surface is changing, in minutes of arc per
minute of time (or seconds of arc per second of time).
""")


def foo2():
    here = get_observer()

    start_date = ephem.Date('2017/12/01 01:00:00')
    stop_date = ephem.Date('2018/01/02 01:00:00')

    targets = [(90,135,180,225,270) for i in range(12)]

    year = 2018

    for i in range(12):
        month = i + 1
        start_date = ephem.Date('%04d/%02d/01 01:00:00' % (year, month))
        stop_date = ephem.Date('%04d/%02d/02 01:00:00' % (year, month + 1))
        filename = '%04d_month%02d.tex' % (year, month)
        make_table(here, start_date, stop_date, filename=filename, target_az=targets[i])

    

        

if __name__ == "__main__":
    #foo1()  # Test code to create an analemma plot
    foo2()  # Test code to create a table of time when sun is at various azumuth angles

