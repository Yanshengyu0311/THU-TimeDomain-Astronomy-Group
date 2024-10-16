procedure pip()

string obj_filename   {prompt="Object file name"}
string obj_lamp_name  {prompt="Object lamp name"}
string std_filename   {"hz4.0001r.fits",prompt="Standard file name"}
string std_lamp_name  {prompt="Standard lamp name"}
real   aperture       {prompt="Apall apterture"}
string cal_dir        {"/home/ysy/iraf/APO_data/standard/allstandar/",prompt="Directory of standard stars"}
string star_name      {prompt="Name of standard star"}
string extin_file     {"/home/ysy/iraf/APO_data/pipline/apoextinct.dat",prompt="Extinction file"}
string output_file    {prompt="Output spectrum name，such as 18hti_r, not 18hti.fits"}

begin

string tmp,tmp1,tmp2,tmp3,tmp_std_c
real ap1,ap2

ap1=-1*aperture
ap2=aperture

apextract.dispaxis=1

  noao.twodspec
  longslit 
  longslit.dispaxis=1

# Cosmicrays removing
print("**********************************************")
print("Romoving the cosmicrays")

# del .pl
i=stridx(".",obj_filename)
#tmp=substr(obj_filename,1,i-1)+"_c"+substr(obj_filename,i,i+3)+"s"
tmp=substr(obj_filename,1,i-1)+"_c"+".fits"
imdelet(tmp)

i=stridx(".",std_filename)
tmp_std_c=substr(std_filename,1,i-1)+"_c"+substr(std_filename,i,i+9)+"s"
print("tmp_std_c")
print(tmp_std_c)

imdelet(tmp_std_c)
#"hz4_c.0001r.fits"
del temp.fits 
del temp1.fits
###
crmedian(input=obj_filename,output=tmp)
crmedian(input=std_filename,output=tmp_std_c)
# Apall
print("**********************************************")
print("Apall object spectrum")

i=stridx(".",tmp)
#tmp1=substr(tmp,1,i-1)+".ms"+substr(tmp,i,i+3)+"s"
tmp1=substr(tmp,1,i-1)+".ms"+".fits"
imdelet(tmp1)

apall(input=tmp,output="",format="multispec",referen="",interac=yes,find=yes,recente=yes,resize=yes,edit=yes,trace=yes,fittrac=yes,extract=yes,extras=yes,review=yes,llimit=ap1,ulimit=ap2,t_funct="spline3",t_order=3,backgro="fit",weights="variance",pfit="fit2d")

print("**********************************************")
print("Apall object lamp spectrum")

del henear01.0001.fits

apall(input=obj_lamp_name,output="henear01",format="onedspec",referen=tmp,interac=no,find=no,recente=no,resize=no,edit=no,trace=no,fittrac=no,extract=yes,extras=no,review=yes,llimit=ap1,ulimit=ap2,t_funct="spline3",t_order=3,backgro="none",weights="none",pfit="fit1d")

print("**********************************************")
print("Apall std spectrum")
#tmp_std_c="hz4_c.0001r.fits"
i=stridx(".",tmp_std_c)
tmp=substr(tmp_std_c,1,i-1)+substr(tmp_std_c,i,i+5)+".fits"
print("tmp")
print(tmp)
#tmp="hz4.0001r.ms.fits"
imdelet(tmp)

apall(input=tmp_std_c,output=tmp,format="multispec",referen="",interac=yes,find=yes,recente=yes,resize=yes,edit=yes,trace=yes,fittrac=yes,extras=yes,review=yes,llimit=ap1,ulimit=ap2,t_funct="spline3",t_order=5,backgro="fit",weights="variance",pfit="fit2d")

print("**********************************************")
print("Apall standard lamp spectrum")

del henear02.0001.fits

apall(input=std_lamp_name,output="henear02",format="onedspec",referen=tmp_std_c,interac=no,find=no,recente=no,resize=no,edit=no,trace=no,fittrac=no,extract=yes,extras=no,review=yes,llimit=ap1,ulimit=ap2,t_funct="spline3",t_order=5,backgro="none",weights="none",pfit="fit1d")

print("**********************************************")
print("Wavelength identify")

#del henear01.0002.fits
#del henear02.0002.fits

#imfunction(input="henear01.0001",output="henear01.0002",function="log10")
#imfunction(input="henear02.0001",output="henear02.0002",function="log10")
identify(images="henear01.0001",coordli="linelists$henear.dat",functio="spline3",order=2)
identify(images="henear02.0001",coordli="linelists$henear.dat",functio="spline3",order=2)
print(tmp1)

refspectra(input=tmp1,referen="henear01.0001.fits",sort="",group="",answer=yes)
refspectra(input=tmp, referen="henear02.0001.fits",sort="",group="",answer=yes)


tmp2="d"+tmp1
imdelet(tmp2)
dispcor(input=tmp1,output=tmp2)
print("222222222")
tmp3="d"+tmp
imdelet(tmp3)
dispcor(input=tmp,output=tmp3)
print("333333333")
del std
standard(input=tmp3,output="std",caldir=cal_dir,star_nam=star_name,observatory="APO",extinction=extin_file)
print("44444444")
del sens.0001.fits
sensfunc(standards="std",sensitivity="sens",observatory="APO",extinction=extin_file,functio="spline3",order=12)

tmp="c"+tmp2

imdelet(images=tmp)
calibrate(input=tmp2,output=tmp,extinction=extin_file,sensitivity="sens.0001",extinct=yes,observatory="APO",flux=yes)

scopy(input=tmp,output=output_file,format="onedspec",clobber=yes)

# Removing the atomospheric absorptions
del(files="standard_c.fits")

calibrate(input=tmp3,output="standard_c",extinction=extin_file,sensitivity="sens.0001",extinct=yes,observatory="APO",flux=yes)

del starabs.fits

continuum(input="standard_c",output="starabs",functio="spline3",order=12,overrid=yes,type="ratio")

del atom.0001.fits

scopy(input="starabs",output="atom",bands=1,format="onedspec",clobber=yes)

del atom.dat

wspectext(input="atom.0001.fits",output="atom.dat",header=no)

end
