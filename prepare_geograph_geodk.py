import pickle
import requests,json
import os
from collections import Counter

ready = True
for fn in ['dkpolygons.pkl','dkpolygons2.pkl','kode2area.json','geo-entity_graph.json',
           'kode2namelookup.json']:
    if not os.path.isfile(fn):
        ready = False

if not ready:
    print('will collect polygons and prepare geo-entity-graph')
    print('will take a while')
    
    from shapely.geometry import Point, Polygon
    
    
    q_gdf = {}    
    types = ['afstemningsomraader',
     'ejerlav',
    # 'jordstykker',
     'kommuner',
     'landsdele',
     'menighedsraadsafstemningsomraader',
     'opstillingskredse',
     'politikredse',
     'postnumre',
     'regioner',
     'retskredse',
     'sogne',
     'supplerendebynavne2']
    # 'valglandsdele',
    #'storkredse']
    
    print('Collecting polygon data from api.dataforsyningen')
    for key in tqdm(types):
        if key in q_gdf:
            continue
        base = "https://api.dataforsyningen.dk/%s"%key
        params = {
                "format": "geojson"
            }
        resp = requests.get(base, params=params)
        resp.raise_for_status()
        gj = resp.json()    
        df = gpd.GeoDataFrame.from_features(gj["features"])
        print(key,df.shape)
        q_gdf[key] = df
    # format 
    kode_keys = ['nr','kode','dagi_id']
    def construct_kode(df,dfkey):
        l = []
        for i in kode_keys:
            if i in df.columns:
                key = i
                break
        df['ID'] = df[key].apply(lambda x: '%s_%s'%(dfkey,x))
        df['name'] = df['navn']
        return df
    
    for q in q_gdf:
        q_gdf[q] = construct_kode(q_gdf[q],q)
        if q=='postnumre':
            df = q_gdf[q]
            l = []
            for nr,navn in df[['nr','navn']].values:
                l.append('%s %s'%(nr,navn))
            df['name'] = l
            q_gdf[q] = df
        if q=='sogne':
            df = q_gdf[q]
            l = []
            for navn in df['navn'].values:
                if not 'Sogn' in navn:
                    
                    l.append('%s Sogn'%(navn))
                else:
                    l.append(navn)
            df['name'] = l
            q_gdf[q] = df
    k2name = {}
    for typ in q_gdf:
        temp = q_gdf[typ]
        for k,n in temp[['ID','name']].values:
            
            k2name[k] = n
    name2k = {name:[] for name in set(k2name.values())}
    for k,n in k2name.items():
        name2k[n].append(k)   
    json.dump([k2name,name2k],open('kode2namelookup.json','w'))
    print('extracting polygons')
    def extract_polygons(q_gdf):
        polygons = {}
        centroids = {}
        #polygons2 = {}
        for q in q_gdf:
            gdf = q_gdf[q]
            #cols = gdf.columns
            for p,geo in gdf[['ID','geometry']].values:
                if geo==None:
                    continue
                
                lon,lat = geo.centroid.coords.xy[0].tolist()[0],geo.centroid.coords.xy[1].tolist()[0]
                
                try:
                    polygons[p]['polygon'].append(geo)
                    polygons[p]['centroids_latlon'].append((lat,lon))
                except:
                    polygons[p]= {'polygon': [geo],'centroids_latlon':[(lat,lon)]}
                
                #centroids['%s_%s'%(q,p)] = lat,lon
        return polygons
    polygons = extract_polygons(q_gdf)
        
    def extract_multipol(geo):
        geos = geo.geoms
        pols = []
        for i in geos:
            bounds = i.exterior.xy
            pol = list(zip(bounds[0],bounds[1]))
            interiors = []
            for j in range(3):
                temp = i.interiors._get_ring(j)
                if temp!=None:
                    interior = list(zip(temp.xy[0],temp.xy[1]))
                    interiors.append(interior)    
            d = {'polygon':pol}
            if len(interiors)>0:
                d['interior'] = interiors
            pols.append(d)
        return pols
    def extract_polygon_to_list(q_gdf):
        polygons = {}
        centroids = {}
        for q in q_gdf:
            gdf = q_gdf[q]
            for p,geo in gdf[['ID','geometry']].values:
                if geo==None:
                    continue
                
                lon,lat = geo.centroid.coords.xy[0].tolist()[0],geo.centroid.coords.xy[1].tolist()[0]
                pol = extract_multipol(geo)
                if not p in polygons:
                    polygons[p] = {}
                    polygons[p]['polygon'] = pol
                    polygons[p]['centroid_latlon'] = [(lat,lon)]
        return polygons
    polygons2 = extract_polygon_to_list(q_gdf)
    
    import pickle
    pickle.dump(polygons,open('dkpolygons.pkl','wb'))
    pickle.dump(polygons2,open('dkpolygons2.pkl','wb'))
    print('building entity graph')
    l = {}
    geo2sub = {}
    l ={}
    c = Counter()
    pols = list(polygons)
    import random
    random.shuffle(pols)
    for i in tqdm(range(len(polygons)-1)):
        key = pols[i]
        pls = polygons[key]['polygon']
        typ = key.split('_')[0]
        for j in range(i+1,len(polygons)):
            key2 = pols[j]
            typ2 = key2.split('_')[0]
            if typ==typ2:
                continue
            pls2 = polygons[key2]['polygon']
            for num,p in enumerate(pls):
                for num2,p2 in enumerate(pls2):
                    #skey = '%s_%d'%(key,num) 
                    #skey2 = '%s_%d'%(key2,num2) 
                    skey = key
                    skey2 = key2
                    if not skey in G:
                        G[skey] = []
                    if not skey2 in G:
                        G[skey2] = []
                    if p.intersects(p2):
                        G[skey].append(skey2)
                        G[skey2].append(skey)
    
    for i in G:
       G[i] = set(G[i])
    len(G),len(name2k),len(k2name)#,sum(l.values()),len(l)
    
    k2area = {k:geo['polygon'][0].area for k,geo in polygons.items()}
    G_w = {k:{} for k in G}
    dat = []
    
    
    for k in tqdm(G):
        s = G[k]
        geo = polygons[k]['polygon'][0]
        a = k2area[k]
        for j in s:
            if j in G_w[k]:
                continue
            geo2 = polygons[j]['polygon'][0]
            oa = geo.intersection(geo2).area
            a2 = k2area[j]
            p = oa/min([a,a2])
            dat.append({'k':k,'k2':j,'a':a,'a2':a2,'p':p,'oa':oa})
            G_w[k][j] = p
            G_w[j][k] = p
    oadf = pd.DataFrame(dat)
    
    oadf.to_csv('geo-entity_graph_weights.csv')
    
    # fix problem with some zipcodes being to large (covering ocean)
    for i in tqdm(G_w):
        temp = G_w[i]
        typs = set([j.split('_')[0] for j in temp])
        for typ in typs:
            t = [j for j in temp if j.split('_')[0]==typ]
            for num,j in enumerate(sorted(t,key=lambda x: temp[x],reverse=True)):
                if G_w[i][j]==0:
                    del G_w[i][j]
                G_w[i][j] = (num,G_w[i][j])
    json.dump(G_w,open('geo-entity_graph.json','w'))
    
    json.dump(k2area,open('kode2area.json','w'))
    print('Done building entity graph')
