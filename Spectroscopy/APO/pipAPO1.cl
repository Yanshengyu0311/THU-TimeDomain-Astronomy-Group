procedure pip()

real   readnoise      {4.9,prompt="Readnoise"}
real   gain           {1.68,prompt="Gain"}
string trim_region    {"[10:2030,300:900]",prompt="Trim region"}

begin

print("**********************************************")
print("Zero combine and correction and overscan")
del Zero.fits
zerocombine(input="@bias.lst",output="Zero",ccdtype='',combine="average",reject="avsigclip",rdnoise=readnoise,gain=gain)
ccdproc(images="*.fits",ccdtype='',fixpix=no,oversca=yes,trim=no,zerocor=yes,darkcor=no,flatcor=no,zero="Zero",biassec="[2051:2096,2:1027]")
print("**********************************************")
print("Dark combine and correction")
#del Dark.fits
#darkcombine(input="@dark.lst",output="Dark",ccdtype='',combine="average",reject="minmax",process=no,scale="exposure",rdnoise=readnoise,gain=gain)
#ccdproc(images="*.fits",ccdtype='',fixpix=no,oversca=no,trim=no,zerocor=no,darkcor=yes,flatcor=no,dark="Dark",biassec="[2051:2096,2:1027]")

print("**********************************************")
print("Trim the images")
#trim region: b [500:1800,300:750], r [700:2000,300:750]
ccdproc(images="*.fits",ccdtype='',fixpix=no,oversca=no,trim=yes,zerocor=no,darkcor=no,flatcor=no,trimsec=trim_region,biassec="[2051:2096,2:1027]")

print("**********************************************")
print("Flat combine normalize and correction")
del Flat.fits
flatcombine(input="@flat.lst",ccdtype='',output="Flat",combine="average",reject="avsigclip",process=no,scale="median",rdnoise=readnoise,gain=gain)
del Flatre.fits

longslit.dispaxis=1

del Flatre.fits
del Flatri.fits
del nFlat.fits

response(calibrat="Flat",normaliz="Flat",response="Flatre",interac=no,functio="spline3",order=15)
illumination(images="Flatre",illumina="Flatri",interac=no,nbins=20,functio="spline3",order=12)
imarith(operand1="Flatre.fits",op="/",operand2="Flatri.fits",result="nFlat.fits")
ccdproc(images="*.fits",ccdtype='',fixpix=no,oversca=no,trim=no,zerocor=no,darkcor=no,flatcor=yes,flat="nFlat",biassec="[2051:2096,2:1027]")

#imcombine(input=objlist,output=outputname,combine="average",reject="avsigclip",scale="exposure",expname="EXPTIME",rdnoise=readnoise,gain=gain,weight="none")

end
