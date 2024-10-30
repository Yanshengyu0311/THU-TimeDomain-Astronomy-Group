#!/home/ysy/anaconda3/envs/iraf27/bin/python2.7
# encoding: utf-8

# 思路：
# 最高权限先指定bias、flat、dark、target
# 如果没指定，就寻找bias.list、flat.list之列的文件
# 最后再自动分。
#TODO 换一个望远镜的fits文件试一试
# from random import choices
# from email.mime import image
import numpy as np
import os
import optparse
import sys
from astropy.io import fits
from astropy.wcs import WCS
from reproject import reproject_interp
# 读取时间
import pandas as pd
import yaml
from astropy.time import Time
from call_Tools import check_image_suffix
from call_Tools import check_remove
from call_Tools import write_list

reload(sys)
sys.setdefaultencoding('utf-8')


# 获取当前文件 (main.py) 所在目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 构建 telescope_Pre.yaml 文件的完整路径
YAML_FILE_PATH = os.path.join(CURRENT_DIR, "telescope_Pre.yaml")

#####################
CWD=os.path.abspath(os.getcwd())

def remove_space_in_header_value(header):
    # 去除header中每个item的value中的空格
    for i in header:
        if type(header[i])== str: 
            if " " in header[i]:
                header[i]=header[i].replace(" ","")
    return header

def check_telescope_instrument(fitsname,opt_telescope,opt_instrument,):
    '''
    检查数据所用的望远镜以及终端
    '''
    specified_telescope = False
    specified_instrument = False
    if opt_telescope!=None:
        if opt_telescope in telescope_Pre_yaml:
            specified_telescope = True
            if opt_instrument!=None:
                if opt_instrument in telescope_Pre_yaml[opt_telescope]:
                    specified_instrument= True
                else:
                    raise Warning("%s is not in the telescope_Pre.yaml[%s],输入-p查看参数"%(opt_instrument,opt_telescope))
            else:
                raise Warning("instrument not specified,输入-p查看参数")
        else:
            raise Warning("%s is not in the telescope_Pre.yaml,输入-p查看参数"%opt_telescope)
    else:
        raise Warning("telescope not specified,输入-p查看参数")
    if specified_telescope and specified_instrument:
        telescop=opt_telescope
        instrume=opt_instrument
    
    else:
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

    print("Telescope specified by : %s"%telescop)
    print("instrument specified by : %s"%instrume)
    return telescop,instrume



def get_files_or_list(param):
    '''
    使用通配符解析输入文件
    '''
    import glob
    if param.startswith('@'):
        # 如果是以 @ 开头，返回列表文件的文件名
        return False,param[1:]  # 去掉@
    else:
        # 使用通配符返回匹配的文件列表
        matched_files = glob.glob(param)
        if not matched_files:
            print ("No files matched for pattern:",param)
        return True,matched_files


def print_table(level0_value):
    '''
    打印yaml表格
    '''
    # 创建 PrettyTable 对象
    from prettytable import PrettyTable
    table = PrettyTable()

    # 设定表头
    table.field_names = ["TELSCOPE", "INSTRUMENT", "KEY", "Value","Values"]
    print(level0_value)
    # 遍历 YAML 数据
    for level1_key, level1_value in level0_value.items():
        for level2_key, level2_value in level1_value.items():
            for level3_key, level3_value in level2_value.items():
                if isinstance(level3_value, dict):
                    for level4_key, level4_value in level3_value.items():                    
                        # print(level3_value)
                        table.add_row([level1_key, level2_key, level3_key, level4_key,level4_value])
                else:
                    table.add_row([level1_key, level2_key, level3_key,level3_value," "])

    # 打印表格
    print(table)


def del_pre_file(file_all):
    '''
    删除之前预处理的文件
    '''
    Old_Zero_Correction_file=[i for i in file_all if "_zcor.fits" in i]
    if any(Old_Zero_Correction_file):
        for i in Old_Zero_Correction_file:
            if os.path.exists(i):os.remove(i)


