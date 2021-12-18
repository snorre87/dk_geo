import pickle
import requests
import os
if not os.path.isfile('geo_lookups.pkl'):
    with open('geo_lookups.pkl','wb') as f:
      f.write(requests.get('https://github.com/snorre87/dk_geo/raw/main/geo_lookups.pkl').content)
      f.close()
pn2pnum,pnr2kom,p2kom,kom2reg,kom2reg,reg2reg = pickle.load(open('geo_lookups.pkl','rb'))

def get_geo_info(geoname):
  info = {}
  for typ,d in zip(['Post_nummer','Kommune','Landsdel','Region'],[pn2pnum,(pnr2kom,p2kom),(kom2reg,kom2reg),reg2reg]): #
    # check if input is either region, kommune, or postnr.
    if typ=='Region':
        print(geoname)
        print(geoname in d)
    if type(d)==tuple:
      for di in d:
        if geoname in di:
          info[typ] = di[geoname]
          if typ=='Kommune':
            info['Postnummer'] = geoname

            geoname = info[typ]
          if typ=='Post_nummer':
            info['Navn'] = geoname
          if typ=='Landsdel':
            info['Kommune'] = geoname

    else:
      if geoname in d:
        info[typ] = d[geoname]
        if typ=='Kommune':
          info['Postnummer'] = geoname
        if typ=='Post_nummer':
            info['Navn'] = geoname
        if typ=='Landsdel':
            info['Kommune'] = geoname
        geoname = info[typ]
  return info
