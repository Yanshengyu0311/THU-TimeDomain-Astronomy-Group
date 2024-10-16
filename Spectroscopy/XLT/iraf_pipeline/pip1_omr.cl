procedure pip()

string log            {prompt="Log file name"}
real   readnoise      {2.64,prompt="Readnoise"}
real   gain           {2.25,prompt="Gain"}
string trim_region    {"[10:1330,20:220]",prompt="Trim region"}
struct* list

begin

real mean_value
string tmp

longslit.dispaxis=1

# Add head parameters, trim, bias and flat correction
print("**********************************************")
print("Add head parameters, trim, bias and flat correction")
readlog(im=log,bf=yes,keyfile=log,list1=log)

print("**********************************************")
print("Zero combine and correction")
del Zero.fits
zerocombine(input="@bias.lst",output="Zero",ccdtype="",combine="average",reject="avsigclip",rdnoise=readnoise,gain=gain)
ccdproc(images="*.fit",ccdtype='',fixpix=no,oversca=no,trim=no,zerocor=yes,darkcor=no,flatcor=no,zero="Zero")

print("**********************************************")
print("Trim the images")
ccdproc(images="*.fit",ccdtype='',fixpix=no,oversca=no,trim=yes,zerocor=no,darkcor=no,flatcor=no,trimsec=trim_region)

print("**********************************************")
print("Flat combine normalize and correction")
del Flat.fits
flatcombine(input="@flat.lst",output="Flat",combine="average",reject="avsigclip",ccdtype="",process=no,scale="median",rdnoise=readnoise,gain=gain)
del Flatre.fits

#imstat(images="Flat.fits",fields='midpt',>>"tmp")
#list="tmp"
#tmp=fscan(list)
#tmp=fscan(list,mean_value)
#imarith(operand1="Flat.fits",op="/",operand2=mean_value,result="Flatre.fits")
#del tmp

response(calibrat="Flat",normaliz="Flat",response="Flatre",interac=no,functio="spline3",order=15)
ccdproc(images="*.fit",ccdtype='',fixpix=no,oversca=no,trim=no,zerocor=no,darkcor=no,flatcor=yes,flat="Flatre")

end