def cli():
    global telescope_Pre_yaml,suffix
    telescope_Pre_yaml=yaml.safe_load(open(YAML_FILE_PATH,"r").read())#telescopr_Pre_yaml

    parser = optparse.OptionParser()

    parser.add_option('--bias',"--Bias","-b","-B", 
                    dest='bias',
                    default="bias.list",
                    # choices=bias_choices,
                    help='The specific bias list contains all bias frame, Example:"@bias.list"(defualt). 如果用列表， 前面加上@，比如："@bias.lst"',
                    nargs=1) 

    parser.add_option('--dark',"--dark","-d","-D", 
                    dest='dark',
                    default="dark.list",
                    help='The specific flat list contains all dark frame, Example:"@dark.list"(defualt). 如果用列表， 前面加上@，比如："@dark.lst"') 

    parser.add_option('--flat',"--Flat","-f","-F", 
                    dest='flat',
                    default="flat.list",
                    help='The specific flat list contains all flat frame, Example:"@flat.list"(defualt). 如果用如果用列表， 前面加上@，比如："@flat.fits"') 

    parser.add_option('--science',"--SCI","-S","-s", 
                    dest='target',
                    default="target.list",
                    help='The specific flat list contains all target frame, Example:@target.list(defualt). 如果用通配符* ， 前面加上@，比如：@*target.fits') 


    parser.add_option('--instrument',"--inst","-I","-i", 
                    dest='instrument',
                    default=None,
                    help='Specify the instrument, Example: "XL80"')
    parser.add_option('--telescope',"--tele","-T","-t", 
                    dest='telescope',
                    default=None,
                    help='Specify the telescope, Example: "TNT80cm"')
    parser.add_option('--printyaml', "-p",
                    dest='printyaml',
                    action="store_true",
                    default=False,
                    help='打印yaml文件，不执行任何操作')
    parser.add_option('--printyamlpath', "--pyp",
                    dest='printyamlpath',
                    action="store_true",
                    default=False,
                    help='打印yaml文件的路径，不执行任何操作')
    # parser.add_option('--mergerimage', "--merger","-m",
    #                 dest='combine_image',
    #                 action="store_true",
    #                 default=False,
    #                 help='合并图像')
    parser.add_option('--tg',"--timegap","--TG", 
                    dest='time_gap',
                    default=0.499999,
                    help='Time gap')

    opt,args = parser.parse_args()
    
    if opt.printyaml    : print_table(telescope_Pre_yaml);exit()
    if opt.printyamlpath: print(YAML_FILE_PATH);exit()

    time_interval=opt.time_gap

    _,flat_list  = get_files_or_list(opt.flat)
    _,bias_list  = get_files_or_list(opt.bias)
    _,dark_list  = get_files_or_list(opt.dark)
    target_list= list(filter(lambda x: "_PreCor.fits" not in x,args))
    
    # print(flat_list)
    # print(bias_list)
    # print(dark_list)
    # print(args)

    file_all=os.listdir(CWD)
    #####################

    # print('All Files in %s:'% CWD)
    # for i in np.sort(file_all): print(i)

    # 删除之前预处理的文件
    del_pre_file(file_all)

    telescop,instrume=check_telescope_instrument(
                                   target_list[0],
                                   opt.telescope,
                                   opt.instrument,
                                   )
    
    Keys=telescope_Pre_yaml[telescop][instrume]





    if "pre_cmd"  in Keys: 
        for c in Keys["pre_cmd"]:os.system(c)
    
    layer="[%d]"%Keys["layer"] if "layer" in Keys else ""
 

    # 确定需要哪些操作
    # 替换关键字,bias,dark,flat,trim,overscan,badpix
    ehead=False
    Bias =False
    Dark =False
    Flat =False
    trim =False
    fxpix=False
    overscan=False


    if "bias_value" in Keys:Bias=True;    print("Bias will be subtracted")
    if "dark_value" in Keys:Dark=True;    print("Dark will be corrected")
    if "flat_value" in Keys:Flat=True;    print("flat will be corrected")
    if "trimsec"    in Keys:trim=True;    print("The image will be trimed within"+ Keys["trimsec"])
    if "fixpix"     in Keys:fxpix=True;   print("The bad pixel mask is "+ Keys["fixpix"])
    if "biassec"    in Keys:overscan=True;print ("The overscan region is" + Keys["biassec"] )
    if "replace_key" in Keys:
        ehead=True
        for k in Keys["replace_key"]["key"]:
            print("%s will be update"%Keys["replace_key"]["key"][k])

    
    img_suffix=check_image_suffix(file_all, Keys)

    # 找到和上面后缀一样的文件
    img_all=[i for i in file_all if i.split(".")[-1]==img_suffix]

    # print(img_all)
    


    # sys.argv 大于等于3，意味着使用了optparse ，从而意味着指定文件了
    bias_list_all  =[]
    dark_list_all  =[]
    flat_list_all  =[]
    target_list_all=[]

    dark_specific_list=False
    flat_specific_list=False
    bias_specific_list=False
    # fits_info
    image_info=pd.DataFrame(columns=["FitsName",
                                    "MJD",
                                    "ObjectType",
                                    "Filter",
                                    "Specified",
                                    "Header",
                                    "ZeroCor",
                                    "DarkCor",
                                    "FlatCor",
                                    ])

    for i in img_all:
        # file_type
        fits_header=fits.getheader(i)
        fits_header=remove_space_in_header_value(fits_header)

        new_row={
            "FitsName"  :i,
            "MJD"       :Time(fits_header[Keys["date_key"]],format=Keys["date_key_type"]).mjd,
            "ObjectType":fits_header[Keys["object_key"]] if Keys["object_key"] in fits_header else None,
            "Filter"    :fits_header[Keys["filter_key"]] if Keys["filter_key"] in fits_header else None,
            "Specified" :False, 
            "Header"    :fits_header,
            "ZeroCor"   :"",
            "DarkCor"   :"",
            "FlatCor"   :"",
        }

        image_info.loc[len(image_info)] = new_row


    image_info=image_info.sort_values(by=["MJD"]).reset_index(drop=True)
    
    for i in bias_list  :image_info.loc[image_info["FitsName"]==i,"Specified"] =True
    for i in dark_list  :image_info.loc[image_info["FitsName"]==i,"Specified"] =True
    for i in flat_list  :image_info.loc[image_info["FitsName"]==i,"Specified"] =True
    for i in target_list:image_info.loc[image_info["FitsName"]==i,"Specified"] =True;\
                         image_info.loc[image_info["FitsName"]==i,"ObjectType"]="science"

    print(image_info)

    
    # TODO 不用写成一个txt文件然后，然后再@bias.list了。可以用python list加入进去


    # 每一种类型（bias,dark）可能拍摄时间不同，对时间进行分类，并写文件。

    zero_combine_done=False
    dark_combine_done=False
    flat_combine_done={i: False for i in image_info.loc[image_info["ObjectType"]=="science","Filter"].unique()}



    
    list_date =lambda x: Time(np.mean(x["MJD"].values),format="mjd").to_datetime().strftime("%Y%m%d")
    file_layer=lambda x: [i+layer for i in x]

    # file_ZeroCor=lambda x: [ for f in x]

    for i in image_info.index:
        if image_info.loc[i,"ObjectType"]!="bias" and \
           image_info.loc[i,"Specified" ]==True :
            image_info.loc[i,"ZeroCor"]=image_info.loc[i,"FitsName"].split("."+img_suffix)[0]+"_ZeroCor.fits"
    for i in image_info.index:
        if image_info.loc[i,"ObjectType"]!="bias" and \
           image_info.loc[i,"ObjectType"]!="dark" and \
           image_info.loc[i,"Specified" ]==True :
            image_info.loc[i,"DarkCor"]=image_info.loc[i,"FitsName"].split("."+img_suffix)[0]+"_ZeroDarkCor.fits"

    from call_iraf import IRAF
    iraf=IRAF(
                 Keys=Keys,
                 cwd=CWD,
                 fxpix=fxpix,
                 Bias=Bias,
                 Dark=Dark,
                 Flat=Flat,
                 trim=trim,
                 overscan =overscan,
    )

    
    dark_combine_input =None
    dark_combine_output=None
    dark_correct_input =None
    dark_correct_output=None
    zero_combine_input =None
    zero_combine_output=None
    zero_correct_input =None
    zero_correct_output=None
    flat_combine_input =None
    flat_combine_output=None
            
    zero_combine_done=False
    for tt in image_info.loc[image_info["ObjectType"]=="science"].index:
        target_filter=image_info.loc[tt,"Filter"]
        target_mjd   =image_info.loc[tt,"MJD"]
        target_input =image_info.loc[tt,"FitsName"]
        target_output=image_info.loc[tt,"FitsName"].strip("."+img_suffix)+"_PreCor"
        print("Process %s at MJD=%.2f"%(target_input,target_mjd))
        
        if Bias:
            bias_used         =image_info.loc[(image_info["ObjectType"]=="bias")&
                                              (image_info["Specified" ]==True),]
            image_need_ZeroCor=image_info.loc[(image_info["ObjectType"]!="bias")&
                                              (image_info["Specified" ]==True),]
            
            print("bias used:")
            for f in bias_used["FitsName"].values:print("%20s"%f)
            # print(bias_used[["FitsName","MJD","ZeroCor"]])
            # print(image_need_ZeroCor[["FitsName","MJD","ZeroCor"]])
            
            zero_combine_input ="zero.%s.list"  %list_date(bias_used)
            zero_combine_output="zero.%s.fits"  %list_date(bias_used)
            zero_correct_input ="ZeroCor_input.%s.list" %list_date(bias_used)
            zero_correct_output="ZeroCor_output.%s.list"%list_date(bias_used)
            
            write_list(file_layer(bias_used["FitsName"].values),
                       zero_combine_input,)
            write_list(file_layer(image_need_ZeroCor["FitsName"].values),
                       zero_correct_input,)
            write_list(image_need_ZeroCor["ZeroCor"].values,
                       zero_correct_output,)
            
        if Dark:
            dark_used         =image_info.loc[(image_info["ObjectType"]=="dark")&
                                              (image_info["Specified" ]==True),]
            image_need_DarkCor=image_info.loc[(image_need_ZeroCor["ObjectType"]!="dark")]
            
            print("dark used:")
            for f in dark_used["FitsName"].values:print("%20s"%f)
            
            dark_combine_input ="dark.%s.list"  %list_date(dark_used)
            dark_combine_output="dark.%s.fits"  %list_date(dark_used)
            dark_correct_input ="DarkCor_input.%s.list" %list_date(bias_used)
            dark_correct_output="DarkCor_output.%s.list"%list_date(bias_used)
            
            write_list(file_layer(dark_used["FitsName"].values),
                       dark_combine_input,)
            write_list(file_layer(image_need_DarkCor["FitsName"].values),
                       dark_correct_input,)
            write_list(image_need_DarkCor["ZeroDarkCor"].values,
                       dark_correct_output,)
            
            
        if Flat:
            flat_used         =image_info.loc[(image_info["ObjectType"]=="flat")&
                                              (image_info["Filter"    ]==target_filter)&
                                              (image_info["Specified" ]==True),]
            
            print("flat used:")
            for f in flat_used["FitsName"].values:print("%20s"%f)
            
            flat_combine_input ="flat.%s.%s.list"  %(list_date(flat_used),target_filter)
            flat_combine_output="flat.%s.%s.fits"  %(list_date(flat_used),target_filter)
            
            write_list(file_layer(flat_used["FitsName"].values),
                       flat_combine_input,)
    
        # whether_continue=input("whether continue[y]/n:")
        # print(whether_continue)
        # if whether_continue in ["n","no","No","NO"]:
        #     break

        if False:
            pass
        else:
            iraf.process(image_input=target_input,
                image_output=target_output,
                zero_combine_input =zero_combine_input,
                zero_combine_output=zero_combine_output,
                dark_combine_input =dark_combine_input,
                dark_combine_output=dark_combine_output,
                flat_combine_input =flat_combine_input,
                flat_combine_output=flat_combine_output,
                zero_correct_input =zero_correct_input,
                zero_correct_output=zero_correct_output,
                dark_correct_input =dark_correct_input,
                dark_correct_output=dark_correct_output,
                target_filter=target_filter,
                zero_combine_done=zero_combine_done,
                )

    
if __name__ == "__main__":
    # 最高权限先指定bias、flat、dark、target
    cli()

    

