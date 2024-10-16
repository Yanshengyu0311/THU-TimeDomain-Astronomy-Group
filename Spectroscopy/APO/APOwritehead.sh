#!/bin/bash
echo $PATH

#this script writes JD to the .fits file of the spectrm of APO3m5
list_fits='fits.lst';list_txt='txt.lst';outfile="./writejd.cl";
ls *.fits > $list_fits; ls *.txt > $list_txt
if [ -f $outfile ]; then
	echo exist
	rm $outfile
fi
touch $outfile
cat $list_fits | while read filename
do
	echo $filename
	time_tai=$(imhead ${filename} l+ | grep 'DATE-OBS=' | cut -d "'" -f 2) #read the observeation time(TAI)
	#echo $time_tai
	t_jd=$(python tai2jd.py $time_tai)
	#echo $t_jd
	echo ccdhedit\(\"${filename}\",\"JD\",\"${t_jd}\",type=\"string\"\) >> $outfile
done
