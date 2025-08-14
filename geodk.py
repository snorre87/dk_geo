import pickle
import requests
import os
if not os.path.isfile('geo_lookups.pkl'):
    with open('geo_lookups.pkl','wb') as f:
        f.write(requests.get('https://github.com/snorre87/dk_geo/raw/main/geo_lookups.pkl').content)
        f.close()
if not os.path.isfile('stringlookuplats.pkl'):
    with open('stringlookuplats.pkl','wb') as f:
        f.write(requests.get('https://github.com/snorre87/dk_geo/raw/main/stringlookuplats.pkl').content)            
        f.close()
e2lat = pickle.load(open('stringlookuplats.pkl','rb'))
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




def get_geo_info(geoname,trust_zizpcodes = True):
    
    assert type(geoname)==str, 'Input has to be string'
    info = {'string':geoname}
    geoname = geoname.strip()
    ds = [pn2pnum,(pnr2kom,p2kom),(kom2reg,kom2reg),reg2reg]
    typs = ['Postnummer','Kommune','Landsdel','Region']
    ### Fix for DST.dks use of Region.
    geoname = geoname.replace('Region ','')
    ###
    
    if geoname in sogn2zip or geoname+' Sogn' in sogn2zip:
        if not geoname in sogn2zip:
            geoname = geoname+' Sogn'
        info['Sogn'] = geoname
        info['match'] = 'Sogn'
        info['match_level'] = 0
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
                    if not 'match' in info:
                        info['match'] = typs[i-1]
                        info['match_level'] = i+1
                    info[typ] = di[geoname]
                    if i==0:
                        info['Postnummer_Navn'] = geoname
                    else:
                        info[typs[i-1]] = geoname
                    geoname = info[typ]
        else:
            if geoname in d:
                if not 'match' in info:
                    info['match'] = typ
                info[typ] = d[geoname]
                if i==0:
                    info['Postnummer_Navn'] = geoname
                else:
                    info[typs[i-1]] = geoname
                geoname = info[typ]
    if geoname in final_regs:
        info['Region'] = geoname
        if not 'match' in info:
            info['match'] = 'Region'
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
    if len(info)==1:
        return {}
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
        return {}
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



pnr_names = set(p2kom)
geonames = set(e2lat)|pnr_names
dkZIP = set(pnr2kom)

l = pn2pnum,pnr2kom,p2kom,kom2reg,kom2reg,reg2reg,sogn2zip
from collections import Counter
def clean_ent(i):
    return i.split(' Sogn')[0]
for i in l:    
    for j in i:
        if j.isdigit():
            continue
        geonames.add(clean_ent(j))    
import re
token_re = re.compile('\w+')
zip_re = re.compile(r'\b\d{4}\b')
def extract_geo_ents(string,allow_endings = [],tokenizer=token_re.findall):
    # do a simple match of names
    m = sorted([i for i in geonames if i in string],key=len,reverse=True)
    m2 = []
    tokens = set()
    for i in m:

        if i in tokens:
            continue
        m2.append(i)
        toks = i.split()
        for j in range(len(toks)):
            tokens.add(toks[j])
            gram = ' '.join(toks[j:j+2])
            tokens.add(gram)
        #s = set(toks)
        #if len(s)==len(s&tokens):
        #    continue
        
        for t in toks:
            tokens.add(t)
            
    m = m2
    zips = list(set(zip_re.findall(string))&dkZIP-tokens)
    if len(m)==0 and len(zips)==0:
        return [],[]
    # separate into uni- bi and trigrams. and zipcodes
    uni,ngrams = [],[]
    for i in m:
        ng = len(i.split())
        if ng>1:
            ngrams.append(i)
        else:
            uni.append(i)
    
    # assume ngrams are matched.
    ents = ngrams
    # look for tokens
    if len(uni)>0:
        tokens = set(tokenizer(string))
        for e in uni:
            if e in tokens:
                ents.append(e)
    return ents,zips

def get_ent_info(ents,zips,trust_zipcodes = True,get_ambigues=False):
    # first check if some of the ents are in the administrative data
    l = []
    for e in ents:
        d = get_geo_info(e)
        d['matchtype'] = 'admin'
        if e in e2lat:
            ex = e2lat[e]
            d['naddresses'] = ex['naddresses']
        if len(d)>0:
            l.append(d)
        else:
            ex = e2lat[e]
            latlon = ex['latlon']
            d = get_geo_info_latlon(*latlon)
            d['matchtype'] = 'city-area'
            d['matchn' ] = ex['count']
            d['naddresses'] = ex['naddresses']
            l.append(d)
            if ex['count']>1:
                if get_ambigues:
                    for lat,lon in ex['extra'][1:]:
                        d = get_geo_info_latlon(*latlon)
                        d['matchtype'] = 'city-area'
                        d['matchn' ] = e[e]
                        d['match_aux'] = True
                        l.append(d)
    l2 = []   
    for z in zips:
        d = get_geo_info(z)
        d['matchtype'] = 'zipcode'
        if len(d)>0:
            if trust_zipcodes:
                l.append(d)
            else:
                l2.append(d)
    if len(l2)>0:
        # compare results
        # check if same municipality and keep zipcode if matching.
        if len(l):
            temp = pd.DataFrame(l)
            if 'Kommune' in temp.columns:
                s = set(temp.Kommune)
                l2 = [i for i in l2 if i['Kommune'] in s]
                
                if len(l2)>0:
                    l = l2
    
    return l
def get_geo_string(string,trust_zipcodes=True):
    ents,zips = extract_geo_ents(string)
    l = get_ent_info(ents,zips,trust_zipcodes)
    return l
