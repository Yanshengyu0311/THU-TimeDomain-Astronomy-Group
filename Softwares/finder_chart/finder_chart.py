#!/home/ysy/anaconda3/envs/Astro/bin/python3.7
from pip import main
def magnitude(RA_DEC):
    from astroquery.sdss import SDSS
    import astropy.units as u
    from astropy import coordinates as coords
    from astropy import units as u
    from astropy.io import fits as FITS
    import matplotlib.pyplot as plt
    import numpy as np
    search_radius =  5 * u.arcmin# 1度内的天体
    target_center = coords.SkyCoord(RA_DEC, unit=(u.hourangle, u.deg), frame='icrs')


    # 获取测光数据
    try:
        phot_data = SDSS.query_sql(f"""
            SELECT ra, dec, petroMag_u, petroMag_g, petroMag_r, petroMag_i, petroMag_z, petroMagErr_u, petroMagErr_g, petroMagErr_r, petroMagErr_i, petroMagErr_z
            FROM PhotoObj
            WHERE
                ra BETWEEN {target_center.ra.deg - search_radius.to(u.deg).value} AND {target_center.ra.deg + search_radius.to(u.deg).value}
                AND dec BETWEEN {target_center.dec.deg - search_radius.to(u.deg).value} AND {target_center.dec.deg + search_radius.to(u.deg).value}
            """)
        phot_data = phot_data.to_pandas()
        phot_data_selected= phot_data[phot_data['petroMag_u'] <=20.0]
        phot_data_selected= phot_data_selected[phot_data_selected['petroMagErr_u'] <0.3]
        phot_data_selected= phot_data_selected[phot_data_selected['petroMagErr_g'] <0.3]
        phot_data_selected= phot_data_selected[phot_data_selected['petroMagErr_r'] <0.3]
        return phot_data_selected.reset_index()
    except:
        import requests
        import os
        import numpy as np
        from astropy.io.votable import parse_single_table
        mindet=1
        server=('https://archive.stsci.edu/'+'panstarrs/search.php')
        params = {'RA': target_center.ra.degree, 'DEC': target_center.dec.degree,
                    'SR': search_radius.to_value(u.deg), 'max_records': 10000,
                    'outputformat': 'VOTable',
                    'ndetections': ('>%d' % mindet)}
        response = requests.get(server,params = params)
        
        with open('temp.xml', "wb") as f:
            f.write(response.content)
        chosen_catalog=parse_single_table('temp.xml')
        os.remove('temp.xml')
        phot_data = chosen_catalog.to_table(use_names_over_ids=True).to_pandas()
        phot_data.rename(columns = {"raMean":"ra"},inplace=True)
        phot_data.rename(columns = {"decMean":"dec"},inplace=True)
        phot_data.rename(columns = {"gMeanPSFMagErr":"petroMagErr_g"},inplace=True)
        phot_data.rename(columns = {"iMeanPSFMagErr":"petroMagErr_i"},inplace=True)
        phot_data.rename(columns = {"rMeanPSFMagErr":"petroMagErr_r"},inplace=True)
        phot_data.rename(columns = {"rMeanPSFMag"   :"petroMag_r"   },inplace=True)
        phot_data_selected= phot_data         [phot_data         ['petroMag_r'   ] <=20.0]
        phot_data_selected= phot_data_selected[phot_data_selected['petroMagErr_g'] <0.3]
        phot_data_selected= phot_data_selected[phot_data_selected['petroMagErr_r'] <0.3]
        phot_data_selected= phot_data_selected[phot_data_selected['petroMagErr_i'] <0.3]
        return phot_data_selected.reset_index()

def match_star(phot_data_selected,ra,dec):
    from astropy import coordinates as coords
    target_coord = coords.SkyCoord("%s %s"%(ra,dec), unit=(u.hourangle, u.deg), frame='icrs')
    dist_target2star=(target_coord.ra.deg -phot_data_selected["ra"])**2+\
                     (target_coord.dec.deg-phot_data_selected["dec"])**2
    matched_catalog=phot_data_selected.iloc[dist_target2star.idxmin()]
    return matched_catalog

def Line(Ra1,Ra2,Dec1,Dec2):
    ra1=Ra1.to_string(sep=":",format="hms")
    ra2=Ra2.to_string(sep=":",format="hms")
    dec1=Dec1.to_string(sep=":",format="dms")
    dec2=Dec2.to_string(sep=":",format="dms")
    l="line(" + ra1 + "," + dec1 + "," + ra2 + "," + dec2 + ")"
    return l
def CrossShape(Ra,Dec,scale=0.7,fmt=" # line=0 0 color=red width=4"):
    scale = scale * u.arcmin

    Line1=Line(
        Ra,
        Ra,
        Dec-5*u.arcsec,
        Dec-5*u.arcsec-scale,
    )
    Line2=Line(
        Ra-5*u.arcsec,
        Ra-5*u.arcsec-scale/np.cos(Dec.to_value(u.rad)),
        Dec,
        Dec,
    )
    Line1 = Line1 + fmt
    Line2 = Line2 + fmt

    return Line1,Line2

