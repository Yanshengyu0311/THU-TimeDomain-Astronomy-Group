procedure pip()

#------------------------------------------------------------------
string star_name          {prompt="Name of standard star"}
string target_name        {prompt="Target name,such as 2018ilu,not 2018ilu.fits"}
string target_date        {"161126",prompt="Such like 141126"}
string grid               {"G3",prompt="Grid, such as G10,g10"}
string sec_std		  {"",prompt="the second standard star"}
string new_terllu_region  {" ",prompt="[1130:1730]"}
#------------------------------------------------------------------
#以下参数需要修改成你的消光文件和标准星文件的目录
string cal_dir            {"/home/ysy/iraf/all_std/",prompt="Directory of standard stars"}
string extin_file         {"/home/ysy/iraf/all_std/LJextinct.dat",prompt="Extinction file"}
#------------------------------------------------------------------
string linelist           {"hene",prompt="the lamp type in identify"}

begin
#定义一些变量
string tmp,tmp1,tmp2,tmp3,tmp_std_c,tmp_obj_c,obj_filename,std_filename,output_file_name
real   ap1,ap2
string trim_region,region_terlu,tmp_HENE,tmp_obj_t,tmp_std_t,tmp_obj_ap,tmp_std_ap
#不同光栅对应的裁剪范围以及大气吸收范围是不一样的
if	(grid =="g3"||grid=="G3"){
	trim_region ="[500:1600,2230:4120]"
	region_terlu="[1130:1730]"}
else if (grid =="g10"||grid=="G10"){
	trim_region ="[500:1600,2560:3120]"
	region_terlu="[360:559]"}
else if (grid =="g8"||grid=="G8"){
	trim_region ="[500:1600,1270:4130]"
	region_terlu="[725:2050]"}
else if (grid =="g14"||grid=="G14"){
	trim_region ="[500:1600,1890:4100]"
	region_terlu="[1760:2211]"}
else if (grid =="g5"||grid=="G5"){
	trim_region ="[500:1600,2010:3220]"
	region_terlu="[443:897]"}
#if (new_trim_region   !=" "){trim_region =new_trim_region}
if (new_terllu_region !=" "){region_terlu=new_terllu_region}
#初始化iraf一些参数
noao
twodspec
apextract.dispaxis=0.9
noao.twodspec
longslit 
longslit.dispaxis=2
observatory(command="list",obsid="lijiang")

#
obj_filename="TARGET.fits"
std_filename="STD1.fits"
#Cosmicrays removing
print("**********************************************")
print("Romoving the cosmicrays")


tmp_obj_c="TARGET_c.fits"
tmp_std_c="STD1_c.fits"

del(files=tmp_obj_c)
del(files=tmp_std_c)
noao
imred
crutil
crmedian(input=obj_filename,output=tmp_obj_c)
crmedian(input=std_filename,output=tmp_std_c)
#---------------------------------------------------------------------------------------------------------
#波长定标
print("**********************************************")
print("Wavelength identify")

tmp_HENE="HENE"
tmp_obj_t="TARGET_t.fits"
tmp_std_t="STD1_t.fits"
del (files="hene.fits")
imcopy(input="HENE.fits[0]",output="hene")
del (files="HENE.fits")
imcopy(input="hene[0]",output="HENE")
del (files="hene.fits")
identify(images="HENE",coordli="linelists$"+linelist+".dat",functio="spline3",order=2,fwidth=8.,cradius= 8., thresho= 3., minsep = 6.,section="column 500")
del(files=tmp_obj_t)
del(files=tmp_std_t)
#修正灯谱的畸变
reidentify(reference="HENE",images="HENE",interac=yes,section="column 500",newaps=yes,step=50,nsum=10,coordli="linelists$"+linelist+".dat",answer=YES,mode="al")
fitcoords(images="HENE",fitname="HENE",interac=yes)



#将源和标准星畸变修正过来

transform (input="HENE",   output="HENE_t", fitnames="HENEHENE")
transform (input=tmp_obj_c,output=tmp_obj_t,fitnames="HENEHENE")
transform (input=tmp_std_c,output=tmp_std_t,fitnames="HENEHENE")
#查看吧畸变修正过后的灯谱

#抽取标准星光谱
print("**********************************************")
print("Apall object spectrum")
#imexamine(input="TARGET")

