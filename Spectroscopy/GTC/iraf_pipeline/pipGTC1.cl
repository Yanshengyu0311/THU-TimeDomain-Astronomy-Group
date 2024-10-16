procedure pip()

string log            {"log",prompt="Log file name"}
real   readnoise      {3.9,prompt="Readnoise"}
real   gain           {1.1,prompt="Gain"}
string trim_region    {"[50:2000,500:900]",prompt="Trim region"}
string reducer        {"Reducer_name",prompt="Reducer name"}
#string trim_or_not    {
#for CCD 1024X1024, gain=1.1, readnoise=3.9
begin


noao
imred
ccdred
onedspec
twodspec
apex
# Check images
images.imutil
del checkimage
#add the reducer name
hedit(image="*fit*",fields="REDUCER",value=reducer,add=yes,delete=no) 

imhead(imlist="*.fit",> "checkimage")
imstat(image="*.fit")

# Add head parameters, trim, bias and flat correction
print("**********************************************")
print("Add head parameters, trim, bias and flat correction")
!ls ./bias/* >bias.lst 
!ls ./flat/* >flat.lst
!rm SCIframe.lst
!ls ./arc/*    >>SCIframe.lst
!ls ./object/* >>SCIframe.lst
!ls ./stds/*    >>SCIframe.lst

print("**********************************************")
print("Zero combine and correction")
del Zero.fits
zerocombine(input="@bias.lst",output="Zero",ccdtype="",combine="average",reject="avsigclip",rdnoise=readnoise,gain=gain)
ccdproc(images="@SCIframe.lst",ccdtype="",fixpix=no,oversca=no,trim=no,zerocor=yes,darkcor=no,flatcor=no,zero="Zero",biassec="[1245:1274,*]")
ccdproc(images="@flat.lst"    ,ccdtype="",fixpix=no,oversca=no,trim=no,zerocor=yes,darkcor=no,flatcor=no,zero="Zero",biassec="[1245:1274,*]")

print("**********************************************")
print("Trim the images")
ccdproc(images="@SCIframe.lst",ccdtype='',fixpix=no,oversca=no,trim=yes,zerocor=no,darkcor=no,flatcor=no,trimsec=trim_region,biassec="[1245:1274,*]")
ccdproc(images="@flat.lst"    ,ccdtype='',fixpix=no,oversca=no,trim=yes,zerocor=no,darkcor=no,flatcor=no,trimsec=trim_region,biassec="[1245:1274,*]")

print("**********************************************")
print("Flat combine normalize and correction")
del Flat.fits
flatcombine(input="@flat.lst",output="Flat",combine="average",reject="avsigclip",ccdtype='',process=no,scale="median",rdnoise=readnoise,gain=gain)
del Flatre.fits

longslit.dispaxis=2

del Flatre.fits
del Flatri.fits
del nFlat.fits
twodspec
longslit
response(calibrat="Flat",normaliz="Flat",response="Flatre",interac=yes,functio="spline3",order=15)
illumination(images="Flatre",illumina="Flatri",interac=yes,nbins=20,functio="spline3",order=12)
imarith(operand1="Flatre.fits",op="/",operand2="Flatri.fits",result="nFlat.fits")

ccdproc(images="@SCIframe.lst",ccdtype='',fixpix=no,oversca=no,trim=no,zerocor=no,darkcor=no,flatcor=yes,flat="nFlat",biassec="[1245:1274,*]")

end