if __name__ == '__main__':
    import numpy as np
    import os
    import optparse
    import sys
    parser = optparse.OptionParser()
    parser.add_option('--name',"-n","-N", 
                    dest='name',
                    default="Target",
                    help='name of the target') 
    parser.add_option('--coordinate',"-c","-C",
                    dest='coordinate',
                    default="00:00:00.00 +00:00:00.000,00 00 00.00 +00 00 00.000",
                    help='coordinate of the target and offset stars') 
    

    opt,args = parser.parse_args()
    target_name = opt.name
    target_coord= (opt.coordinate).split(",")[0]
    offset_coord= (opt.coordinate).split(",")[1:]

    from astropy import units as u
    from astropy import coordinates as coords
    from astropy.coordinates import SkyCoord

    target_RA    =target_coord.split(" ")[0]
    target_DEC   =target_coord.split(" ")[-1]
    target_RA_u  =coords.Angle(target_RA+ " hours")
    target_DEC_u =coords.Angle(target_DEC,unit=u.deg)

    S =1 * u.arcmin
    S1=S / np.cos(target_DEC_u.to_value(u.rad))
    Region =[]
    Region.append("# Region file format: DS9 version 4.1")
    Region.append('global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1')
    Region.append('fk5')

    SDSS_catalog=magnitude("%s %s"%(target_RA_u,target_DEC_u,))
    
    # 添加目标源
    l1,l2=CrossShape(
        target_RA_u,
        target_DEC_u,
        fmt=" # line=0 0 color=red width=4"
        )
    Region.append(l1)
    Region.append(l2)
    Region.append('# text('+\
        (target_RA_u  -  0.5 * S).to_string(sep=":",format="hms") +',' + \
        (target_DEC_u -  0.1 * S).to_string(sep=":",format="dms") +   \
        ') textangle=0 textrotate=0 color=red width=3 font="helvetica 14 bold roman"  text={'+target_name+"}")


    # 添加参考星
    for i in range(len(offset_coord)):
        c = SkyCoord(offset_coord[i], unit=(u.hourangle, u.deg)).to_string('hmsdms')
        offset_star_ra =c.split()[0]
        offset_star_dec=c.split()[1]
        offset_star_RA_u  =coords.Angle(offset_star_ra)
        offset_star_DEC_u =coords.Angle(offset_star_dec,unit=u.deg)
        
        starselected=match_star(SDSS_catalog,offset_star_RA_u,offset_star_DEC_u)
        offset_star_RA_u  =coords.Angle(starselected['ra'] ,unit=u.deg,).to(unit=u.hourangle)
        offset_star_DEC_u =coords.Angle(starselected['dec'],unit=u.deg,)
        
        l1,l2=CrossShape(
            offset_star_RA_u,
            offset_star_DEC_u,
            fmt=" # line=0 0 color=yellow width=4"
            )
        Region.append(l1)
        Region.append(l2)

        Region.append('# text('+\
            (offset_star_RA_u  -  0.5 * S).to_string(sep=":",format="hms") +',' + \
            (offset_star_DEC_u -  0.1 * S).to_string(sep=":",format="dms") +   \
            ') textangle=0 textrotate=0 color=yellow width=3 font="helvetica 14 bold roman"  text={Offset Star '+str(i+1)+"}")


        x=offset_star_ra.replace("h",":").replace("m",":").replace("s","")
        y=offset_star_dec.replace("d",":").replace("m",":").replace("s","")
        Region.append('# text('+\
            (offset_star_RA_u  -  0.6 * S).to_string(sep=":",format="hms") +',' + \
            (offset_star_DEC_u -  0.2 * S).to_string(sep=":",format="dms") +   \
            ') textangle=0 textrotate=0 color=yellow width=3 font="helvetica 10 bold roman"  text={' + \
            x +" "+ y +"}")


        E_offset = "%.2f" %((target_RA_u -offset_star_RA_u ).to_value(u.arcsec)* np.cos(offset_star_DEC_u.to_value(u.rad))) 
        W_offset = "%.2f" %((target_DEC_u-offset_star_DEC_u).to_value(u.arcsec))
        
        Region.append(
            '# text('+
            (target_RA_u      ).to_string(sep=":",format="hms") +','+
            (target_DEC_u + (2.0-i*0.5)*S).to_string(sep=":",format="dms") +
            ') textangle=0 textrotate=0 color=white width=3 font="helvetica 14 bold roman" text={Offst Star '+str(i+1)+", r~%.2f mag, "%(starselected["petroMag_r"])+
            "East Offset= "  +E_offset +'",'+
            "North Offset = "+W_offset +'"}'
        )

    # 添加尺子
    Region.append(Line(target_RA_u - 1*S1, \
        target_RA_u - 2*S1, \
        target_DEC_u-3*S, \
        target_DEC_u-3*S)+\
        " # line=0 0 color=cyan width=4 text={1'}")

    # 添加罗盘
    Region.append('# compass('+\
        (target_RA_u -  4*S).to_string(sep=":",format="hms")+','+\
        (target_DEC_u - 3*S).to_string(sep=":",format="dms")+\
        ',15.00") compass=fk5 {N} {E} 1 1 color=cyan width=4 font="helvetica 14 normal roman"')

    # 添加文本
    Region.append(
        '# text('+
        (target_RA_u       ).to_string(sep=":",format="hms") +','+
        (target_DEC_u + 3*S).to_string(sep=":",format="dms") +
        ') textangle=0 textrotate=0 color=red width=3 font="helvetica 14 bold roman" text={'+target_name+" RA="+target_RA+" DEC="+target_DEC+"}"
    )
    Region.append(
        '# text('+
        (target_RA_u        ).to_string(sep=":",format="hms") +','+
        (target_DEC_u +2.5*S).to_string(sep=":",format="dms") +
        ') textangle=0 textrotate=0 color=white width=3 font="helvetica 14 bold roman" text={From offset star to target:}'
    )

    with open('main.reg','w') as REG:
        for ll in Region:
            print(ll)
            REG.write(ll+'\n')

    print('-'*60)
    print('sudo ds9 -log -lock frame wcs -view layout vertical *.fits -regions main.reg')



