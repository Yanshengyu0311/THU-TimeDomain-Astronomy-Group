# encoding: utf-8
import os

suffix={"fits":0,"fit":0,"fts":0}

def check_image_suffix(file_all,Keys):
    '''
    # 找出来图的后缀，统计所有后缀，后缀多的作为最终后缀
    '''
    img_suffix="fits"
    if "suffix" in Keys:
        img_suffix=Keys["suffix"]
    else:
        for f in file_all:
            file_suffix=f.split(".")[-1]
            if file_suffix in suffix.keys():
                suffix[file_suffix] += 1
        for i in suffix.keys():
            if suffix[i] ==max(suffix.values()):
                img_suffix=i
    print("image suffix is "+img_suffix)
    return img_suffix
    
def check_remove(file_list,):
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
            if os.path.exists(cf):
                os.remove(cf)
            else:
                for s in suffix_fits:
                    if os.path.exists(cf+"."+s):
                        os.remove(cf+"."+s)
    elif type(file_list)==type(list):
        for f in file_list:
            if os.path.exists(f):
                os.remove(f)

def find_list(list_arg):
    import glob
    files = glob.glob(os.path.join(CWD,list_arg))
    list_select=[os.path.abspath(i) for i in files if os.path.exists(i)] 
    return list_select

def write_list(List,file_name):
    with open(file_name,"w") as f:
        for i in List:
            f.write(i+"\n")
    print("%s has been written."%file_name)