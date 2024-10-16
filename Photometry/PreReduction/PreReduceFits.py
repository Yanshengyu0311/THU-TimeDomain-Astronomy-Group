#!/home/ysy/anaconda3/envs/iraf27/bin/python2.7
# encoding: utf-8

# 思路：
# 最高权限先指定bias、flat、dark、target
# 如果没指定，就寻找bias.list、flat.list之列的文件
# 最后再自动分。
#TODO 换一个望远镜的fits文件试一试
# from random import choices
# from email.mime import image
from email.mime import image
from enum import unique
import numpy as np
import os
import optparse
import sys
from astropy.io import fits

def remove_space_in_header_value(header):
    # 去除header中每个item的value中的空格
    for i in header:
        if type(header[i])== str: 
            if " " in header[i]:
                header[i]=header[i].replace(" ","")
    return header

def check_header(fitsname):
    # telescope and instrument name

    header_test=fits.getheader(fitsname)
    header_test=remove_space_in_header_value(header_test)

    if "TELESCOP" in header_test.keys():
        telescop= header_test["TELESCOP"]
    else:
        print("can't find header Key: INSTRUME")


    if "INSTRUME" in header_test.keys():
        instrume= header_test["INSTRUME"]
    else:
        print("can't find header Key: INSTRUME")
    return telescop,instrume

def find_list(list_arg):
    import glob
    files = glob.glob(os.path.join(cwd,list_arg))
    list_select=[os.path.abspath(i) for i in files if os.path.exists(i)] 
    return list_select

# 最高权限先指定bias、flat、dark、target
reload(sys)
sys.setdefaultencoding('utf-8')
parser = optparse.OptionParser()

CurrentPath = os.getcwd()
ScriptPath  = sys.path[0]

parser.add_option('--bias',"--Bias","-b","-B", 
                dest='bias',
                default="bias.list",
                # choices=bias_choices,
                help='The specific bias list contains all bias frame, Example:bias.list(defualt). 如果用通配符* ， 前面加上@，比如：@*bias.fits',
                nargs=1) 

parser.add_option('--dark',"--dark","-d","-D", 
                dest='dark',
                default="dark.list",
                help='The specific flat list contains all dark frame, Example:dark.list(defualt). 如果用通配符* ， 前面加上@，比如：@*dark.fits') 

parser.add_option('--flat',"--Flat","-f","-F", 
                dest='flat',
                default="flat.list",
                help='The specific flat list contains all flat frame, Example:flat.list(defualt). 如果用通配符* ， 前面加上@，比如：@*flat.fits') 

parser.add_option('--target',"--Target","-t","-T", 
                dest='target',
                default="target.list",
                help='The specific flat list contains all target frame, Example:target.list(defualt). 如果用通配符* ， 前面加上@，比如：@*target.fits') 

opt,args = parser.parse_args()
bias_list  = opt.bias
dark_list  = opt.dark
flat_list  = opt.flat
target_list= args


bias_input0=[]
flat_input0=[]
dark_input0=[]
flat_input0=[]

#####################
file_all=os.listdir("./")
cwd=os.path.abspath("./")
#####################


#####################################################################
# 删除之前预处理的文件
#####################################################################
Old_Zero_Correction_file=[i for i in file_all if "_zcor.fits" in i]
if any(Old_Zero_Correction_file):
    for i in Old_Zero_Correction_file:
        if os.path.exists(i):os.remove(i)

# Old_PreCor_fits=[i for i in file_all if "_PreCor.fits" in i]
# if any(Old_PreCor_fits):
#     for i in Old_PreCor_fits:
#         if os.path.exists(i):os.remove(i)

target_list=list(filter(lambda x: "_PreCor.fits" not in x,target_list))
#####################################################################

file_all=os.listdir("./")

telescop,instrume=check_header(target_list[0])

# load the yml
import yaml
telescope_yml_path=os.path.join(ScriptPath,"telescope_Pre.yaml") 
Key_all=yaml.load(open(telescope_yml_path,"r").read())
Keys=Key_all[telescop][instrume]

