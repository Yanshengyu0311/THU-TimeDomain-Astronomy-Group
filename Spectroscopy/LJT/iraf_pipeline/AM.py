import numpy as np
import sys,os
import astropy
from astropy.io import fits
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
import astropy.units as u
from astropy.time import Time
# bear_mountain = EarthLocation(lat=41.3*u.deg, lon=-74*u.deg, height=390*u.m)
fits_name  = sys.argv[1]
source_ra  = sys.argv[2]
source_dec = sys.argv[3]
fits_name  = os.path.realpath(fits_name)
print(fits_name)
# fits_name="/home/ysy/data/240/2011-2013/2021_03_25/2012ab_slit1.8_G3_YFvd170141/"+"YFvd170141.fits"
# fits_name="D:\\数据处理\\iraf教程\\实验数据\\240\\YFxb100105.fits"
TARGET_fits=astropy.io.fits.open(fits_name)
utcoffset=-8*u.hour
LJ_loacation=astropy.coordinates.EarthLocation(lat=26.6951*u.deg, lon=(360-259.9)*u.deg, height=3193*u.m)
time1 = Time(TARGET_fits[0].header["DATE-OBS"])

# time1 = Time('2016-03-04T22:10:20.303')#-utcoffset
# time1 = Time(56698.8598,format="mjd")#-utcoffset
# source_ra ="13:45:50.75"
# source_dec="26:47:46.4"

source_coor  = SkyCoord(ra=source_ra,dec=source_dec,unit=(u.hourangle, u.deg))
source_altaz = source_coor.transform_to(AltAz(obstime=time1,location=LJ_loacation))
airmass=source_altaz.secz

print(airmass)
#fits_header=TARGET_fits[1].header
TARGET_fits[0].header.set('AIRMASS' ,format(airmass, '.6f'))
#print(source_ra.strip(":"))
#print(fits_header["AIRMASS"])
#TARGET_fits.close()
fits.writeto(fits_name,data=TARGET_fits[1].data,header=TARGET_fits[0].header,overwrite=True)












