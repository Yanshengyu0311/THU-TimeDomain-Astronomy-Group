procedure pip()

string obj_filename   {prompt="Object file name"}
string std_filename   {prompt="Standard file name"}
string obj_lamp_name  {prompt="Standard lamp name"}
string star_name      {prompt="Name of standard star"}
string output_file    {prompt="Output spectrum name"}
string inst_name      {"GTC",prompt="instrument name"}
string date           {"19961126",prompt="observed date"}
string telluric_region{"[1050:1640]",prompt="telluric_region"}
string lamp_type      {"linelists$HgAr.dat",prompt="lamp type"}
string cal_dir        {"/home/ysy/iraf/all_std/",prompt="Directory of standard stars"}
string observatory    {"lapalma",prompt="observatory"}
string extin_file     {"/home/ysy/iraf/pip/GTC/GTCextinct.dat",prompt="Extinction file"}

begin

string tmp,tmp1,tmp2,tmp3,name1,name2,std_lamp_name,realoutputfile,tmp_cr_1,tmp_cr_2,tmp_ap_1,tmp_ap_2
real ap1,ap2
std_lamp_name=obj_lamp_name
ap1=-1
ap2=1

apextract.dispaxis=1

noao.twodspec
longslit 
longslit.dispaxis=2

# Cosmicrays removing
print("**********************************************")
print("Romoving the cosmicrays")

tmp_cr_1="CMR_"+output_file +".fits"
tmp_cr_2="CMR_"+star_name   +".fits"
imdelet(tmp_cr_1)
imdelet(tmp_cr_2)
crutil
crmedian(input=obj_filename,output=tmp_cr_1)
crmedian(input=std_filename,output=tmp_cr_2)
# Apall
print("**********************************************")
print("Apall object spectrum")

tmp_ap_1="ap_"+output_file +".ms.fits"
delete(files=tmp_ap_1)



apall(input=tmp_cr_1,output=tmp_ap_1,format="multispec",referen="",interac=yes,find=yes,recente=yes,resize=yes,edit=yes,trace=yes,fittrac=yes,extract=yes,extras=yes,review=yes,llimit=ap1,ulimit=ap2,t_funct="spline3",t_order=4,backgro="fit",weights="variance",pfit="fit2d")
print("**********************************************")
print("Apall object lamp spectrum")

del lamp01.0001.fits

apall(input=obj_lamp_name,output="lamp01",format="onedspec",referen=tmp_cr_1,interac=no,find=no,recente=no,resize=no,edit=no,trace=no,fittrac=no,extract=yes,extras=no,review=yes,llimit=ap1,ulimit=ap2,t_funct="spline3",t_order=5,backgro="none",weights="none",pfit="fit2d")

print("**********************************************")
print("Apall std spectrum")


tmp_ap_2="ap_"+star_name +".ms.fits"
delete(files=tmp_ap_2)


apall(input=tmp_cr_2,output=tmp_ap_2,format="multispec",referen="",interac=yes,find=yes,recente=yes,resize=yes,edit=yes,trace=yes,fittrac=yes,extras=yes,review=yes,llimit=ap1,ulimit=ap2,t_funct="spline3",t_order=5,backgro="fit",weights="variance",pfit="fit2d")

print("**********************************************")
print("Wavelength identify")

del lamp01.0002.fits

#imfunction(input='lamp01.0001',output='lamp01.0002',function='log10')
identify(images="lamp01.0001",coordli=lamp_type,functio="spline3",order=1)

refspectra(input=tmp_ap_1,referen="lamp01.0001.fits",sort="",group="",answer=yes)
refspectra(input=tmp_ap_2,referen="lamp01.0001.fits",sort="",group="",answer=yes)

imdelet(image="dispcor_"+output_file +".fits")
imdelet(image="dispcor_"+star_name   +".fits")
dispcor(input=tmp_ap_1,output="dispcor_"+output_file)
dispcor(input=tmp_ap_2,output="dispcor_"+star_name  )

del std
standard(input="dispcor_"+star_name,output="std",bandwid=50.,bandsep=50.,caldir=cal_dir,star_nam=star_name,observatory=observatory,extinction=extin_file)

del sens.fits
del sens.0001.fits
sensfunc(standards="std",sensitivity="sens",observatory=observatory,extinction=extin_file,functio="spline3",order=20)

imdelet(image="cali_"+output_file +".fits")
delete (files="cali_"+output_file +".fits")
calibrate(input="dispcor_"+output_file,output="cali_"+output_file,extinction=extin_file,sensitivity="sens",extinct=yes,observatory=observatory,flux=yes)

scopy(input="cali_"+output_file,output=output_file,format="onedspec",clobber=yes)


del standard_c.fits


del standard_c
calibrate(input="dispcor_"+star_name,output="standard_c",extinction=extin_file,sensitivity="sens",extinct=yes,observatory=observatory,flux=yes)

del starabs.fits

#continuum(input="standard_c",output="starabs",functio="spline3",order=20,overrid=yes,type="ratio")

del atom.0001.fits
del ATOM.fits
del(files=output_file+".fits")
#scopy(input="starabs",output="atom",bands=1,format="onedspec",clobber=yes)
#imcopy(input="atom.0001.fits"+telluric_region,output="ATOM.fits")
realoutputfile=output_file+"_"+inst_name+"_"+date
imdelete(image=realoutputfile+".fits")


#del temp_telluric_1.fits
#del temp_telluric_2.fits
#del temp_telluric_3.fits
#telluric (input=output_file+".0001",     output="temp_telluric_1.fits",cal="atom.0001.fits[1305:1405]",interac=yes)
#telluric (input="temp_telluric_1.fits",  output="temp_telluric_2.fits",cal="atom.0001.fits[1020:1160]",interac=yes)
#telluric (input="temp_telluric_2.fits",  output="temp_telluric_3.fits",cal="atom.0001.fits[1170:1250]",interac=yes)
#telluric (input="temp_telluric_3.fits",  output=realoutputfile        ,cal="atom.0001.fits[1400:1470]",interac=yes)

imcopy(input=output_file+".0001",output=realoutputfile)


name1=realoutputfile+".fits"
name2=realoutputfile+".txt"

del name2
#del atom.dat
#del atom_trim.dat

#wspectext(input="atom.0001.fits",output="atom.dat",     header=no)
#wspectext(input="ATOM.fits"     ,output="atom_trim.dat",header=no)
wspectext(input=name1           ,output=name2          ,header=no)

end
