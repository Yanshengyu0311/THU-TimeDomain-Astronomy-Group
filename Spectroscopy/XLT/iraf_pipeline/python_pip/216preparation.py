#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
拿到这个文件应保证系统运行python3,有sys模块,还要有执行权限,不然就改权限chmod
此脚本用于将兴隆的log表.txt文件, 提取信息, 生成数据处理的前期准备文件, bias.lst, flat.lst, log

兴隆的log表的名字一般给的时候是如20181002.txt(下面都用这个文件名举例)这样的, 但是有的时候可能是20181002-wxf.txt或者其他形式,但是第一步要把这个文件名改为标准的如20181002.txt这样的形式,日期就是拍摄当日的日期,要8位数的格式.

第二步打开20181002.txt, 把里面的空白行都删除,然后在notes那一列下面将comp, standard, slit, object写好, flat和bias不用写,写了也没事.

第三步要把兴隆的log表和这个脚本放在一个目录下,然后在命令行输入216preparation.py 20181002.txt,打回车就行,程序运行完毕同目录下会生成名为,log,bias.lst,flat.lst三个文件,检查一下看看符不符合要求.
"""
"""
2021.02.01记
上面的记录是之前学长学姐写的，之后我曾有一些修改。
在2021年1月31日，216望远镜的文件名命名个已经发生了了很大的改变，为了适应改变，我做除了一些修改，这些修改让这个脚本变得臃肿，但是还是可以凑合用的。如果你看懂这个脚本以后，你就可以发现，这个脚本可以写的更加优雅，简洁。但是我比较懒，不想写了。有人想写的话可以放弃正这个脚本。
"""

import sys
import os
print(sys.argv)
#xinglong_log_file_name = os.getcwd().split('/')[-1]+'.txt'
xinglong_log_file_name = sys.argv[1]
print(xinglong_log_file_name)
#读取命令行输入的参数, 因为命令行输入的是216preparation.py 20181002.txt, 所以argv[0]就是216preparation.py, argv[1]就是20181002.txt

# if '/' in xinglong_log_file_name:
#     print('''this script does not accept absolute path,
#              which means that you must go into the directory
#              where xinglong log exists.''')
#     sys.exit()

#提取文件名中的日期信息
#date = xinglong_log_file_name.split('.')[0]
date=os.path.realpath(sys.argv[1]).split("/")[-2]


# input_path = './'+date+'.txt'
input_path=xinglong_log_file_name
bias_path = './bias.lst'
flat_path = './flat.lst'
log_path = './log'

try:
    f_input = open(input_path, 'r', encoding = 'iso8859')
    #兴隆的log表给的时候他们那台电脑比较老所以编码用的比较老,所以读取的时候要规定编码为iso8859
except:
    print('file does not exist!')
    sys.exit()
f_bias = open(bias_path, 'w')
f_flat = open(flat_path, 'w')
f_log = open(log_path, 'w')




day = date[6:8]#提取日期中的天
month = date[4:6]#提取日期中的月份
year = date[0:4]#提取日期中的年份

#下面的代码是为了写pipeline需要的log表的第二行下一天的日期.
#estimate if leap year.
if int(year)%100 == 0 and int(year)%400 == 0:
    leap_year_flag = True
elif int(year)%100 != 0 and int(year)%4 == 0:
    leap_year_flag = True
else:
    leap_year_flag = False

#estimate if big month or little month or Feb
if month in ['01','03','05','07','08','10','12']:
    if day == '31':
        next_date = '01/'+str((int(month)+1)%12)+'/'+year[-2:]
    else:
        next_date = str(int(day)+1)+'/'+month+'/'+year[-2:]
elif month in ['04','06','09','11']:
    if day == '30':
        next_date = '01/'+str((int(month)+1)%12)+'/'+year[-2:]
    else:
        next_date = str(int(day)+1)+'/'+month+'/'+year[-2:]
elif month == '02':
    if leap_year_flag and day == '29':
        next_date = '01/03/'+year[-2:]
    elif (not leap_year_flag) and day == '28':
        next_date = '01/03/'+year[-2:]
    else:
        next_date =str(int(day)+1)+'/03/'+year[-2:]

#如果是一年的最后一天,则上面的判断作废, 重新给next_date赋值
if month == '12' and day == '31':
    next_date = '01/01/' + str(int(year[-2:])+1)

f_log.write(day+'/'+month+'/'+year[-2:]+'\n')#在pipeline需要的log表中第一行写下拍摄日的日期
f_log.write(next_date +'\n')#在第二行中写下拍摄日的下一天的日期


lines = f_input.readlines()[11:]#兴隆观测站216log文件从11行及以后是观测的信息

#获取路径下所有问你件名
all_file_name=[]
data_log_path = os.path.realpath(sys.argv[1])
data_path     = data_log_path.strip(data_log_path.split("/")[-1])
for root, dirs, files in os.walk(data_path):
    i=[]

for line in lines:
    file_num = line[0:15].strip()
    obj = line[15:28].strip()
    btime = line[28:41].strip()
    exposure = line[41:52].strip()
    ra = line[52:66].strip()
    dec = line[66:80].strip()
    epoch = line[80:91].strip()
    if ra == '':
        ra = '00:00:00.00'

    if dec == '':
        dec = '00:00:00.0'

    if epoch == '':
        epoch = '2000'
    
    notes = line[91:].strip()
    if obj in ['bias','Bias','BIAS','BIas','BIAs']:
        notes = 'zero'
        obj = 'bias'
    elif obj in ['flat','Flat','FLAT','FLat','FLAt']:
        notes = 'flat'
        obj = 'flat'
    else:
        pass
    

    if '-' in file_num:
        file_num_front = int(file_num.split('-')[0][-3:])
        file_num_end = int(file_num.split('-')[1])
        for i in range(file_num_front, file_num_end+1):
            output_file_num = file_num[0:8] + '%04d'%i
            output_file_name=list(filter(lambda x:output_file_num in x,files))[0]
            outputline = '%-70s'%output_file_name + '%-17s'%obj + '%-13s'%notes +\
                         '%-13s'%btime + '%-6s'%exposure + '%-15s'%ra + '%+11s'%dec +\
                         '%+10s'%epoch + '\n'
            f_log.write(outputline)
            if obj == 'bias':
                f_bias.write(output_file_name + '\n')
            elif obj == 'flat':
                f_flat.write(output_file_name + '\n')
            else:
                print('wrong when writing flat.lst and bias.lst')
    else:
        output_file_num = file_num[0:8] + '%04d'%int(file_num[8:])
        output_file_name=list(filter(lambda x:output_file_num in x,files))[0]
        # print(output_file_name)

        notes="aa"
        if 'fear' in output_file_name.lower():
            notes="comp"
        elif ('sn'  in obj.lower()\
        or 'at'     in obj.lower()\
        or 'tmt'    in obj.lower()):
            notes="object"
        elif ((list(filter(lambda X:X.lower().split('\n')[0] in obj.lower(),open(sys.argv[0].strip(sys.argv[0].split("/")[-1])+'allstd.lst','r').readlines())))!=[]):
            notes="standard"
        print(notes)

        outputline = '%-70s'%output_file_name + '%-17s'%obj + '%-13s'%notes +\
                     '%-13s'%btime + '%-6s'%exposure + '%-15s'%ra + '%+11s'%dec +\
                     '%+10s'%epoch + '\n'
        f_log.write(outputline)


f_input.close()
f_bias.close()
f_flat.close()
f_log.close()
os.system("cat *.txt") 
print('\n')


















