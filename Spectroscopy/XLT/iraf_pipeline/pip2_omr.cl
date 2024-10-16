procedure pip()

string obj_filename   {prompt="Object file name"}
string obj_lamp_name  {prompt="Object lamp name"}
string std_filename   {prompt="Standard file name"}
string std_lamp_name  {prompt="Standard lamp name"}
real   aperture       {prompt="Apall apterture"}
string cal_dir        {prompt="Directory of standard stars"}
string star_name      {prompt="Name of standard star"}
string extin_file     {prompt="Extinction file"}
string output_file    {prompt="Output spectrum name"}

begin

string tmp,tmp1,tmp2,tmp3,name1,name2
real ap1,ap2

ap1=-1*aperture
ap2=aperture

apextract.dispaxis=1

# Cosmicrays removing
print("**********************************************")
print("Romoving the cosmicrays")

i=stridx(".",obj_filename)
tmp=substr(obj_filename,1,i-1)+"_c"+substr(obj_filename,i,i+3)+"s"
imdelet(tmp)
del temp.fits 
del temp1.fits 

cosmicray(input=obj_filename,output='temp.fits',thresho=10,fluxrat=5.,npasses=5,window=5,interac=no,answer=yes)

cosmicray(input='temp.fits',output='temp1.fits',thresho=10,fluxrat=5.,npasses=5,window=5,interac=no,answer=yes)

cosmicray(input='temp1.fits',output=tmp,thresho=10,fluxrat=5.,npasses=5,interac=yes,answer=yes)

#cosmicray(input=obj_filename,output=tmp,thresho=3.5,fluxrat=5.,npasses=5,window=5,interac=yes,answer=yes)

# Apall
print("**********************************************")
print("Apall object spectrum")

i=stridx(".",tmp)
tmp1=substr(tmp,1,i-1)+".ms"+substr(tmp,i,i+3)+"s"
imdelet(tmp1)

apall(input=tmp,output="",format="multispec",referen="",interac=yes,find=yes,recente=yes,resize=yes,edit=yes,trace=yes,fittrac=yes,extract=yes,extras=yes,review=yes,nfind=1,llimit=ap1,ulimit=ap2,t_funct="spline3",t_order=5,backgro="fit",weights="variance",pfit="fit2d")

print("**********************************************")
print("Apall object lamp spectrum")

del hear01.0001.fits

apall(input=obj_lamp_name,output="hear01",format="onedspec",referen=tmp,interac=no,find=no,recente=no,resize=no,edit=no,trace=no,fittrac=no,extract=yes,extras=no,review=yes,nfind=1,llimit=ap1,ulimit=ap2,t_funct="spline3",t_order=5,backgro="none",weights="none",pfit="fit1d")

print("**********************************************")
print("Apall std spectrum")

i=stridx(".",std_filename)
tmp=substr(std_filename,1,i-1)+".ms"+substr(std_filename,i,i+3)+"s"
imdelet(tmp)

apall(input=std_filename,output="",format="multispec",referen="",interac=yes,find=yes,recente=yes,resize=yes,edit=yes,trace=yes,fittrac=yes,extras=yes,review=yes,nfind=1,llimit=ap1,ulimit=ap2,t_funct="spline3",t_order=5,backgro="fit",weights="variance",pfit="fit2d")

print("**********************************************")
print("Apall object lamp spectrum")

del hear02.0001.fits

apall(input=std_lamp_name,output="hear02",format="onedspec",referen=std_filename,interac=no,find=no,recente=no,resize=no,edit=no,trace=no,fittrac=no,extract=yes,extras=no,review=yes,nfind=1,llimit=ap1,ulimit=ap2,t_funct="spline3",t_order=5,backgro="none",weights="none",pfit="fit1d")

print("**********************************************")
print("Wavelength identify")
identify(images="hear01.0001",coordli="linelists$idhenear.dat",order=1)
#identify(images="hear02.0001",coordli="linelists$idhenear.dat",order=1)
#identify(images="hear01.0001",coordli="linelists$thar.dat",order=1)
#identify(images="hear02.0001",coordli="linelists$thar.dat",order=1)

refspectra(input=tmp1,referen="hear01.0001.fits",sort="",group="",overrid=yes,answer=yes)
refspectra(input=tmp,referen="hear01.0001.fits",sort="",group="",overrid=yes,answer=yes)

tmp2="d"+tmp1
imdelet(tmp2)
dispcor(input=tmp1,output=tmp2,flux=no,samedis=yes,global=yes,ignorea=yes)

tmp3="d"+tmp
imdelet(tmp3)
dispcor(input=tmp,output=tmp3,flux=no,samedis=yes,global=yes,ignorea=yes)

del std
standard(input=tmp3,output="std",bandwid=50.,bandsep=50.,caldir=cal_dir,star_nam=star_name,observatory="bao",extinction=extin_file,answer=yes)

del sens.fits
sensfunc(standards="std",sensitivity="sens",observatory="bao",extinction=extin_file,functio="spline3",order=20)

tmp="c"+tmp2

imdelet(tmp)
calibrate(input=tmp2,output=tmp,extinction=extin_file,sensitivity="sens",extinct=yes,observatory="bao",flux=yes)

scopy(input=tmp,output=output_file,format="onedspec",clobber=yes)

# Removing the atomospheric absorptions

del standard_c.fits

calibrate(input=tmp3,output="standard_c",extinction=extin_file,sensitivity="sens",extinct=yes,observatory="bao",flux=yes)

del starabs.fits

continuum(input="standard_c",output="starabs",functio="spline3",order=20,overrid=yes,type="ratio")

del atom.0001.fits

scopy(input="starabs",output="atom",bands=1,format="onedspec",clobber=yes)

del atom.dat

wspectext(input="atom.0001.fits",output="atom.dat",header=no)

name1=output_file+".0001.fits"
name2=output_file+".txt"
wspectext(input=name1,output=name2,header=no)
end