if "pre_cmd"  in Keys:
    for c in Keys["pre_cmd"]:
        os.system(c)
if "layer" in Keys.keys():
    layer="["+str(Keys["layer"])+"]"
else:
    layer=""

# 确定需要哪些操作
# 替换关键字,bias,dark,flat,trim,overscan,badpix
ehead=False
Bias =False
Dark =False
Flat =False
trim =False
fxpix=False
overscan=False

if "replace_key" in Keys.keys():
    ehead=True
    print(Keys["replace_key"]["key"].values(),"will be update")

if "bias_value" in Keys.keys():
    Bias=True
    print("Bias will be subtracted")
    
if "dark_value" in Keys.keys():
    Dark=True
    print("Dark will be subtracted")

if "flat_value" in Keys.keys():
    Flat=True

if "trimsec" in Keys.keys():
    trim=True
    print("The image will be trimed within"+ Keys["trimsec"])

if "fixpix" in Keys.keys():
    fxpix=True
    print("The bad pixel mask is "+ Keys["fixpix"])

if "biassec" in Keys.keys():
    overscan=True
    print ("The overscan region is" + Keys["biassec"] )


# sys.argv 大于等于3，意味着使用了optparse ，从而意味着指定文件了
bias_list_all  =[]
dark_list_all  =[]
flat_list_all  =[]
target_list_all=[]

dark_specific_list=False
flat_specific_list=False
bias_specific_list=False

if len(sys.argv)-len(target_list) >1:

    # bias
    if "@" in bias_list:
        bias_list=bias_list.strip("@")
        bias_input=[bias_list]
        bias_list_all=find_list(bias_list)
        # print()
    else:
        if os.path.exists(bias_list):
            bias_list_all=[i.split("[")[0].strip("\n") for i in open(bias_list).readlines()]
        bias_input=[bias_list]
        
    if Bias and bias_list_all!=[]:print("Bias:[XXX]".replace("XXX",bias_list[0]))
    for i in bias_list_all:print("     "+i)
    if os.path.exists(bias_list):
        bias_list=[bias_list]
        bias_specific_list=True
    else:
        bias_list=[]
        bias_specific_list=False

    # flat
    if "@" in flat_list:
        flat_list=flat_list.strip("@")
        flat_list_all=find_list(flat_list)
        flat_input=[flat_list]
    else:
        if os.path.exists(flat_list):
            flat_list_all=[i.split("[")[0].strip("\n") for i in open(flat_list).readlines()]
        flat_input=[flat_list]
    if Flat and flat_list_all!=[]:print("flat:[XXX]".replace("XXX",flat_list))
    for i in flat_list_all:print("     "+i)
    if os.path.exists(flat_list):
        flat_list=[flat_list]
        flat_specific_list=True
    else:
        flat_list=[]
        flat_specific_list=False

    # dark
    if "@" in dark_list:
        dark_list=dark_list.strip("@")
        dark_list_all=find_list(dark_list)
        dark_input=[dark_list]
    else:
        if os.path.exists(dark_list):
            dark_list_all=[i.split("[")[0].strip("\n") for i in open(dark_list).readlines()]
        dark_input=[dark_list]
    if Dark and dark_list_all!=[]:print("Dark:[XXX]".replace("XXX",dark_list))
    for i in dark_list_all:print("     "+i)
    if os.path.exists(dark_list):
        dark_list=[dark_list]
        dark_specific_list=True
    else:
        dark_list=[]
        dark_specific_list=False
    # # target
    # if "@" in target_list:
    #     target_list=target_list.strip("@")
    #     target_list_all=find_list(target_list,file_all)
    #     target_input=[target_list]
    # else:
    #     if os.path.exists(target_list):
    #         target_list_all=[i.strip("\n") for i in open(target_list).readlines()]
    #     target_input=[target_list]
    # if  target_list_all!=[]:print("target:[XXX]".replace("XXX",target_list))
    # for i in target_list_all:print("     "+i)

    # if Bias and bias_list_all==[]:print("no Bias specificed!")
    # if Flat and flat_list_all==[]:print("no Flat specificed!")
    # if Dark and dark_list_all==[]:print("no Dark specificed!")
    # if        target_list_all==[]:print("no Target specificed!")
        
