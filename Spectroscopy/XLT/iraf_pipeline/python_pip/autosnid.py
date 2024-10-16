#!/usr/bin/python3

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

snidout='_snid.output'
compout='_snid.png'
snidflux=[
        '_snidflux.dat',
        '_comp0001_snidflux.dat','_comp0002_snidflux.dat',
        '_comp0003_snidflux.dat','_comp0004_snidflux.dat'
    ]
legends=['input spectrum','2','3','4','5']
plots=[None,None,None,None,None]
colors=['k','r','g','b','m']

def exec(command):
    print(command)
    result=os.system(command)
#    print('command returned '+str(result))
    
def getsnidbase(filepath):
    i=len(filepath)
    while i>0 and filepath[i-1]!='/' and filepath[i-1]!='\\':
        i-=1
    j=len(filepath)
    while j>i and filepath[j-1]!='.':
        j-=1
    if j>i and filepath[j-1]=='.':
        j-=1
    return filepath[i:j]

def getbase(filepath):
    i=len(filepath)
    while i>0 and filepath[i-1]!='/' and filepath[i-1]!='\\':
        i-=1
    while i<len(filepath) and filepath[i]!='.':
        i+=1
    return filepath[:i]
print (os.path.abspath(os.path.dirname(__file__)))
current_abs_path=os.path.abspath(os.path.dirname(__file__))
basename=[]

allfile=[]
for root, dirs, files in os.walk(current_abs_path):  
    allfile=allfile+ files
for ff in allfile:
    if "_bfosc_" in ff and ".txt" in ff:
        basename.append(ff.split(".")[0])
SNID_done_list=[]
for nm in  basename:
    for ff in allfile:
        if nm  in allfile:
            if nm +compout == ff:
                SNID_done_list.append(nm)
print(SNID_done_list)

# for ll in SNID_done_list:
#     if ll in basename:
#         basename.remove(ll)
print(basename)
for BB in basename:
    filepath=BB+".txt"
    snidbase=getsnidbase(filepath)
    realbase=current_abs_path
    snidcommand='snid verbose=0 inter=0 plot=0 fluxout=4'
    
    snidcommand+=' '+filepath
    exec(snidcommand)
    
    snidout0=realbase+"/"+BB+snidout
    srcdata=np.loadtxt(snidbase+snidflux[0])
    exec('rm '+snidbase+snidflux[0])
    plt.figure(figsize=(8,12))
    plt.xlabel('redshifted wavelength[A]')
    plt.ylabel('flux+offset[arbitrary]')
    title=realbase
    snidres=open(snidout0,'r')
    index=0
    plotmax=max(srcdata[:,1])+1.5*3
    plotmin=min(srcdata[:,1])
    for line in snidres:
        if index>0 and index<=4:
            compdata=np.loadtxt(snidbase+snidflux[index])
            exec('rm '+snidbase+snidflux[index])
            compmax=max(compdata[:,1])+1.5*(4-index)
            compmin=min(compdata[:,1])+1.5*(4-index)
            if compmax>plotmax:
                plotmax=compmax
            if compmin<plotmin:
                plotmin=compmin
            plots[0],=plt.plot(srcdata[:,0],srcdata[:,1]+1.5*(4-index),colors[0],linewidth=0.5)
            plots[index],=plt.plot(compdata[:,0],compdata[:,1]+1.5*(4-index),colors[index])
            line=line.split()
            legends[index]=line[0]+': '+line[1]+'('+line[2]+')'+'\nz='+line[5]+'+-'+line[6]+' age='+line[7]
            index+=1
        elif line=='#no. sn type lap rlap z zerr age age_flag grade\n':
            index=1
        elif line[:4]=='zmed':
            line=line.split()
            title+='\nz='+line[1]+'+-'+line[2]
        elif line[:4]=='agem':
            line=line.split()
            title+='\nage='+line[1]+'+-'+line[2]

    plt.title(title)
    plotrange=plotmax-plotmin
    plt.ylim(plotmin-plotrange*0.05,plotmax+plotrange*0.25)
    snidres.close()
    plt.legend(plots,legends,loc='upper left')
    plt.savefig(realbase+"/"+BB+compout)
    print('results are stored in '+snidout0)
    print('comparison figure is stored in '+realbase+"/"+BB+compout)