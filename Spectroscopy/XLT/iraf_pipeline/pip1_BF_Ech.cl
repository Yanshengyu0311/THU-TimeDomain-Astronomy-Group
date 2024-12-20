procedure pip()

#string log            {"log",prompt="Log file name"}
real   readnoise      {3.9,prompt="Readnoise"}
real   gain           {1.1,prompt="Gain"}
string trim_region    {"[250:1600,850:2044]",prompt="Trim region"}
string reducer        {"Reducer_name",prompt="Reducer name"}
##string trim_or_not    {
##for CCD 1024X1024, gain=1.1, readnoise=3.9
begin

noao
imred
ccdred
onedspec
twodspec
apex
images.imutil
echell

#del checkimage
##add the reducer name
#hedit(image="*fit*",fields="REDUCER",value=reducer,add=yes,delete=no) 
#
#imhead(imlist="*.fit",> "checkimage")
#imstat(image="*.fit")

## Add head parameters, trim, bias and flat correction
print("**********************************************")
#print("Add head parameters, trim, bias and flat correction")



imdelete(images="Zero.fits")
imdelete(images="*_t.fit*")

imdelete(images="*_tz.fit*")
imdelete(images="*_tzf.fit*")

delete(files="*.lst")

!ls *BIAS* >bias.lst
!ls *FLAT*_G10_E9* > flat.lst
!ls *_SPECSTARGET_* > obj.lst
!ls *_SPECSFLUXREF_* > std.lst
!ls **_FeAr_*> Arc.lst
!cat *lst > all.lst
!mv *.log new.log

del all_object.lst
!ls *_FeAr_*_E9.fit*      >> all_object.lst
!ls *_SPECSTARGET_*.fit*  >> all_object.lst
!ls *_SPECSFLUXREF_*.fit* >> all_object.lst

print("**********************************************")
print("trime the image")
ccdproc(images="@all.lst",output="@all.lst//_t",ccdtype="",fixpix=no,oversca=no,trim=yes,zerocor=no,darkcor=no,flatcor=no,trimsec=trim_region)
print("Trime Done")
print("**********************************************")

#print("Overscan correction")
#
##ccdproc(images="*.fit",fixpix=no,oversca=yes,trim=no,zerocor=no,darkcor=no,flatcor=no,trimsec=trim_region,biassec="[1245:1274,*]",functio="spline3",order=3)


print("**********************************************")
print("Zero combine")
zerocombine(input="@bias.lst//_t",output="Zero",ccdtype="",combine="median",reject="minmax",rdnoise=readnoise,gain=gain)
print("Zero combine done")

print("**********************************************")
print("Flat combine")
flatcombine(input="@flat.lst//_t",output="Flat_t",combine="average",reject="avsigclip",ccdtype="",process=no,scale="mode",rdnoise=readnoise,gain=gain)
print("Flat combine Done")

print("**********************************************")
print("bias correction")

#!ls Flat_t.fit*             >> bias_cor.lst
#!ls *_FeAr_*_t.fit*         >> bias_cor.lst
#!ls *_SPECSTARGET_*_t.fit*  >> bias_cor.lst
#!ls *_SPECSFLUXREF_*_t.fit* >> bias_cor.lst

ccdproc(images="Flat_t",output="Flat_tz",ccdtype="",fixpix=no,oversca=no,trim=no,zerocor=yes,darkcor=no,flatcor=no,zero="Zero",biassec="")
print("bias correction done")
print("**********************************************")


print("Flat combine normalize and correction")

!ls *_FeAr_*_E9_t.fit*      >> flat_cor.lst
!ls *_SPECSTARGET_*_t.fit*  >> flat_cor.lst
!ls *_SPECSFLUXREF_*_t.fit* >> flat_cor.lst

unlearn echelle
unlearn apall
unlearn apflatten
imdelete(images="_tzf.fit*")
imdelete(images="flat_n")

unlearn apflatten
unlearn apall


echelle.dispaxis=1
echelle

apall(input="Flat_tz",output="",recente=no,resize=no,extract=no,extras=yes,lower=-7,upper=7,width=20,nfind=12,shift=no,avglimi=yes,t_order=3,t_funct="spline3")

apflatten(input="Flat_tz",output="flat_n",referen="Flat_tz",find=no,recente=no,resize=no,trace=no,fittrac=no,order=3,niterat=5)

implot(image="flat_n")

ccdproc(images="@flat_cor.lst",output="@all_object.lst//_tzf",ccdtype="",fixpix=no,oversca=no,trim=no,zerocor=yes,darkcor=no,flatcor=yes,flat="flat_n",zero="Zero",biassec="")

end