tmp_obj_ap="apTARGET"
del(files="apTARGET.0001.fits")
del(files=  "apSTD1.0001.fits")

apall(input=tmp_obj_t,output="apTARGET",format="onedspec",referen="",interac=yes,find=yes,recente=yes,resize=yes,edit=yes,trace=yes,fittrac=yes,extract=yes,extras=yes,review=yes,llimit=INDEF,ulimit=INDEF,t_funct="spline3",t_order=3,backgro="fit",weights="variance",pfit="fit1d")

apall(input=tmp_std_t,output="apSTD1",format="onedspec",referen="",interac=yes,find=yes,recente=yes,resize=yes,edit=yes,trace=yes,fittrac=yes,extract=yes,extras=yes,review=yes,llimit=INDEF,ulimit=INDEF,t_funct="spline3",t_order=3,backgro="fit",weights="variance",pfit="fit1d")

#---------------------------------------两条标准星操作

if (sec_std!=""){
print("The second spectral")
del(files="STD2_c.fits")
del(files="STD2_t.fits")
del(files="apSTD2.0001.fits")
del(files="std")
#---------------------------------------以下是第二条标准星操作去宇宙线/抽谱等操作
crmedian(input="STD2.fits",output="STD2_c.fits")
transform (input="STD2_c.fits",output="STD2_t.fits",fitnames=tmp_HENE+tmp_HENE)
apall(input="STD2_t",output="apSTD2",format="onedspec",referen="",interac=yes,find=yes,recente=yes,resize=yes,edit=yes,trace=yes,fittrac=yes,extract=yes,extras=yes,review=yes,llimit=INDEF,ulimit=INDEF,t_funct="spline3",t_order=3,backgro="fit",weights="variance",pfit="fit1d")
standard(input="apSTD1.0001.fits",output="std",caldir=cal_dir,star_nam=star_name,observatory="lijiang",extinction=extin_file,answer=yes)
standard(input="apSTD2.0001.fits",output="std",caldir=cal_dir,star_nam=sec_std  ,observatory="lijiang",extinction=extin_file,answer=yes)
}
#observatory数据在obsdb.dat,尝试这这样用：observatory(obsid="lijiang")等参数
#---------------------------------------一条标准星操作
if (sec_std==""){
del(files="std")
standard(input="apSTD1.0001.fits",output="std",caldir=cal_dir,star_nam=star_name,observatory="lijiang",extinction=extin_file,answer=yes)
}
#---------------------------------------相应曲线
del sensLJT.0001.fits
del sensLJT.fits
del cailTARGET.fits
del cailSTD.fits
sensfunc(standards="std",sensitivity="sensLJT",extinction=extin_file,observatory="lijiang",functio="spline3",order=10)
calibrate(input="apTARGET.0001.fits",output="cailTARGET",extinction=extin_file,observatory="lijiang",sensitivity="sensLJT",extinct=yes,flux=yes)
calibrate(input=  "apSTD1.0001.fits",output="cailSTD",   extinction=extin_file,observatory="lijiang",sensitivity="sensLJT",extinct=yes,flux=yes)

###大气吸收线
del sF.fits
del tF.fits
del tTARGET.fits
del terTARGET.fits
imcopy(input="cailSTD.fits"+region_terlu,output="sF")
continuum (input="sF",output="tF",functio="spline3",order=3,overrid=yes,type="ratio")
telluric (input="cailTARGET", output="terTARGET",cal="tF",interac=yes)

##储存文件成TXT
del U.0001.fits
del U.1001.fits
del U.2001.fits
del U.3001.fits
scopy(input="terTARGET", output="U",        format="onedspec",clobber=yes)
scopy(input="cailTARGET",output="U_no_atom",format="onedspec",clobber=yes)
output_file_name=target_name+"_"+target_date+"_LJT_"+grid
imdelete(images=output_file_name+".fits")
imcopy(input="U.0001.fits",output=output_file_name)
wspectext(input="U.0001.fits",output=output_file_name+".dat",header=no)
wspectext(input="tF",         output="atom.dat",      header=no)
wspectext(input="U_no_atom.0001.fits", output=output_file_name+"_no_atom.dat",header=no)
#加检查步骤
end
