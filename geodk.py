import pickle
import requests
import os
if not os.path.isfile('geo_lookups.pkl'):
    with open('geo_lookups.pkl','wb') as f:
        f.write(requests.get('https://github.com/snorre87/dk_geo/raw/main/geo_lookups.pkl').content)
        f.close()
if not os.path.isfile('kom2kode.pkl'):
    # kom2code = dict(pd.read_html('https://www.dst.dk/da/Statistik/dokumentation/Times/stofmisbrug/kommunekode')[0][['Tekst','Kode']].values)
    # pickle.dump(kom2code,open(path+'kom2code.pkl','wb'))
    with open('kom2kode.pkl','wb') as f:
        f.write(requests.get('https://github.com/snorre87/dk_geo/raw/main/kom2kode.pkl').content)
        f.close()

pn2pnum,pnr2kom,p2kom,kom2reg,kom2reg,reg2reg,sogn2zip,lat_lookups = pickle.load(open('geo_lookups.pkl','rb'))
pnum2pn = {j:i for i,j in pn2pnum.items()}
final_regs = set(reg2reg.values())
kom2code = pickle.load(open('kom2kode.pkl','rb'))
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

dk_polygons = [
    # DK
    [(8.1, 54.5), (8.1, 57.8), (12.7, 57.8), (12.7, 54.5), (8.1, 54.5)],
     # Bornholm
    [(14.6, 54.9), (14.6, 55.3), (15.3, 55.3), (15.3, 54.9), (14.6, 54.9)],
     # Greenland
    [(-75.0, 59.0), (-75.0, 83.0), (-10.0, 83.0), (-10.0, 59.0), (-75.0, 59.0)],
    # Faroe Islands 
    [(-7.8, 61.2), (-7.8, 62.5), (-6.0, 62.5), (-6.0, 61.2), (-7.8, 61.2)]]
def point_in_polygon(lon, lat, polygon):
    """
    Ray casting algorithm for testing if a point is inside a polygon.
    polygon: list of (lon, lat) tuples.
    """
    inside = False
    n = len(polygon)
    
    for i in range(n - 1):
        x1, y1 = polygon[i]
        x2, y2 = polygon[i + 1]
        
        # Check if the latitude is between the y-coords of the edge
        if ((y1 > lat) != (y2 > lat)):
            # Find x coordinate where the line at 'lat' crosses the edge
            x_intersect = x1 + (lat - y1) * (x2 - x1) / (y2 - y1)
            if x_intersect > lon:
                inside = not inside
                
    return inside
def is_in_denmark(lat, lon):
    """Check if (lat, lon) is inside Denmark's bounding polygon."""
    for pol in dk_polygons:
        val = point_in_polygon(lon, lat, pol)
        if val == True:
            return True
    return False




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
    if 'Kommune' in info:
        kom = info['Kommune']
        try:
            k_code = kom2code[kom]
            info['Kommune_kode'] = k_code
        except:
            pass

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
    "Geographical Info is inferred from the nearest locating the nearest Sogn (not a bounding box)."
    indk = is_in_denmark(lat,lon)
    if not indk:
        return {'Sogn':'Not in DK'}
    dist = []
    for sogn,(lat2,lon2) in lat_lookups['Sogn'].items():
        try: # some values are nan
            dist.append((haversine(lat,lon,lat2,lon2),sogn))
        except:
            pass
    sogn = min(dist)[-1]
    info = get_geo_info(sogn)
    info['distance_closest_sogn_km'] = min(dist)[0]
    return info
