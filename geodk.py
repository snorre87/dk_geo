import pickle
import requests,json
import os
from collections import Counter
if not os.path.isfile('dkpolygons.pkl'):
    with open('dkpolygons.pkl','wb') as f:
        f.write(requests.get('https://github.com/snorre87/dk_geo/raw/main/dkpolygons.pkl').content)            
        f.close()
    with open('dkpolygons2.pkl','wb') as f:
        f.write(requests.get('https://github.com/snorre87/dk_geo/raw/main/dkpolygons2.pkl').content)    
        f.close()
if not os.path.isfile('geo-entity_graph.json'):
    with open('geo-entity_graph.json','w') as f:
        f.write(requests.get('https://github.com/snorre87/dk_geo/raw/main/geo-entity_graph.json').content)            
        f.close()
if not os.path.isfile('kode2namelookup.json'):
    with open('kode2namelookup.json','w') as f:
        f.write(requests.get('https://github.com/snorre87/dk_geo/raw/main/kode2namelookup.json').content)            
        f.close()

if not os.path.isfile('kode2area.json'):
    with open('kode2area.json','w') as f:
        f.write(requests.get('https://github.com/snorre87/dk_geo/raw/main/kode2area.json').content)            
        f.close()





version = 0.2
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

dk_bbox_refs = ['DK','Bornholm','Greenland','Faroe Islands']
dk_polygons = [
    # DK
    [(8.1, 54.5), (8.1, 57.8), (12.7, 57.8), (12.7, 54.5), (8.1, 54.5)],
     # Bornholm
    [(14.6, 54.9), (14.6, 55.3), (15.3, 55.3), (15.3, 54.9), (14.6, 54.9)],
     # Greenland
    [(-75.0, 59.0), (-75.0, 83.0), (-10.0, 83.0), (-10.0, 59.0), (-75.0, 59.0)],
    # Faroe Islands 
    [(-7.8, 61.2), (-7.8, 62.5), (-6.0, 62.5), (-6.0, 61.2), (-7.8, 61.2)]]

def is_in_polygon_pure(lon,lat,polygon):
    xs, ys = zip(*polygon)
    if not (min(xs) <= lon <= max(xs) and min(ys) <= lat <= max(ys)):
        return False
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

try:
    from shapely.geometry import Point, Polygon
    def is_in_polygon(lon,lat,polygon):
        if type(polygon)==list:
            return is_in_polygon_pure(lon,lat,polygon)
        p = Point((lon,lat))
        return polygon.contains(p)
    print('Shapely as backend')
except Exception as e:
    print(str(e))
    print('shapely is probably not installed')



try:
    import geopandas as gpd
    polygons = pickle.load(open('dkpolygons.pkl','rb'))
except:
    print('geopandas not installed will use pure python method')
    polygons = pickle.load(open('dkpolygons2.pkl','rb'))

def point_in_polygon(lon, lat, polygon,interior=False):
    """
    Ray casting algorithm for testing if a point is inside a polygon.
    polygon: list of (lon, lat) tuples.
    """
    if type(polygon)!=list:
        
        if is_in_polygon(lon,lat,polygon):
            return True
        return False
    if interior!=False:
        for i in interior:
            inside = point_in_polygon(interior)
            if inside:
                return False
    if is_in_polygon_pure(lon,lat,polygon):
        return True
    return False

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


def is_in_denmark(lat, lon):
    """Check if (lat, lon) is inside Denmark's bounding polygon."""
    for num,pol in enumerate(dk_polygons):
        val = point_in_polygon(lon, lat, pol)
        if val == True:
            return dk_bbox_refs[num]
    return False

def get_graph_overlap(keys):
    c = Counter()
    for key in keys:
        
        for j in G_w[key]:
            if not j in keys:
                c[j]+=1
    return [i for i,count in c.most_common() if count==len(keys)]


def get_geo_info_latlon(inp,lowest_level='sogne',add_all_types=True):
    if type(inp)!=str:
        lat,lon = inp
        d = recursive_lookup(lat,lon,lowest_level=lowest_level)
        if not add_all_types:
            return get_meta_data(d)
        keys = []
        for key in all_types:
            if key in d:
                keys+=d[key]
        susp = get_graph_overlap(keys)
        
        l = []
        for i in susp:
            pls = polygons[i]['polygon']
            for num,geo in enumerate(pls):
                if is_in_polygon(lon,lat,geo):
                    l.append(i) 
        for typ in set([i.split('_')[0] for i in l]):
            temp = [i for i in l if typ==i.split('_')[0]]
            if not typ in d:
                d[typ] = temp
            else:
                print('Not supposed to be like this')
                d[typ]+=temp
        return get_meta_data(d)
    else:
        raise ValueError('Input is malformed')


# get suspects from region to sogn
regioner = [i for i in polygons if 'regioner' in i]
types = ['sogne','postnumre','kommuner','regioner']
all_types = ['sogne','postnumre','opstillingskredse','kommuner','retskredse','politikredse','regioner']
def recursive_lookup(lat,lon,keys=False,typ='regioner',d=False,lowest_level='sogne',types = all_types):
    if keys==False:
        indk = is_in_denmark(lat,lon)
        keys = regioner
        if indk==False:
            return {'indk':False}
        l = []
        for i in keys:
            pls = polygons[i]['polygon']
            for num,geo in enumerate(pls):
                if is_in_polygon(lon,lat,geo):
                    l.append(i)
                    break
                    #l.append('%s_%d'%(i,num))    
        typ = 'regioner'
        d = {typ:l,'indk':indk}
        keys = l
    
    d['latlon'] = (lat,lon)
    typ_key = keys[0].split('_')[0]
    typ_num = types.index(typ)-1
    typ = types[typ_num]
    neighbors = set()
    for key in keys:
        neighbors.update(G_w[key])
    l = []
    
        
    for key in neighbors:
        
        typ2 = key.split('_')[0]
        if typ2!=typ:
            continue 
    
        #k,num = key.rsplit('_',maxsplit=1)
        #num = int(num)
        k = key
        geo = polygons[k]['polygon'][0]
        if is_in_polygon(lon,lat,geo):
            l.append(key)
    d[typ] = l
    
    if len(l)==0:
        l = keys
    if typ==lowest_level:
        d['latlon_match'] = polygons[keys[0]]['centroids_latlon']
    else:
        d = recursive_lookup(lat,lon,keys=l,typ=typ,d=d,lowest_level=lowest_level,types=types)
    return d



