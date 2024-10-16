procedure pip()

string obj_filename   {prompt="Object file name"}
string std_filename   {prompt="Standard file name"}
string obj_lamp_name  {prompt="Standard lamp name"}
string star_name      {prompt="Name of standard star"}
string output_file    {prompt="Output spectrum name"}
string cal_dir        {"/home/ysy/iraf/all_std/",prompt="Directory of standard stars"}
string extin_file     {"/home/ysy/iraf/pip/216/baoextinct.dat",prompt="Extinction file"}

begin

string tmp,tmp1,tmp2,tmp3,name1,name2,std_lamp_name,realoutputfile,tmp_cr_1,tmp_cr_2,tmp_ap_1,tmp_ap_2
real ap1,ap2
std_lamp_name=obj_lamp_name
ap1=-1
ap2=1

apextract.dispaxis=1

  noao.twodspec
  longslit 
  longslit.dispaxis=1

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

#hedit(image=obj_lamp_name,fields="CD1_1",delete=yes)
#hedit(image=tmp_cr_1     ,fields="CD1_1",delete=yes)
#hedit(image=tmp_cr_2     ,fields="CD1_1",delete=yes)
#hedit(image=obj_lamp_name,fields="CD2_2",delete=yes)
#hedit(image=tmp_cr_1     ,fields="CD2_2",delete=yes)
#hedit(image=tmp_cr_2     ,fields="CD2_2",delete=yes)
#hedit(image=obj_lamp_name,fields="CD2_3",delete=yes)
#hedit(image=tmp_cr_1     ,fields="CD2_3",delete=yes)
#hedit(image=tmp_cr_2     ,fields="CD2_3",delete=yes)


apall(input=tmp_cr_1,output=tmp_ap_1,format="multispec",referen="",interac=yes,find=yes,recente=yes,resize=yes,edit=yes,trace=yes,fittrac=yes,extract=yes,extras=yes,review=yes,llimit=ap1,ulimit=ap2,t_funct="spline3",t_order=4,backgro="fit",weights="variance",pfit="fit2d")
print("**********************************************")
print("Apall object lamp spectrum")

del fear01.0001.fits

#apall(input="202101310012_SPECLWLLIGHT_Fear_slit2.3_385LP_G4.fit",output="fear01",format="onedspec",referen="CMR_SN2020adow.fits",trace=no,extract=yes,find=no,recente=no,resize=no,edit=no,trace=no,fittrac=no,extract=yes,extras=no,review=yes,llimit=1,ulimit=1,t_funct="spline3",t_order=5,backgro="none",weights="none",pfit="fit2d")

apall(input=obj_lamp_name,output="fear01",format="onedspec",referen=tmp_cr_1,interac=no,find=no,recente=no,resize=no,edit=no,trace=no,fittrac=no,extract=yes,extras=no,review=yes,llimit=ap1,ulimit=ap2,t_funct="spline3",t_order=5,backgro="none",weights="none",pfit="fit2d")


#hedit(image="fear01.0001",fields="CTYPE1",  value="PIXEL")
#hedit(image="fear01.0001",fields="WAT1_001",value="wtype=linear label=Pixel")

print("**********************************************")
print("Apall std spectrum")


tmp_ap_2="ap_"+star_name +".ms.fits"
delete(files=tmp_ap_2)


apall(input=tmp_cr_2,output=tmp_ap_2,format="multispec",referen="",interac=yes,find=yes,recente=yes,resize=yes,edit=yes,trace=yes,fittrac=yes,extras=yes,review=yes,llimit=ap1,ulimit=ap2,t_funct="spline3",t_order=5,backgro="fit",weights="variance",pfit="fit2d")


print("**********************************************")
print("Wavelength identify")

del fear01.0002.fits

imfunction(input='fear01.0001',output='fear01.0002',function='log10')
identify(images="fear01.0002",coordli="linelists$fear.dat",functio="spline3",order=1)

refspectra(input=tmp_ap_1,referen="fear01.0002.fits",sort="",group="",answer=yes)
refspectra(input=tmp_ap_2,referen="fear01.0002.fits",sort="",group="",answer=yes)

imdelet(image="dispcor_"+output_file +".fits")
imdelet(image="dispcor_"+star_name   +".fits")
dispcor(input=tmp_ap_1,output="dispcor_"+output_file)
dispcor(input=tmp_ap_2,output="dispcor_"+star_name  )

del std
standard(input="dispcor_"+star_name,output="std",bandwid=50.,bandsep=50.,caldir=cal_dir,star_nam=star_name,observatory="bao",extinction=extin_file)

del sens.fits
del sens.0001.fits
sensfunc(standards="std",sensitivity="sens",observatory="bao",extinction=extin_file,functio="spline3",order=20)

imdelet(image="cali_"+output_file +".fits")
calibrate(input="dispcor_"+output_file,output="cali_"+output_file,extinction=extin_file,sensitivity="sens",extinct=yes,observatory="bao",flux=yes)

scopy(input="cali_"+output_file,output=output_file,format="onedspec",clobber=yes)

# Removing the atomospheric absorptions

del standard_c.fits


del standard_c
calibrate(input="dispcor_"+star_name,output="standard_c",extinction=extin_file,sensitivity="sens",extinct=yes,observatory="bao",flux=yes)

del starabs.fits

continuum(input="standard_c",output="starabs",functio="spline3",order=20,overrid=yes,type="ratio")

del atom.0001.fits
del ATOM.fits
del(files=output_file+".fits")
scopy(input="starabs",output="atom",bands=1,format="onedspec",clobber=yes)
imcopy(input="atom.0001.fits[1050:1640]",output="ATOM.fits")
realoutputfile=output_file+"_bfosc_"+substr(obj_filename,1,8)
imdelete(image=realoutputfile+".fits")


del temp_telluric_1.fits
del temp_telluric_2.fits
del temp_telluric_3.fits
telluric (input=output_file+".0001",     output="temp_telluric_1.fits",cal="atom.0001.fits[1305:1405]",interac=yes)
telluric (input="temp_telluric_1.fits",  output="temp_telluric_2.fits",cal="atom.0001.fits[1020:1160]",interac=yes)
telluric (input="temp_telluric_2.fits",  output="temp_telluric_3.fits",cal="atom.0001.fits[1170:1250]",interac=yes)
telluric (input="temp_telluric_3.fits",  output=realoutputfile        ,cal="atom.0001.fits[1400:1470]",interac=yes)

del atom.dat
del atom_trim.dat
wspectext(input="atom.0001.fits",output="atom.dat",     header=no)
wspectext(input="ATOM.fits",output="atom_trim.dat",header=no)
name1=realoutputfile+".fits"
name2=realoutputfile+".txt"
del name2
wspectext(input=name1,output=name2,header=no)
#imcopy name2 "/home/ysy/data/216/SNID/"+output_file
#!source activate base && python /home/ysy/data/216/SNID/autosnid.py *.txt 
!cp /home/ysy/iraf/pip/216/python_pip/autosnid.py ./
!source activate base && python autosnid.py

end