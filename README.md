# geodk.py
 Script for looking up administrative entitities from latitude and longitude, or by string matching. Build on polygon data from https://api.dataforsyningen.dk. 
```python
import geodk
lat,lon = 55.676098,12.568337
res = geodk.get_geo_info_latlon((lat,lon))
# res
#{'regioner_kode': ['regioner_1084'],
# 'regioner': ['Region Hovedstaden'],
# 'indk': 'DK',
# 'latlon': (55.676098, 12.568337),
# 'politikredse_kode': ['politikredse_1470'],
# 'politikredse': ['Københavns Politi'],
# 'retskredse_kode': ['retskredse_1101'],
# 'retskredse': ['Københavns Byret'],
# 'kommuner_kode': ['kommuner_0101'],
# 'kommuner': ['København'],
# 'opstillingskredse_kode': ['opstillingskredse_0003'],
# 'opstillingskredse': ['Indre By'],
# 'postnumre_kode': ['postnumre_1550'],
# 'postnumre': ['1550 København V'],
# 'sogne_kode': ['sogne_7002'],
# 'sogne': ['Helligånds Sogn'],
# 'latlon_match': [(55.67597910716383, 12.56909419326523)],
# 'landsdele_kode': ['landsdele_218528'],
# 'landsdele': ['Byen København'],
# 'menighedsraadsafstemningsomraader_kode': ['menighedsraadsafstemningsomraader_577555'],
# 'menighedsraadsafstemningsomraader': ['Helligånds'],
# 'ejerlav_kode': ['ejerlav_2000179'],
# 'ejerlav': ['Vestervold Kvarter, København'],
# 'afstemningsomraader_kode': ['afstemningsomraader_711926'],
# 'afstemningsomraader': ['3. Indre By']}
## Locates geographical entities in a text string
string = 'Addresse: 8000 Aarhus C'
res2 = geodk.get_geo_info_string(string)
#res
# {'match_type': 'administrative',
# 'matchlevel': 'postnumre',
# 'matchlevel_num': 1,
# 'match_code': 'postnumre_8000',
# 'match': '8000 Aarhus C',
# 'nmatches': 1,
# 'entity_order': 0,
# 'postnumre_kode': ['postnumre_8000'],
# 'postnumre': ['8000 Aarhus C'],
# 'regioner_kode': ['regioner_1082'],
# 'regioner': ['Region Midtjylland'],
# 'kommuner_kode': ['kommuner_0751'],
# 'kommuner': ['Aarhus'],
# 'retskredse_kode': ['retskredse_1165'],
# 'retskredse': ['Retten i Århus'],
# 'politikredse_kode': ['politikredse_1461'],
# 'politikredse': ['Østjyllands Politi'],
# 'opstillingskredse_kode': ['opstillingskredse_0065',
#  'opstillingskredse_0062'],
# 'opstillingskredse': ['Aarhus Øst', 'Aarhus Syd'],
# 'landsdele_kode': ['landsdele_218546'],
# 'landsdele': ['Østjylland'],
# 'supplerendebynavne2_kode': ['supplerendebynavne2_666647'],
# 'supplerendebynavne2': ['Marsb.Skov']}
```