k2name,name2k = json.load(open('kode2namelookup.json','r'))

geoname_types = set([#'ejerlav',
 'kommuner',
 'postnumre',
 'regioner',
  'sogne',
 'supplerendebynavne2'])
# these should be used for geolookup.
# data should be looked up in the Graph.
geonames = set()
for k,name in k2name.items():
    for typ in geoname_types:
        if typ in k:
            geonames.add(name)

dkZIP = set([i.split('_')[1] for i in k2name if 'postnumre' in i])

import re
token_re = re.compile('\w+')
zip_re = re.compile(r'\b\d{4}\b')
sort_geonames = sorted(geonames,key=len,reverse=True)
G_w = json.load(open('geo-entity_graph.json','r'))
k2area = json.load(open('kode2area.json','r'))

def get_meta_data(d):
    new = {}
    for key in d:
        if 'latlon' in key:
            new[key] = d[key]
            continue
        val = d[key]
        if not type(val)==list:
            new[key] = val
            continue
        l = []
        l2 = []
        new['%s_kode'%key] = d[key]
        for i in val:
            name = k2name[i]
            if not name in l:
                l.append(name)
        new[key] = list(l)
    return new


def extract_geo_ents(string,allow_endings = [],tokenizer=token_re.findall):
    # do a simple match of names
    m = [i for i in sort_geonames if i in string]
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
levels = ['afstemningsomraader', 'ejerlav', 'kommuner', 'landsdele', 'menighedsraadsafstemningsomraader', 'opstillingskredse'
          , 'politikredse', 'postnumre', 'regioner'
          , 'retskredse', 'sogne', 'supplerendebynavne2']
typ2level = {'afstemningsomraader':0, 'ejerlav':0, 'kommuner':2, 'landsdele':5, 'menighedsraadsafstemningsomraader':0, 'opstillingskredse':3
          , 'politikredse':3, 'postnumre':1, 'regioner':4
          , 'retskredse':3, 'sogne':0, 'supplerendebynavne2':1}
def get_geo_info_string(string,trust_zips=False
                        ,minimum_intersection=0.05,keep_lowest_match=True,
                       keep_ambivalent=False,keep_match_level_only=True):
    string = str(string)
    
    ents,zips = extract_geo_ents(string)
    dat = []
    if trust_zips:
        for zi in zips:
            
            z = 'postnumre_%s'%zi
            if z in k2name:
                match_level = z.split('_')[0] 
                susp = G_w[z]
                susp = [i for i,(num,j) in susp.items() if j>minimum_intersection or num==0]    
                d = {'match_type':'zipcode','matchlevel':'postnumre','matchlevel_num':typ2level['postnumre'],'match_code':z,'match':zi,'nmatches':1,'postnumre':[zi]} 
                for i in susp:
                    typ = i.split('_')[0]
                    if keep_match_level_only==False:
                        if not typ in d:
                            d[typ] = []
                        d[typ].append(i)
                    else:
                        if typ2level[typ]>=typ2level[match_level]:
                            if not typ in d:
                                d[typ] = []
                            d[typ].append(i)
                dat.append(d) 
    # check if in administrative names:
    for num,ent in enumerate(ents):
        if ent in name2k:
            ks = name2k[ent]
            ks = [i for i in ks if i.split('_')[0] in geoname_types]
            edges = []
            for k in ks:
                
                susp = G_w[k]
                match_level = k.split('_')[0] 
                if not match_level in geoname_types:
                    continue
                susp = [i for i,(num,j) in susp.items() if j>minimum_intersection or num==0]    
                d = {'match_type':'administrative','matchlevel':match_level,'matchlevel_num':typ2level[match_level],'match_code':k,'match':ent,'nmatches':len(ks),'entity_order':num,match_level:[k]}                
                
                for i in susp:
                    typ = i.split('_')[0]
                    if keep_match_level_only==False:
                        if not typ in d:
                            d[typ] = []
                        d[typ].append(i)
                    else:
                        if typ2level[typ]>=typ2level[match_level]:
                            if not typ in d:
                                d[typ] = []
                            d[typ].append(i)
                dat.append(d)
    dat = sorted(dat,key=lambda x: k2area[x['match_code']])
    
    dat = [get_meta_data(i) for i in dat]
    dat2 = [i for i in dat if i['nmatches']==1]
    
    if keep_ambivalent==False:
        dat = dat2
    if keep_lowest_match==False:
        return dat 
    
    dat2 = [i for i in dat if i['nmatches']==1]
    if len(dat2)>0:
        return dat2[0]
    else:
        return {}
def get_geo_info(val,trust_zips=False):
    if type(val)==str:
        return get_geo_info_string(val,trust_zips=trust_zips)
    else:
        return get_geo_info_latlon(lat,lon)
