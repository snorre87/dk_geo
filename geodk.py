import pickle
import requests
import os
if not os.path.isfile('geo_lookups.pkl'):
    with open('geo_lookups.pkl','wb') as f:
        f.write(requests.get('https://github.com/snorre87/dk_geo/raw/main/geo_lookups.pkl').content)
        f.close()
pn2pnum,pnr2kom,p2kom,kom2reg,kom2reg,reg2reg,sogn2zip,lat_lookups = pickle.load(open('geo_lookups.pkl','rb'))
pnum2pn = {j:i for i,j in pn2pnum.items()}
final_regs = set(reg2reg.values())
version = 0.1
reg2main = {'Bornholm': 'Bornholm',
 'Byen København': 'Sjælland',
 'Fyn': 'Fyn',
 'Københavns omegn': 'Sjælland',
 'Nordjylland': 'Jylland',
 'Nordsjælland': 'Sjælland',
 'Sydjylland': 'Jylland',
 'Vest- og Sydsjælland': 'Sjælland',
 'Vestjylland': 'Jylland',
 'Østjylland': 'Jylland',
 'Østsjælland': 'Sjælland'}
def get_geo_info(geoname):
    info = {}
    assert type(geoname)==str, 'Input has to be string'
    ds = [pn2pnum,(pnr2kom,p2kom),(kom2reg,kom2reg),reg2reg]
    typs = ['Postnummer','Kommune','Landsdel','Region']
    ### Fix for DST.dks use of Region.
    geoname = geoname.replace('Region ','')
    ###
    if geoname in sogn2zip:
        info['Sogn'] = geoname
        geoname = sogn2zip[geoname]
        try:
            # get postnummer navn
            geoname = pnum2pn[geoname]
        except:
            pass
    for i in range(len(typs)):
        typ,d = typs[i],ds[i]
        # check if input is either region, kommune, or postnr.
        if type(d)==tuple:
            for di in d:
                if geoname in di:
                    info[typ] = di[geoname]
                    if i==0:
                        info['Postnummer_Navn'] = geoname
                    else:
                        info[typs[i-1]] = geoname
                    geoname = info[typ]
        else:
            if geoname in d:
                info[typ] = d[geoname]
                if i==0:
                    info['Postnummer_Navn'] = geoname
                else:
                    info[typs[i-1]] = geoname
                geoname = info[typ]
    if geoname in final_regs:
        info['Region'] = geoname
    if "Landsdel" in info:
        info['mainland'] = reg2main[info['Landsdel']]
    for key,val in list(info.items()):
        if key=='Postnumer_Navn':
            continue
        if key not in lat_lookups:
            continue
        d = lat_lookups[key]
        if val in d:
            info['%s_latlng'%key] = d[val]
    return info
import math
from numpy import cos, sin, arcsin, sqrt
from math import radians
def haversine(lat1,lon1,lat2,lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * arcsin(sqrt(a))
    km = 6367 * c
    return km

def get_geo_info_latlon(lat,lon):
    dist = []
    for sogn,(lat2,lon2) in lat_lookups['Sogn'].items():
        try: # some values are nan
            dist.append((haversine(lat,lon,lat2,lon2),sogn))
        except:
            pass
    sogn = min(dist)[-1]
    return get_geo_info(sogn)
