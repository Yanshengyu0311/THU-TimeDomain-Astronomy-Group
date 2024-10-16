procedure newspec()

string  im       {prompt="Input image"}
bool    bf       {no,prompt="If get keyword from file?"}
string  keyfile  {prompt="file containing key word"}
string  format   {"",prompt="Filename objname type btime exptime ra dec epoch"}
string  obj      {prompt="Object  name which input into imheader"}
string  type     {enum="object|standard|comp|flat|zero|dark",prompt="Image type"}
string  btime    {prompt="The Beijing time of object image observed"}
string  exptime  {prompt="Exposure time of object"}
string  ra       {prompt="Object Ra"}
string  dec      {prompt="Object Dec"}
real    epoch    {prompt="Object epoch"}
struct*  list1

begin

	string dmy,dmy1,dmy2
	string tmp1,tmp2
	int    day,month,year
	real   wtime
	string str1,str2,str3,str4,str5,str6,str7,str8,stime
	string tmp


	noao
	imred 
	ccdred
	astutil
#get information from task parameter and write into image header
	if (bf==no)  {
	   ccdhedit(im,"object",obj,type="string")
	   ccdhedit(im,"title",obj,type="string")
	   ccdhedit(im,"IMAGETYP",type,type="string")
	   ccdhedit(im,"BT",btime,type="string")
#	   ccdhedit(im,"dispaxis",1,type="string")
	   if (type=="object"||type=="comp"||type=="standard") {
	     ccdhedit(im,"ra",ra,type="string")
	     ccdhedit(im,"dec",dec,type="string")
	     ccdhedit(im,"epoch",epoch,type="real")
           }
	}
#get information from keyfile and write into image header
	else {
	   list1=keyfile
	#get day/month/year from keyfile 
	   tmp=fscan(list1,dmy1)
	   tmp=fscan(list1,dmy2)

	   while(fscan(list1,im,obj,type,btime,exptime,ra,dec,epoch) != EOF) {
		ccdhedit(im,"object",obj,type="string")
		ccdhedit(im,"title",obj,type="string")
		ccdhedit(im,"IMAGETYP",type,type="string")
	   	ccdhedit(im,"BT",btime,type="string")
#                ccdhedit(im,"dispaxis",1,type="string")
		if(type=="object"||type=="comp"||type=="standard") {
		  ccdhedit(im,"ra",ra,type="string")
		  ccdhedit(im,"dec",dec,type="string")
		  ccdhedit(im,"epoch",epoch,type="real")
		}

       # Image header already has 'EXPTIME'   Cao 06/02/04
       #get exposure time from image header
		imgets(im,"EXPTIME")         
		exptime=imgets.value

		wtime=real(btime)
		dmy=dmy1
		if(wtime >= 24.0)
		  { dmy=dmy2
		    wtime=wtime-24.0 }
	#seperate day month year
		 print(dmy) | scan(day)
		 i=stridx("/",dmy)
		 tmp1=substr(dmy,i+1,i+10)
		 print(tmp1) | scan(month)
		 i=stridx("/",tmp1)
		 tmp2=substr(tmp1,i+1,i+6)
		 print(tmp2) | scan(year)

	#insert date,time and exposure to image header
	#inorder to get a good look header, delete a few parameter first
		hedit(im,"DATE-OBS","",add-,delete+,verify-,show-)
		hedit(im,"TIME","",add-,delete+,verify-,show-)
	#	hedit(im,"EXPOSURE","",add-,delete+,verify-,show-)

		ccdhedit(im,"DATE-OBS",dmy1,type="string")
		ccdhedit(im,"EXPOSURE",exptime,type="string")
	#	ccdhedit(im,"EXPTIME",exptime,type="string")
		ccdhedit(im,"BT",btime,type="string")
		ccdhedit(im,"OBSERVAT","BAO")

		if(type=="object"||type=="comp"||type=="standard") 
		{
	#caculating siderial time and write in image header
		if(access("tmpcao"))
		  delete("tmpcao",verify-)

asttimes(observatory="BAO",header-,year=year+2000,month=month,day=day,time=wtime,>>"tmpcao")	
		list="tmpcao"
#		tmp1=fscan(list)
#		tmp1=fscan(list)
#		tmp1=fscan(list)
#		tmp1=fscan(list)
		tmp1=fscan(list,str1,str2,str3,str4,str5,str6,str7,str8,stime)
		!rm -f "tmpcao"
#		!/usr/bin/rm "tmpcao"

		ccdhedit(im,"UT",str6,type="string")
		ccdhedit(im,"ST",stime,type="string")
		ccdhedit(im,"JD",str8,type="string")
setairmass(im,observatory="BAO",intype="beginning",outtype="effective",date="date-obs",exposure="exposure",airmass="airmass",utmiddle="utmiddle",show+,update+,override+)
print("###   ",im,"   ","date  -- ",dmy,"   st=",stime)
print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
		}
	}
}
end
