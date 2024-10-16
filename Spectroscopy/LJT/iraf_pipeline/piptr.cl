procedure pip()
string target_name        {prompt="Target name,such as 2018ilu,not 2018ilu.fits"}
string target_date        {"161126",prompt="Such like 141126"}
string grid               {"G3",prompt="Grid, such as G10,g10"}
string std_ter            {prompt="Whther use standard terlluric file"}
begin
string output_file_name

###大气吸收线
del terTARGET.fits
if (std_ter=="no"){
telluric (input="cailTARGET", output="terTARGET",cal="tF",interac=yes)
}
else {
del TF.fits
del ter_temp_1.fits
del ter_temp_2.fits
del ter_temp_3.fits
imcopy(input="/home/ysy/iraf/pip/240/LJT_telluric/Tellu25.fits",output="TF.fits")
telluric (input="cailTARGET", output="ter_temp_1",cal="TF.fits[529:587]",interac=yes)
telluric (input="ter_temp_1", output="ter_temp_2",cal="TF.fits[370:492]",interac=yes)
telluric (input="ter_temp_2", output="ter_temp_3",cal="TF.fits[272:370]",interac=yes)
telluric (input="ter_temp_3", output="terTARGET" ,cal="TF.fits[603:830]",interac=yes)
}
##储存文件成TXT
del U.0001.fits
del U.0002.fits
del U.0003.fits
del U.0004.fits
scopy(input="terTARGET", output="U",        format="onedspec",clobber=yes)
scopy(input="cailTARGET",output="U_no_atom",format="onedspec",clobber=yes)
output_file_name=target_name+"_"+target_date+"_LJT_"+grid
imdelete(images=output_file_name+".fits")
imcopy(input="U.0001.fits",output=output_file_name)
wspectext(input="U.0001.fits",output=output_file_name+".dat",header=no)
wspectext(input="tF",         output="atom.dat",      header=no)
wspectext(input="U_no_atom.0001.fits", output=output_file_name+"_no_atom.dat",header=no)
# telluric cailTARGET.fits  cailTARGET1.fits tF.fits[1:153]
# telluric cailTARGET1.fits cailTARGET2.fits tF.fits[153:262]
# telluric cailTARGET2.fits cailTARGET3.fits tF.fits[262:601]
end
