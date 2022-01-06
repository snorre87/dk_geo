import pickle
import requests
import os
if not os.path.isfile('geo_lookups.pkl'):
    with open('geo_lookups.pkl','wb') as f:
        f.write(requests.get('https://github.com/snorre87/dk_geo/raw/main/geo_lookups.pkl').content)
        f.close()
pn2pnum,pnr2kom,p2kom,kom2reg,kom2reg,reg2reg,sogn2zip,z2geo,sogn2geo = pickle.load(open('geo_lookups.pkl','rb'))
pnum2pn = {j:i for i,j in pn2pnum.items()}
final_regs = set(reg2reg.values())
version = 0.1
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
    for key,val in list(info.items()):
        if val in z2geo:
            info['zip_lat_lng'] = z2geo[val]
        if val in sogn2geo:
            info['sogn_lat_lng'] = sogn2geo[val]
    return info
