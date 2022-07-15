import pandas as pd
import numpy as np
import csv

raw = pd.read_csv('2018-ga-precinct-autoadapted.csv',
                  dtype = {'district': str})

###COUNTY/JURISDICTION MAPS###
county_fips = pd.read_csv('../../../help-files/county-fips-codes.csv')
county_fips = county_fips[county_fips['state'] == 'Georgia']

county_fips_map = {}
for i in range(len(county_fips['county_name'].values)):
    county_fips_map[county_fips['county_name'].values[i]] = county_fips['county_fips'].values[i]


#fix county
def fix_county(name):
    if name == 'BEN_HILL': return 'BEN HILL'
    elif name == 'JEFF_DAVIS': return 'JEFF DAVIS'
    return name

raw['county_name'] = raw['county_name'].apply(fix_county)

#county fips, juris fips

raw['county_fips'] = raw['county_name'].apply(lambda x: county_fips_map[x])
raw['jurisdiction_fips'] = raw['county_fips']

#read me
raw['readme_check'] = 'FALSE'

#magnitude
raw['magnitude'] = 1

#fix candidate
def fix_candidate(name):
    name = name.replace(',', '')
    name = name.replace('.', '')
    name = name.replace('  ', ' ')
    name = name.strip()
    if 'SANDIFORD' in name: return "KARIN SANDIFORD"
    if name == '"ABLE" MABLE THOMAS': return 'MABLE "ABLE" THOMAS'
    if name == 'E BLACK': return "ELLIS BLACK"
    else: return name

raw['candidate'] = raw['candidate'].apply(fix_candidate)
raw['candidate'] = raw['candidate'].replace('Ã','A',regex=True)

#fix district
def fix_dist(dist):
    numeric = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
    
    if len(dist) == 1:
        dist = '00' + dist

    elif len(dist) == 2:
        dist = '0' + dist

    return dist

raw['district'] = raw['district'].apply(fix_dist)

#marty harbin and e black

raw['party_detailed'] = np.where(raw['candidate'] == 'MARTY HARBIN', 'REPUBLICAN', raw['party_detailed'])
raw['party_simplified'] = np.where(raw['candidate'] == 'MARTY HARBIN', 'REPUBLICAN', raw['party_detailed'])
raw.loc[raw['candidate']=='ELLIS BLACK', 'party_detailed'] = 'REPUBLICAN'
raw.loc[raw['candidate']=='ELLIS BLACK', 'party_simplified'] = 'REPUBLICAN'

def fix_party_simplified(x):
        if x in ['DEMOCRAT','REPUBLICAN','LIBERTARIAN','NONPARTISAN']: return x
        if x == '': return ""
        else: return "OTHER"
raw['party_simplified'] = raw.party_simplified.apply(fix_party_simplified)
#date
raw['date'] = '2018-11-06'

raw.to_csv('2018-ga-precinct-general-updated.csv', index = None, quoting=csv.QUOTE_NONNUMERIC)