else:
    # 如果没指定，就寻找bias.XXXXXXXX.list、flat.XXXXXXXX.list之列的文件

    if Dark :
        print("not specific dark list, will try to find dark list file")
        dark_list=list(filter(lambda x:("dark." in x.lower() and (".list" in x or "lst" in x)),file_all))
        for ll in dark_list:
            print("Found dark:[XXX]".replace("XXX",ll))
            ll_all=[i.split("[")[0].strip("\n") for i in open(ll).readlines()]
            for i in ll_all:print("           "+i)

    if Bias :
        print("not specific bias list, will try to find bias list file")
        bias_list=list(filter(lambda x:(("bias." in x.lower() or "bais." in x.lower()) and (".list" in x or "lst" in x)),file_all))
        for ll in bias_list:
            print("Found Bias:[XXX]".replace("XXX",ll))
            ll_all=[i.split("[")[0].strip("\n") for i in open(ll).readlines()]
            for i in ll_all:print("           "+i)
        

    if Flat :
        print("not specific flat list, will try to find flat list file")
        flat_list=list(filter(lambda x:("flat." in x.lower() and (".list" in x or "lst" in x)),file_all))
        for ll in flat_list:
            print("Found Flat:[XXX]".replace("XXX",ll))
            ll_all=[i.split("[")[0].strip("\n") for i in open(ll).readlines()]
            for i in ll_all:print("           "+i)

    # # target
    # if target_list=="target.list" and os.path.exists("target.list"):
    #     print("Flat:[target.list]")
    # else:
    #     print("No target list,  will try to find target file")
    #     target_list=list(filter(lambda x:("target." in x.lower() and (".list" in x or "lst" in x)),file_all))
    #     for ll in target_list:
    #         print("Found target:[XXX]".replace("XXX",ll))
    #         target_list_all=[i.strip("\n") for i in open(ll).readlines()]
    #         for i in target_list_all:print("           "+i)

    # 依据头文件中的 波段 时间 文件种类 进行划分

