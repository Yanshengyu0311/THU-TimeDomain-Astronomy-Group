#! /home/ysy/anaconda3/envs/autophot_env/bin/python


# from dataclasses import replace
# from tkinter.font import BOLD
# from distutils.log import error
# from types import NoneType
import pwd
from autophot.prep_input import load
from autophot.autophot_main import run_automatic_autophot
import os
from astropy.io import fits


def linput(input_str,Arg):
    i="buzhidao"
    while i not in Arg:
        i=input(input_str)
    return i

def replace_autophot_input(param):
    autophot_input=load()
    autophot_input["wdir"]=""
    for i in param:
        if i in autophot_input:
            if type(param[i])!=str and autophot_input[i]!=None and type(autophot_input[i])!=bool:
                for j in param[i]:

                    if j in autophot_input[i]:
                        autophot_input[i][j]=param[i][j]
                    else:
                        raise KeyError("%s not in deflault autophot input parameter list"%j)
            elif autophot_input[i]==None:
                autophot_input[i]=param[i]
            elif type(autophot_input[i])!=bool:
                autophot_input[i]=param[i]
        
        else:
            raise KeyError("%s not in deflault autophot input parameter list"%i)
    return autophot_input

def read_autophot_LC(csv_name):
    import numpy as np
    import pandas as pd
    REDUCED_csv=pd.read_csv(csv_name)
    num_photo_data=len(REDUCED_csv)
    all_filter=["r","i","u","g","z","B","V","I","U","C"]
    all_band=list(filter(lambda x: x in all_filter,REDUCED_csv.keys()))
    autophot_result=[]
    all_fits_name=[]
    for i in range(num_photo_data):
        reduce_csv = REDUCED_csv.iloc[i,:]
        fits_name  = reduce_csv["fname"].split("/")[-1]
        # 是否减模板
        subtract = reduce_csv.subtraction
        # 判断滤光片
        for j in all_band:
            if type(reduce_csv[j])==type(str()):
                Filter=j
                break
        mjd  = reduce_csv.mjd
        telescope=reduce_csv.telescope
        mag  = float(reduce_csv[j].strip("[").strip("]"))
        mag_e= reduce_csv[j+"_err"]
        detection_limit_SNR=3
        
        if np.isnan(mag) and ~np.isnan(reduce_csv["lmag_inject"]):
            detection=0
            mag=reduce_csv["lmag_inject"]

        if np.isnan(reduce_csv["lmag_inject"]):
            detection= 1
        elif reduce_csv["lmag_inject"] >mag:
            detection = 1
        else:
            detection = 0
            mag       = reduce_csv["lmag_inject"]
        if subtract and ~np.isnan(mag):
            if fits_name in all_fits_name:
                remove_item=list(filter(lambda x:np.abs(x[0]-mjd)<2e-4,autophot_result))[0]
                autophot_result.remove(remove_item)
            all_fits_name.append(fits_name)
            autophot_result.append([mjd,mag,mag_e,telescope,Filter,detection])
    mjdsort=np.argsort([i[0] for i in autophot_result ], )
    autophot_result=[autophot_result[i] for i in mjdsort]
    return autophot_result


def select_filter(band):
    all_fits_name=[f for f in os.listdir("./") if ".fits" in f]
    band_id={
        "i":"ip",
        "r":"rp",
        "g":"gp",
        "B":"B",
        "V":"V",
        "U":"U",
        "z":"zs",
    }
    excluded_filter=[band_id[f] for f in band_id if f not in band]
    selected_filter=[band_id[f] for f in band_id if f     in band]
    print("The filter excluded",excluded_filter)
    print("The filter reduced" ,selected_filter)
    for f in all_fits_name:
        if fits.open(f)[0].header["FILTER"] in excluded_filter:
            os.system("mv %s ../"%f)


