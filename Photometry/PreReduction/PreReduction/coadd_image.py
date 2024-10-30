
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


# 获取当前文件 (main.py) 所在目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 构建 telescope_Pre.yaml 文件的完整路径
YAML_FILE_PATH = os.path.join(CURRENT_DIR, "telescope_Pre.yaml")

#####################
CWD=os.path.abspath(os.getcwd())


def most_common_prefix(lst):
    # 找出最短字符串，作为最长可能前缀的初始值
    shortest_str = min(lst, key=len)
    
    # 初始化前缀的最大长度
    max_prefix_len = len(shortest_str)
    
    # 遍历最大可能的前缀长度
    for i in range(len(shortest_str)):
        prefix = shortest_str[:i+1]
        
        # 计算具有当前前缀的字符串数量
        count = sum(1 for s in lst if s.startswith(prefix))
        
        # 如果所有字符串都包含这个前缀，更新最大前缀长度
        if count == len(lst):
            max_prefix_len = i + 1
        else:
            break

    # 返回所有字符串共有的最长前缀
    return shortest_str[:max_prefix_len]


def combine_image(fits_path,
                  output_path=None,
                  mjd=0,
                  time_header_key="DATE-OBS",
                  time_fmt="isot",
                  filter_header_key="FILTER",
                    INSTRUME_header_key="INSTRUME",
                    TELESCOP_header_key="TELESCOP",):   
    import warnings
      
    combine_file="CombinedImages"
    if os.path.exists("./"+combine_file):
        pass
    else:
        print("./"+combine_file,"created")
        os.mkdir("./"+combine_file)
    if output_path is None:
        output_path = most_common_prefix(fits_path)+".fits"
    combine_fits_path="./"+combine_file+"/"+output_path
    if len(fits_path)==1:
        if os.path.exists(combine_fits_path):
            os.remove(combine_fits_path)
        import shutil
        shutil.copyfile(fits_path[0], combine_fits_path) 
        print(fits_path,"-->")
        print(combine_fits_path) 
    else:
        
        hdul=[]
        for p in fits_path:
            hdul.append(fits.open(p)[0])
        all_TELESCOP=np.unique([h.header[TELESCOP_header_key] for h in hdul])
        all_instrume=np.unique([h.header[INSTRUME_header_key] for h in hdul])
        all_filter  =np.unique([h.header[filter_header_key ] for h in hdul])
        if len(all_TELESCOP)>1:
            warnings.warn(all_TELESCOP)
            return
        elif len(all_instrume)>1:
            warnings.warn(all_instrume)
            return
        elif len(all_filter)>1:
            warnings.warn(all_filter)
            return 
        else:
            print("Telescope: ",all_TELESCOP[0])
            print("Instrument:",all_instrume[0])
            print("Filter:    ", all_filter[0])
            for i in fits_path:
                if i != fits_path[-1]:
                    print("%s +"%(i))
                else:
                    print(i)
            print("= %s"%(combine_fits_path))

        
        from reproject import mosaicking
        combined_image, footprint =mosaicking.reproject_and_coadd(
            input_data=hdul,
            output_projection=WCS(hdul[0].header),
            reproject_function= reproject_interp,
            shape_out=tuple([hdul[0].header["NAXIS1"],hdul[0].header["NAXIS2"]]),
            combine_function='sum',
            )
        combined_image[~footprint.astype(bool)] = 0
        new_header=hdul[0].header.copy()
        new_header["EXPTIME"]=np.sum([h.header["EXPTIME"] for h in hdul])
        if mjd==0:
            combine_time=np.nanmean([Time(h.header[time_header_key],format=time_fmt).mjd for h in hdul])
            new_header[time_header_key]=Time(combine_time,format="mjd").to_value(format=time_fmt)
        else:
            new_header[time_header_key]=mjd
            
        combined_hdu = fits.PrimaryHDU(data=combined_image,
                                    header=new_header)

        combined_hdu.writeto(combine_fits_path,overwrite=True)
        print("Done")

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

if __name__ == "__main__":

    global telescope_Pre_yaml,suffix
    telescope_Pre_yaml=yaml.safe_load(open(YAML_FILE_PATH,"r").read())#telescopr_Pre_yaml

    parser = optparse.OptionParser()

    parser.add_option('--instrument',"--inst","-I","-i", 
                    dest='instrument',
                    default=None,
                    help='Specify the instrument, Example: "XL80"')
    parser.add_option('--telescope',"--tele","-T","-t", 
                    dest='telescope',
                    default=None,
                    help='Specify the telescope, Example: "TNT80cm"')
    parser.add_option('--output',"--out","-O","-o",
                    dest='combine_output',
                    default=None,
                    help='Name for output file')

    opt,args = parser.parse_args()

    telescop,instrume=check_telescope_instrument(
                                   args[0],
                                   opt.telescope,
                                   opt.instrument,
                                   )
    
    Keys=telescope_Pre_yaml[telescop][instrume]

    combine_image(list(args),
                  opt.combine_output,
                mjd=0,
                time_header_key=Keys["date_key"],#"DATE-OBS"
                time_fmt=Keys["date_key_type"],#"isot"
                filter_header_key=Keys["filter_key"],#"FILTER",
                INSTRUME_header_key="INSTRUME",
                TELESCOP_header_key="TELESCOP",)
    exit()