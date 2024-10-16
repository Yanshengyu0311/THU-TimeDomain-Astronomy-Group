procedure pip()

string   grid               {"G3",prompt="Grid, such as G10,g10"}
real     readnoise          {6.5,prompt="Readnoise,6.5"}
real     gain               {0.34,prompt="Gain,0.34"}
string   new_trim_region    {" ",prompt="new trim region,such as [500:1600,2230:4120]"}
#string   new_terllu_region  {" ",prompt="[1130:1730]"}

begin
#调用
string trim_region,region_terlu
noao
twodspec
longslit
longslit.dispaxis=2
noao
imred
ccdred
#定义变量
#不同光栅的裁剪范围以及大气吸收范围
if	(grid =="g3"||grid=="G3"){
	#trim_region ="[500:1600,2500:4120]"
        trim_region ="[500:1600,2230:4120]"
	region_terlu="[1130:1730]"}
else if (grid =="g10"||grid=="G10"){
 	#trim_region ="[500:1600,2050:2500]"
        #region_terlu="[320:519]"} 
        trim_region ="[500:1600,2560:3120]"
	region_terlu="[360:559]"}
else if (grid =="g8"||grid=="G8"){
	trim_region ="[500:1600,1270:4130]"
	region_terlu="[925:2050]"}
else if (grid =="g14"||grid=="G14"){
	trim_region ="[500:1600,1890:4100]"
	region_terlu="[1760:2211]"}
else if (grid =="g5"||grid=="G5"){
	trim_region ="[500:1600,2010:3020]"
	region_terlu="[443:897]"}
if (new_trim_region   !=" "){trim_region =new_trim_region}
#if (new_terllu_region !=" "){region_terlu=new_terllu_region}
###########################################################################################################################################
#合并本底
print("**********************************************")
print("Zero combine ,trim and correction and overscan")
if (access("./bias/Zero.fits")){
language
clpackage
system
del(files="Zero.fits") 
imcopy (input="./bias/Zero.fits",output="Zero.fits")}
else
{
zerocombine(input="./bias/Y*[1]",output="Zero",ccdtype="",combine="average",reject="minmax",rdnoise=readnoise,gain=gain)
imcopy (input="Zero.fits",output="./bias/Zero")#将本底文件复制bias下，
}
#为了节省电脑储存空间，把Zero放在bias，原来bias文件删除
del(files="./bias/Y*")                    #删除本底文件
#图像减bias
del(files="./flat/Y*//tz")
ccdproc(images="./flat/Y*[1]",output="./flat/Y*//tz",ccdtype="",fixpix=no,oversca=yes,biassec="[10:40,*]",trimsec=trim_region,flatcor=no,darkcor=no,zero="Zero",zerocor=yes,trim=yes)
###########################################################################################################################################
#图像除平场
print("**********************************************")
print("Flat combine normalize and correction")
del(files="./flat/Flat.fits")
del(files="./flat/reFlat.fits")
del(files="./flat/ilFlat.fits")
del(files="perFlat.fits")
#平场合并
flatcombine(input="./flat/Y*tz.fits",output="./flat/Flat",ccdtype='',combine="median",reject="avsigclip",process=no,scale="mode",rdnoise=readnoise,gain=gain)
noao
twodspec
longslit
#平场归一化（色散方向）
response(calibrat="./flat/Flat",normaliz="./flat/Flat",response="./flat/reFlat",interac=yes,functio="spline3",order=15)

#平场归一化（空间方向）
illumination(images="./flat/reFlat",illumina="./flat/ilFlat",interac=no,nbins=10,functio="spline3",order=12)
imarith (operand1="./flat/reFlat.fits", op="/",operand2="./flat/ilFlat.fits",result="perFlat")
del(files="@l2//.fits")
del(files="STD1")
del(files="TARGET")
del(files="HENE") 

#图像除平场
ccdproc(images="@l1",output="@l2",ccdtype='',fixpix=no,oversca=yes,trim=yes,zerocor=yes,darkcor=no,flatcor=yes,biassec="[10:40,*]",trimsec=trim_region,zero="Zero",flat="perFlat")
#############################################################################################################################################

print("All standard star name:")
print("Zet17Cas feige98LJT      hz44         hr9087    ltt9491  grw70d5824")
print("wolf485  feige98         hz43         hr8634    ltt9239  gd71")
print("wolf1346 feige92         hz43         hr7950    ltt7987  gd71")
print("sp2341   feige67         hz4          hr7596    ltt745   gd50")
print("sp2032   feige66         hz4          hr718     ltt7379  gd248")
print("sa95_42  feige56         hz21         hr5501    ltt6248  gd153")
print("s108     feige34         hz2          hr4963    ltt4816  gd108")
print("rvs404   feige34         hz15LJT      hr4468    ltt4364  g9348")
print("rvf404   feige25         hz15         hr3454    ltt3864  g93_48")
print("refYZN   feige15_LJT     bd75d325     hr3454    ltt3218  g60_54")
print("RefYZ    feige15         bd40d4032    hr1544    ltt2415  g24_9")
print("Ref_YZN  feige110_lowres bd33d2642    cd32d9927 ltt1788  g193_74")
print("ngd71    feige110        bd28d4211    cd32d9927 ltt1020  g191b2b")
print("ngc7293  feige110        bd25d4655    cd_32d241 pg1708   g163d51")
print("l1512    feige11         bd25d3941    hd93521   pg1708   g163_51")
print("kopff27  eg274           bd17d4708    hd84937   pg1545   g158_100")
print("hilt600  eg21            bd08d2015LJT hd19445   PG0823   g138_31")
print("hilt102  fagk_81d266_005 bd08d2015    he3")
#imheader(images="TARGET")
end