if __name__ == '__main__':
    import optparse
    import sys  
    import os
    import yaml

    yes=["Y","y","Yes","yes","YES",""]
    no =["N","n","No" ,"no" ,"NO"] 
    CurrentPath = os.getcwd()
    ScriptPath  = sys.path[0]

    parser = optparse.OptionParser(
        prog ="Autophot.py",
        usage= "%prog [options] autophot.yml"
    )
    
    parser.add_option("--wdir","-w", 
                    dest='workdir',
                    default=ScriptPath,
                    help='Directry contains Yaml file for telescope and instrument configuration') 

    parser.add_option("--SimpleDefault","--SD",
                    dest='SimpleYaml',
                    action="store_true",
                    help='Creat a Simple Autophot Yaml configuration file') 

    parser.add_option("-D",
                    dest='DefaultYaml',
                    action="store_true",
                    help='Creat a default Autophot Yaml configuration file') 
    parser.add_option("-r","-R",
                    dest="ReadResult",
                    help='print result File')
    parser.add_option("-f","--filter", 
                dest='Reduce_Filter',
                default="all",
                type=str,
                help='The filter would like to be reduced')
    # TODO
    parser.add_option("--RA","--ra", 
                    dest='ra',
                    default=0,
                    type=float,
                    help='ra of target')

    parser.add_option('--update',"-u", 
                    dest='UpdateYaml',
                    action="store_true",
                    help='whether update the Yaml')
                     
    opt,args = parser.parse_args()
    
    
    if opt.SimpleYaml==True:
        
        YamlNameSimple="autophot_simple.yaml"
        YamlPathDefualt=os.path.join(CurrentPath,YamlNameSimple)

        with open(os.path.join(ScriptPath,YamlNameSimple),'r') as y:
            autophot_input_simple=yaml.load(y,Loader=yaml.FullLoader)
        
        autophot_input_simple["wdir"]     =ScriptPath+"/"
        autophot_input_simple["fits_dir"] =CurrentPath+"/"
        # autophot_input_simple[]=

        with open(YamlPathDefualt,"w") as f:
            f.write(yaml.dump(autophot_input_simple, allow_unicode=True))

        print("The simple Autophot Yaml file have been saved in:")
        print(YamlPathDefualt)
        
        sys.exit()

    if opt.DefaultYaml==True:
        autophot_input = load()
        YamlNameDefualt="autophot.yaml"
        YamlPathDefualt=os.path.join(CurrentPath,YamlNameDefualt)

        autophot_input["wdir"]     =ScriptPath+"/"
        autophot_input["fits_dir"] =CurrentPath+"/"
        # autophot_input[]=

        with open(YamlPathDefualt,"w") as f:
            f.write(yaml.dump(autophot_input, allow_unicode=True))

        print("The default Autophot Yaml file have been saved in:")
        print(YamlPathDefualt)
        
        sys.exit()

    if opt.ReadResult:
        # Path0=os.path.abspath(CurrentPath+"/../")
        # Path1=CurrentPath.split("/")[-1]
        # PathOutput=Path1+"_REDUCED"
        # PathCSV=os.path.join(Path0,PathOutput,"REDUCED.csv")
        PathCSV=opt.ReadResult
        autophot_result=read_autophot_LC(PathCSV)

        for i in autophot_result: print(i)

        sys.exit()
    if opt.Reduce_Filter!="all":
        select_filter(opt.Reduce_Filter)

        sys.exit()

    

    dir_contents = [i for i in os.listdir(CurrentPath) if not i.startswith('.')]
    FITSFile=list(filter(lambda x: ".fit" in x,dir_contents))
    print(any(FITSFile))
    if not any(FITSFile): 
        print("No image in current path")
        sys.exit()

    
    autophot_yaml  =args[0]
    if os.path.exists(autophot_yaml):
        with open(autophot_yaml,'r') as y:
            autophot_input_param=yaml.load(y,Loader=yaml.FullLoader)
    else:
        raise ValueError("%s no find"%autophot_yaml)

    autophot_input = replace_autophot_input(autophot_input_param)

    fits_dir_autophot_input=os.path.abspath(autophot_input["fits_dir"])
    if fits_dir_autophot_input != os.path.abspath(CurrentPath):
        print("FITS path in %s is not current path but %s"%tuple([autophot_yaml,fits_dir_autophot_input]))
        ChangePath=linput("Whether change the path into the current path([yes]/no):",yes+no)
        if   ChangePath in yes:
            autophot_input["fits_dir"]=os.path.abspath(CurrentPath)+"/"
        elif ChangePath in no:
            pass
    
    if autophot_input['template_subtraction']['prepare_templates']:
        run_automatic_autophot(autophot_input)
        autophot_input['template_subtraction']['prepare_templates']=False
    run_automatic_autophot(autophot_input)
