import pandas as pd
import io
import json

input_file = 'LCO.js'

MJD0 = 60584.07425925927 + 19.1230947217

MJD_list = []
m_list = []
dm_list = []
mark_list = []
filter_list = []
detect_list = []

with open(input_file, 'r') as f:
	line = f.readline()
lines = line.split('}, {label')[1:]
len_lines = len(lines)
for i in range(len_lines):
	filter_ = lines[i].split('"')[1].split()[-1][0]
	#print(filter_)
	data_ = lines[i][lines[i].index('[['):].replace('[','').replace(']','').replace('"','').split(',')
	data_len = len(data_)
	data_n = int(data_len / 4)
	for j in range(data_n):
		MJD_list.append(float(data_[4*j]) + MJD0)
		m_list.append(float(data_[4*j+1]))
		dm_list.append(float(data_[4*j+2]))
		mark_list.append(True)
		filter_list.append('LCO_'+filter_)
		detect_list.append(True)
data = pd.DataFrame({'MJD':MJD_list,
				   'm':m_list,
				   'dm':dm_list,
				   'mark':mark_list,
				   'filter':filter_list,
				   'detect':detect_list}).sort_values(by='MJD')

data.to_csv('LCO.dat',index=False)





	
