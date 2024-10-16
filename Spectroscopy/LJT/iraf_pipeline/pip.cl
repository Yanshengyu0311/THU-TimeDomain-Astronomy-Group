#云南丽江2.4m望远镜pipeline
procedure pip()

begin
#调用
longslit
ccdred

#!ds9 -zscale Y* &

#检查图像

#合并本底

zerocombine(input="./bias/Y*[1]",output="Zero")

#imcopy (input="Zero.fits",output="./bias/Zero")
#imdel (images="./bias/Y*")

#zerocombine(input="@zero",output="Zero")

#将本底文件复制到平场下
#imutil
#imcopy(input="Zero",output="./flat/Zero")


#平场减本底
#G3
ccdproc(images="./flat/Y*[1]",   output="./flat/Y*//tz",biassec="[10:40,*]",trimsec="[500:1600,2230:4120]",flatcor=no,darkcor=no,zerocor=yes,trim=yes,)
#G10
#2560:3220
#G8
#1270:4130
#G14
#1890:4100
#G5
#2010:3220
#ccdproc(images="./flat/Y*[1]",   output="./flat/Y*//tz",biassec="[10:40,*]",trimsec="[500:1600,a]",flatcor=no,darkcor=no,zerocor=yes,trim=yes,)



ccdred
#合并平场
#flatcombine(input="./flat/@./flat/l2//tz",output="./flat/Flat")
flatcombine(input="./flat/Y*tz.fits",output="./flat/Flat")


#平场归一化（色散方向）
response(calibrat="./flat/Flat",normaliz="./flat/Flat",response="./flat/reFlat",interac=yes)

#平场归一化（空间方向）
illumination(images="./flat/reFlat",illumina="./flat/ilFlat",interac=no)
imarith (operand1="./flat/reFlat.fits", op="/",operand2="./flat/ilFlat.fits",result="perFlat")

#除平场 并裁剪图像
#imhead Y*[1] >l1
!gedit l1 l2
#G3
ccdproc(images="@l1",output="@l2",trim=yes,zerocor=yes,flatcor=yes,biassec="[10:40,*]",trimsec= "[500:1600,2230:4120]",zero="Zero",flat="perFlat") 
#G10
#2560:3220
#G8
#1270:4130
#G14
#1890:4100
#G5
#2010:3220
#ccdproc(images="@l1",output="@l2",trim=yes,zerocor=yes,flatcor=yes,biassec="[10:40,*]",trimsec= "[500:1600,]",zero="Zero",flat="perFlat")

#去宇宙线
crmedian(input="TARGET",output="TARGETc")
crmedian(input="STD",output="STDc")
#crmedian(input="STD1",output="STD1c")
#波长定标
identify(images="HENE")

#修正灯谱的畸变
reidentify(reference="HENE",images="HENE",interac=yes)
fitcoords(images="HENE",fitname="HENE",interac=yes)

#查看吧畸变修正过后的灯谱
display HENE

#将源和标准星畸变修正过来
transform (input="HENE",output="HENEt",fitnames="HENEHENE")
display HENEt
transform (input="TARGETc",output="TARGETt",fitnames="HENEHENE")
transform (input="STDc"  ,output="STDt"  ,fitnames="HENEHENE")

#抽谱看孔径
!ds9 STD &
imexam #vv(vector) or c(column)
#源谱
apall(input="TARGETt",output="apTARGET",interac=yes)

#标准星谱
apall(input="STDt",output="apSTD",interac=yes)

#去大气吸收线 6670A-8380A
#G3
imcopy(input="apSTD.0001.fits[1130:1730]",output="sF")
#G8
#imcopy(input="apSTD.0001.fits[925:2050]",output="sF")
#G14
#imcopy(input="apSTD.0001.fits[1760:2211]",output="sF")
#G10
#imcopy(input="apSTD.0001.fits[360:587]",output="sF")
#G5
#imcopy(input="apSTD.0001.fits[443:897]",output="sF")

continuum (input="sF",output="tF")
telluric (input="apTARGET.0001", output="tTARGET",cal="tF",interac=yes)

#流量定标，由于需要输入Airmass和exposure time，所以需要一下两步
#ehead STD

#standard(airmass=1.08,exptime=180,star_nam="mfeige25")
standard
#生成响应曲线
sensfunc (standard="std",sensitiv="sensLJT")

#目标源流量定标
calibrate(input="tTARGET",output="caliTARGET")

#输出文件为TXT格式
scopy(input="caliTARGET",output="U")
#caliTARGET[*,1,1](1) --> U.0001(1)
#caliTARGET[*,1,2](1) --> U.1001(1)
#caliTARGET[*,1,3](1) --> U.2001(1)
#caliTARGET[*,1,4](1) --> U.3001(1)
wspectext(input ="U.0001.fits",output="spec.dat")
splot U.0001.fits
#修改文件名
print("rename the data flie as the 2018ilu_181201_LJT_G3")
end