suffix={"fits":0,"fit":0,"fts":0}
# if dark_list_all==[] or flat_list_all ==[] or bias_list_all==[]:
if True:
    # 找出来图的后缀，统计所有后缀，后缀多的作为最终后缀
    
    for f in file_all:
        file_suffix=f.split(".")[-1]
        if file_suffix in suffix.keys():
            suffix[file_suffix] += 1
    for i in suffix.keys():
        if suffix[i] ==max(suffix.values()):
            img_suffix=i
    print("image suffix is "+img_suffix)
    
    # 找到和上面后缀一样的文件
    img_all=[i for i in file_all if i.split(".")[-1]==img_suffix]
    img_all.extend(bias_list_all)
    img_all.extend(flat_list_all)
    img_all.extend(dark_list_all)


    # 读取时间
    from astropy.io import fits
    from astropy.time import Time
    img_mjd={}
    print("---------------------------------------")
    print("All Image:")
    for i in img_all:
        # file_type
        print(i)
        fits_header=fits.getheader(i)
        fits_header=remove_space_in_header_value(fits_header)
        date=fits_header[Keys["date_key"]]
        mjd=np.floor(Time(date,format=Keys["date_key_type"]).mjd)
        mjd=Time(date,format=Keys["date_key_type"]).mjd
        # Filter=Keys[fits_header[Keys["filter_key"]]]
        img_mjd[os.path.basename(i)]=mjd

    # print(img_mjd)
    print("---------------------------------------")
    print("Date observed:")
    for i in img_mjd: print("%s: %s"%(i,Time(img_mjd[i],format="mjd").isot))
    # 依据key word 做分类
    file_type={}

    for i in img_all:
        # file_type
        is_target=True
        fits_header=fits.getheader(i)
        fits_header=remove_space_in_header_value(fits_header)

        if Bias:
            if Keys["bias_value"] == fits_header[Keys["object_key"]]:
                file_type[i]="bias"
                is_target=False
                if i not in bias_list_all:
                    bias_list_all.append(i)
                continue
        if Flat:
            if Keys["flat_value"] == fits_header[Keys["object_key"]]:
                file_type[i]="flat"
                is_target=False
                if i not in flat_list_all:
                    flat_list_all.append(i)
                continue
        if Dark:
            if Keys["dark_value"] == fits_header[Keys["object_key"]]:
                file_type[i]="dark"
                is_target=False
                if i not in dark_list_all:
                    dark_list_all.append(i)
                continue
        target_list_all.append(i)
        if is_target:
            file_type[i]="target"

    # for i in file_type:
    #     print(i,file_type[i], fits.getheader(i)[Keys["object_key"]])

    time_interval=0.4999999
    # TODO 不用写成一个txt文件然后，然后再@bias.list了。可以用python list加入进去


    # 每一种类型（bias,dark）可能拍摄时间不同，对时间进行分类，并写文件。

    if Dark and dark_list_all:
        dark_mjd =np.array([img_mjd[i] for i in dark_list_all])
        dark_MJD =np.unique(np.around(dark_mjd))

        dark_list_mjd={}
        for mm in dark_MJD:
            list_name="dark."+((Time(mm,format="mjd").iso).split()[0]).replace('-',"")+".list"
            if list_name not in dark_list:dark_list.append(list_name)
            with open(list_name,"w") as dark_list_file:
                for ii in dark_list_all:
                    if np.abs(mm-img_mjd[ii])<time_interval:
                        dark_list_file.write(ii+layer+"\n")     
                print(list_name+" was writen in "+cwd)      
    else:
        print("no dark file found")


    if Bias and bias_list_all:
        bias_mjd =np.array([img_mjd[i] for i in bias_list_all])
        bias_MJD =np.unique(np.around(bias_mjd))
        bias_list_mjd={}
        for mm in bias_MJD:
            list_name="bias."+((Time(mm,format="mjd").iso).split()[0]).replace('-',"")+".list"
            if list_name not in bias_list:bias_list.append(list_name)
            with open(list_name,"w") as bias_list_file:
                for ii in bias_list_all:
                    if np.abs(mm-img_mjd[ii])<time_interval:
                        bias_list_file.write(ii+layer+"\n")
                print(list_name+" was writen in "+cwd)
                
    else:
            print("no bias file found")



    # 因为flat有滤光片，所以分波段，份时间，然后将列表写入文件
    # 所有用滤光片拍摄的image
    img_wth_filter=flat_list_all[:]
    img_wth_filter.extend(target_list_all)

    # image的filter的信息
    img_filter={}

    for i in img_wth_filter:
        try:
            fits_header=fits.getheader(i)
            fits_header=remove_space_in_header_value(fits_header)
            Filter=Keys[fits_header[Keys["filter_key"]]]
            img_filter[os.path.basename(i)]=Filter
        except:
            pass
        # print(i,img_mjd[i],Filter)

    # 根据header的信息，不一定是常规的滤光片
    filter_unusal=[]
    # 所有收集到的文件中有过滤光片的文件中，一句header 中的key word 找到的源
    Filter_type_using=list(set(img_filter.values()))
    # 所有文件中，常见的滤光片。
    Filter_all =[]

    for i in Filter_type_using:
        if i in Keys.values():
            Filter_all.append(i)
        else:
            filter_unusal.append(i)
            print("filter key word "+i+" is unusual,please check the config file")
# if flat_list_all ==[]:
    # 依据时间 和滤光片写list
    if Flat and flat_list_all:
        flat_mjd =np.array([img_mjd[os.path.basename(i)] for i in flat_list_all])
        flat_MJD =np.unique(np.around(flat_mjd))
        flat_list_mjd={}
        for f in Filter_all:
            flat_list_tmp={}
            for mm in flat_MJD:
                list_name="flat."+f+"."+((Time(mm,format="mjd").iso).split()[0]).replace('-',"")+".list"
                flat_list_tmp[list_name]=[]
                for ii in flat_list_all:
                    if np.abs(mm-img_mjd[os.path.basename(ii)])<time_interval and img_filter[os.path.basename(ii)] == f:
                        flat_list_tmp[list_name].append(ii+layer+"\n")
                if any(flat_list_tmp[list_name]):
                    if list_name not in flat_list: flat_list.append(list_name)
                    with open(list_name,"w") as flat_list_file:
                        for nn in flat_list_tmp[list_name]:
                            flat_list_file.write(nn) 
                    print(list_name+" was writen in "+cwd)

    else:
        print("no flat file found")

