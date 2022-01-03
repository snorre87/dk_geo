import pickle
import requests
with open('geo_lookups.pkl','wb') as f:
    f.write(requests.get('https://github.com/snorre87/dk_geo/raw/main/geo_lookups.pkl').content)
    f.close()
pn2pnum,pnr2kom,p2kom,kom2reg,kom2reg,reg2reg,sogn2zip = pickle.load(open('geo_lookups.pkl','rb'))
pnum2pn = {j:i for i,j in pn2pnum.items()}
def get_geo_info(geoname):
    info = {}
    assert type(geoname)==str, 'Input has to be string'
    ds = [pn2pnum,(pnr2kom,p2kom),(kom2reg,kom2reg),reg2reg]
    typs = ['Postnummer','Kommune','Landsdel','Region']
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
    return info
