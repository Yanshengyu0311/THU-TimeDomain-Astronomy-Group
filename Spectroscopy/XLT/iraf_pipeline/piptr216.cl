procedure pip()
string target_name        {prompt="Target name,such as SN2018ilu,not SN2018ilu.fits"}
string target_date        {"20201126",prompt="Such like 20201126"}
string std_ter            {"yes",prompt="Whther use standard terlluric file"}
string segmentation       {"no",prompt="Whther split into several segmentation"}
string faketelluric       {"no",prompt="Whther use fake telluric"}

begin
string fail_ter_fits,name1,name2
del atom.fits
del ATOM.fits
fail_ter_fits=target_name+"_bfosc_"+target_date
del(files=fail_ter_fits+".fits")
imdelet(images="ter_new_"+target_name)
scopy(input="starabs",output="atom",bands=1,format="onedspec",clobber=yes)
imcopy(input="atom.0001.fits[1160:1640]",output="ATOM.fits")
if (faketelluric=="yes"){
del fake_terlluric_temp.fits
del fake_terlluric.fitsi
imcopy(input=target_name+".0001[1050:1640]",output="fake_terlluric_temp")
continuum(input="fake_terlluric_temp",output="fake_terlluric",functio="spline3",order=6,overrid=yes,type="ratio")
telluric (input=target_name+".0001",output="ter_new_"+target_name,cal="fake_terlluric",interac=yes)
}
else{
imcopy(input=target_name+".0001",output="ter_new_"+target_name)
}
if (std_ter=="yes"){del atom.0001.fits
imcopy(input="/home/ysy/iraf/pip/216/ATOM/atom.0001.fits",output="./atom.0001.fits")}

if (segmentation=="no"){
telluric (input="ter_new_"+target_name, output=fail_ter_fits,cal="ATOM",interac=yes)
}
else {
del temp_telluric_1.fits
del temp_telluric_2.fits
del temp_telluric_3.fits
del temp_telluric_4.fits
#telluric (input=target_name+".0001",    output="temp_telluric_1.fits",cal="atom.0001.fits[1072:1134]",interac=yes)
#telluric (input="temp_telluric_1.fits", output="temp_telluric_2.fits",cal="atom.0001.fits[1144:1305]",interac=yes)
#telluric (input="temp_telluric_2.fits", output="temp_telluric_3.fits",cal="atom.0001.fits[1349:1401]",interac=yes)
#telluric (input="temp_telluric_3.fits", output="temp_telluric_4.fits",cal="atom.0001.fits[1317:1349]",interac=yes)
#telluric (input="temp_telluric_4.fits", output=fail_ter_fits,         cal="atom.0001.fits[1511:1672]",interac=yes)

telluric (input="ter_new_"+target_name,     output="temp_telluric_1.fits",cal="atom.0001.fits[1305:1405]",interac=yes)
telluric (input="temp_telluric_1.fits",  output="temp_telluric_2.fits",cal="atom.0001.fits[1020:1160]",interac=yes)
telluric (input="temp_telluric_2.fits",  output="temp_telluric_3.fits",cal="atom.0001.fits[1170:1250]",interac=yes)
telluric (input="temp_telluric_3.fits",  output=fail_ter_fits         ,cal="atom.0001.fits[1400:1470]",interac=yes)
}



del atom.dat
del atom_trim.dat
wspectext(input="atom.0001.fits",output="atom.dat",     header=no)
wspectext(input="ATOM.fits",     output="atom_trim.dat",header=no)
name1=fail_ter_fits+".fits"
name2=fail_ter_fits+".txt"
del name2
wspectext(input=name1,output=name2,header=no)
#imcopy name2 "/home/ysy/data/216/SNID/"+output_file
!cp /home/ysy/data/216/autosnid.py ./
!source activate base && python autosnid.py
end