# print(target_list)
# print(bias_list)
# print(flat_list)


def check_remove(file_list):
    suffix_fits=list(suffix.keys())
    if type(file_list)==type(str()):
        if file_list[0]=="@":
            check_file=open(file_list.strip("@"),"r").readlines()
            for cf in check_file:
                cf=cf.split("\n")[0]
                cf=cf.split("[" )[0]
                for s in suffix_fits:
                    if os.path.exists(cf+"."+s):
                        os.remove(cf+"."+s)

        else:
            cf=file_list
            cf=cf.split("\n")[0]
            cf=cf.split("[" )[0]
            for s in suffix_fits:
                if os.path.exists(cf+"."+s):
                    os.remove(cf+"."+s)
    if type(file_list)==type(list):
        for f in file_list:
            if os.path.exists(f):
                os.remove(f)


zero_combine_done=False
dark_combine_done=False
flat_combine_done={i: False for i in list(np.unique(img_filter.values()))}
print(flat_combine_done)


for tt in target_list:
    target_filter=img_filter[tt]
    target_mjd   =img_mjd[tt]
    target_output=tt.strip("."+img_suffix)+"_PreCor"
    # target_mjd =np.around(Time(fits.getheader(i)[Keys["date_key"]],format=Keys["date_key_type"]).mjd

    if Bias:
        if bias_specific_list:
            bias_input=bias_list[0]
        else:
            bias_list_time_interval=[]
            for bl in bias_list:
                if len(bl.split("."))==3 and len(bl.split(".")[1])==8:
                    bias_list_date=bl.split(".")[1]
                    bias_list_mjd =Time(bias_list_date[0:4]+"-"+bias_list_date[4:6]+"-"+bias_list_date[6:8]+" 00:00:00.00",format="iso").mjd
                else:
                    # 如果list列表中没有时间，就选择list中第一个fits图查看时间
                    # bias_list_date=(Time(fits.getheader((open(bl,"r").readlines()[0]).split("[")[0].strip("\n"))[Keys["date_key"]],format=Keys["date_key_type"]).iso).split()[0].replace("-","")
                    bias_list_mjd=np.around(img_mjd[(open(bl,"r").readlines()[0]).split("[")[0].strip("\n")])
                bias_list_time_interval.append(bias_list_mjd-target_mjd)
            bias_input=bias_list[bias_list_time_interval.index(min(bias_list_time_interval))]
        print("xxx use Bias:[XXX]".replace("XXX",bias_input).replace("xxx",tt))
        bb_all=[i0.split("[")[0].strip("\n") for i0 in open(bias_input).readlines()]
        for bb in bb_all:print("           "+bb)
        zero_combine_output="zero."+(Time(fits.getheader((open(bias_input,"r").readlines()[0]).split("[")[0].strip("\n"))[Keys["date_key"]],format=Keys["date_key_type"]).iso).split()[0].replace("-","")

    if Dark:
        if dark_specific_list:
            dark_input=dark_list[0]
        else:
            dark_list_time_interval=[]
            for bl in dark_list:
                if len(bl.split("."))==3 and len(bl.split(".")[1])==8:
                    dark_list_date=bl.split(".")[1]
                    dark_list_mjd =Time(dark_list_date[0:4]+"-"+dark_list_date[4:6]+"-"+dark_list_date[6:8]+" 00:00:00.00",format="iso").mjd
                else:
                    # 如果list列表中没有时间，就选择list中第一个fits图查看时间
                    # dark_list_date=(Time(fits.getheader((open(bl,"r").readlines()[0]).split("[")[0].strip("\n"))[Keys["date_key"]],format=Keys["date_key_type"]).iso).split()[0].replace("-","")
                    dark_list_mjd=np.around(img_mjd[(open(bl,"r").readlines()[0]).split("[")[0].strip("\n")])
                dark_list_time_interval.append(dark_list_mjd-target_mjd)
            dark_input=dark_list[dark_list_time_interval.index(min(dark_list_time_interval))]
        print("xxx use Dark:[XXX]".replace("XXX",dark_input).replace("xxx",tt))
        dd_all=[i0.split("[")[0].strip("\n") for i0 in open(dark_input).readlines()]
        for dd in dd_all:print("           "+dd)
        dark_cor_output=dark_input.strip("lst").strip("list").strip("LIST").strip("LST")+"zcor"
        with open(dark_cor_output,"w") as df:
            for iii in open(dark_input,"r").readlines():
                df.write(iii.split("[")[0].strip("\n").strip("."+img_suffix)+"_zcor"+"\n")
        dark_combine_output="dark."+(Time(fits.getheader((open(dark_input,"r").readlines()[0]).split("[")[0].strip("\n"))[Keys["date_key"]],format=Keys["date_key_type"]).iso).split()[0].replace("-","")

    if Flat:

        if flat_specific_list:
            flat_input=flat_list[0]
        else:
            flat_list_time_interval=[]
            
            flat_list_tmp=list(filter(lambda x: target_filter==x.split(".")[1],flat_list))
            for bl in flat_list_tmp:
                if len(bl.split("."))==4 and len(bl.split(".")[2])==8:
                    flat_list_date=bl.split(".")[2]
                    flat_list_mjd =Time(flat_list_date[0:4]+"-"+flat_list_date[4:6]+"-"+flat_list_date[6:8]+" 00:00:00.00",format="iso").mjd
                else:
                    # 如果list列表中没有时间，就选择list中第一个fits图查看时间
                    # flat_list_date=(Time(fits.getheader((open(bl,"r").readlines()[0]).split("[")[0].strip("\n"))[Keys["date_key"]],format=Keys["date_key_type"]).iso).split()[0].replace("-","")
                    flat_list_mjd=np.around(img_mjd[(open(bl,"r").readlines()[0]).split("[")[0].strip("\n")])
                flat_list_time_interval.append(flat_list_mjd-target_mjd)
            flat_input=flat_list_tmp[flat_list_time_interval.index(min(flat_list_time_interval))]
        print("xxx use Flat:[XXX]".replace("XXX",flat_input).replace("xxx",tt))
        ff_all=[i0.split("[")[0].strip("\n") for i0 in open(flat_input).readlines()]
        for ff in ff_all:print("           "+ff)
        flat_cor_output=flat_input.strip("lst").strip("list").strip("LIST").strip("LST")+"zcor"
        with open(flat_cor_output,"w") as ff:
            for iii in open(flat_input,"r").readlines():
                ff.write(iii.split("[")[0].split("\n")[0].split("."+img_suffix)[0]+"_zcor"+"\n")
        flat_combine_output="flat."+target_filter+"."+(Time(fits.getheader((open(flat_input,"r").readlines()[0]).split("[")[0].strip("\n"))[Keys["date_key"]],format=Keys["date_key_type"]).iso).split()[0].replace("-","")
    
    # whether_continue=input("whether continue[y]/n:")
    # print(whether_continue)
    # if whether_continue in ["n","no","No","NO"]:
    #     break

    if False:
        pass
    else:
        from pyraf import iraf
        os.chdir(cwd)

        print('Loading IRAF packages ...')
        iraf.imred()
        iraf.ccdred()
        print('unlearning previous settings...')
        # iraf.ccdred.unlearn()
        iraf.ccdred.ccdproc.unlearn()
        iraf.ccdred.combine.unlearn()
        iraf.ccdred.flatcombine.unlearn()
        iraf.ccdred.zerocombine.unlearn()
        iraf.ccdred.darkcombine.unlearn()

        iraf.ccdred.ccdproc.ccdtype = ""
        iraf.ccdred.ccdproc.zerocor = False
        iraf.ccdred.ccdproc.flatcor = False
        iraf.ccdred.ccdproc.fixpix  = False
        iraf.ccdred.ccdproc.oversca = False
        iraf.ccdred.ccdproc.trim    = False
        iraf.ccdred.ccdproc.darkcor = False


        if fxpix:
            iraf.ccdred.ccdproc.fixpix  = False
            iraf.ccdred.ccdproc.fixfile = Keys["fixpix"]
        if Bias:
            if not zero_combine_done:
                # combine flat images
                print('Combining bias images ...')
                check_remove(zero_combine_output)
                iraf.ccdred.zerocombine.ccdtype = ''
                # iraf.ccdred.zerocombine.process = 'no'
                iraf.ccdred.zerocombine.process = False
                iraf.ccdred.zerocombine.reject  = 'avsigclip'
                iraf.ccdred.zerocombine.combine = "average"
                iraf.ccdred.zerocombine.rdnoise = Keys['rdnoise']
                iraf.ccdred.zerocombine.gain    = Keys["gain"]
                iraf.ccdred.zerocombine.output  = zero_combine_output
                iraf.ccdred.zerocombine(input="@"+bias_input)
            # iraf.ccdred.zerocombine(input=",".join(bb_all))

            iraf.ccdred.ccdproc.zerocor = True
            iraf.ccdred.ccdproc.zero    = zero_combine_output
        if Dark:
            print('Combining dark images ...')
            check_remove("@"+dark_cor_output)
            check_remove(dark_combine_output)
            iraf.ccdred.ccdproc(images="@"+dark_input,output="@"+dark_cor_output)
            iraf.ccdred.darkcombine.ccdtype = ''
            # iraf.ccdred.flatcombine.process = 'no'
            iraf.ccdred.darkcombine.process = False
            iraf.ccdred.darkcombine.reject  = 'avsigclip'
            iraf.ccdred.darkcombine.combine = "average"
            iraf.ccdred.darkcombine.rdnoise = Keys['rdnoise']
            iraf.ccdred.darkcombine.gain    = Keys["gain"]
            iraf.ccdred.darkcombine.output  = dark_combine_output
            iraf.ccdred.darkcombine(input="@"+dark_cor_output)
            iraf.ccdred.ccdproc.darkcor     = True
            iraf.ccdred.ccdproc.dark        = dark_combine_output

        if Flat:
            print('Combining flat images ...')
            check_remove("@"+flat_cor_output)
            check_remove(flat_combine_output)
            iraf.ccdred.ccdproc(images="@"+flat_input,output="@"+flat_cor_output)
            # TODO flat_cor_output name
            print(target_filter,flat_input,flat_cor_output)
            iraf.ccdred.flatcombine.ccdtype = ''
            iraf.ccdred.flatcombine.scale   = 'mode'
            # iraf.ccdred.flatcombine.process = 'no'
            iraf.ccdred.flatcombine.process = False
            iraf.ccdred.flatcombine.reject  = 'avsigclip'
            iraf.ccdred.flatcombine.combine = "median"
            iraf.ccdred.flatcombine.rdnoise = Keys['rdnoise']
            iraf.ccdred.flatcombine.gain    = Keys["gain"]
            iraf.ccdred.flatcombine.output  = flat_combine_output
            iraf.ccdred.flatcombine(input="@"+flat_cor_output)
            iraf.ccdred.ccdproc.flatcor     = True
            iraf.ccdred.ccdproc.flat        = flat_combine_output  

                  
        if trim:
            iraf.ccdred.ccdproc.trim    = True
            iraf.ccdred.ccdproc.trimsec = Keys["trimsec"]
        
        if overscan:
            iraf.ccdred.ccdproc.oversca = True
            iraf.ccdred.ccdproc.biassec = Keys["biassec"]
        check_remove(target_output)
        iraf.ccdred.ccdproc(images=tt,output=target_output)


        print('--- DONE ---')
