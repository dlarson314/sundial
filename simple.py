import ephem

# Approximate location of the flag pole near the Statue of Liberty, 
# based on Google Earth
here = ephem.Observer()
here.lat = '40.690574'    # Latitude, decimal degrees, in a string
here.lon = '-76.045686'   # Longitude, decimal degrees, in a string
here.elev = 3.0           # Elevation in meters above sea level

# 9:00 AM on the 4th of July, 2017, with a 4 hour shift from Eastern Daylight Time
# to GMT.
here.date = ephem.Date('2017/07/04 09:00:00') + 4 * ephem.hour 

sun = ephem.Sun()
sun.compute(here)

print "Date                                    (GMT) = ", here.date
print "Latitude            (degrees:minutes:seconds) = ", here.lat
print "Longitude           (degrees:minutes:seconds) = ", here.lon
print "Elevation                            (meters) = ", here.elev 
print "Azimuth of the sun  (degrees:minutes:seconds) = ", sun.az
print "Altitude of the sun (degrees:minutes:seconds) = ", sun.alt


