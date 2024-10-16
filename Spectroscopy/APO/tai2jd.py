#!/bin/env python
### transfer TAI time to JD
import sys
from astropy.time import Time

if __name__ == '__main__':
	t_tai=[]
	times=sys.argv[1]
	t_tai.append(times)
	t=Time(t_tai,format='isot',scale='tai')
	t_jd=str(round(t.jd[0],4))
	print t_jd
