import pandas as pd
import numpy as np
import csv

raw = pd.read_csv('2018-wi-precinct-autoadapted.csv', dtype = {'district': str})

###COUNTY/JURISDICTION MAPS###
county_fips = pd.read_csv('../../help-files/county-fips-codes.csv')
county_fips = county_fips[county_fips['state'] == 'Wisconsin']

jurisdiction_fips = pd.read_csv('../../help-files/jurisdiction-fips-codes.csv')
jurisdiction_fips = jurisdiction_fips[jurisdiction_fips['state'] == 'Wisconsin']


county_fips_map = {}
for i in range(len(county_fips['county_name'].values)):
    county_fips_map[county_fips['county_name'].values[i]] = county_fips['county_fips'].values[i]
    
    # leads to incorrect results
# jurisdiction_fips_map = {}
# for i in range(len(jurisdiction_fips['jurisdiction_name'].values)):
#     name = jurisdiction_fips['jurisdiction_name'].values[i]
#     name = name.replace(' TOWN', '')
#     name = name.replace(' CITY', '')
#     name = name.replace(' VILLAGE', '')
#     name = name.replace('GRANDVIEW', 'GRAND VIEW')
#     name = name.replace('MOUNT STERLING', "MT. STERLING")
#     jurisdiction_fips_map[name] = jurisdiction_fips['jurisdiction_fips'].values[i]

###CLEANER FUNCTIONS###
def fix_candidate(name):
    name = name.replace(',', '')
    name = name.replace('.', '')

    return name


def fix_dist(dist):
    numeric = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
    
    if len(dist) == 1:
        dist = '00' + dist

    elif len(dist) == 2:
        dist = '0' + dist

    return dist

#fix candidate
raw['candidate'] = raw['candidate'].apply(fix_candidate)

#fix district
raw['district'] = raw['district'].apply(fix_dist)

#magnitude
raw['magnitude']= 1

#county fips
def get_county_fips(name):
    return county_fips_map[name]

raw['county_fips'] = raw['county_name'].apply(get_county_fips)

#date
raw['date'] = '2018-11-06'

#jurisdiction fips/jurisdiction
def precinct_to_jurisdiction(name):
    namecopy = name
    name = name.replace('CITY OF ', '')
    name = name.replace('TOWN OF ', '')
    name = name.replace('VILLAGE OF ', '')

    name = name.replace(' CITY', '')
    name = name.replace('FONTANA', 'FONTANA-ON-GENEVA LAKE')
    name = name.replace('LAND O-LAKES', "LAND O'LAKES")
    name = name.replace('SAINT LAWRENCE', "ST. LAWRENCE")
    name = name.replace('MOUNT STERLING', "MT. STERLING")
    name = name.replace('LAVALLE', "LA VALLE")    
    
    
    def remove_ward(word):
        for i in range(len(word)):
            if word[i:i+5] == ' WARD':
                return word[:i]

    name = remove_ward(name)
    if name == 'SALEM LAKES': name = 'SALEM'
    return name

def get_jur_fips(name):
    return jurisdiction_fips_map[name]

raw['jurisdiction_name'] = raw['precinct'].apply(precinct_to_jurisdiction)

# leads to incorrect results
# raw['jurisdiction_fips'] = raw['jurisdiction_name'].apply(get_jur_fips)

# doing a merge rather than dictionary mapping
jurisdiction_fips['jurisdiction_fips'] = jurisdiction_fips['jurisdiction_fips'].astype(str)
jurisdiction_fips['jurisdiction_name'] = jurisdiction_fips['jurisdiction_name'].replace(' TOWN', '', regex=True)
jurisdiction_fips['jurisdiction_name'] = jurisdiction_fips['jurisdiction_name'].replace(' CITY', '', regex=True)
jurisdiction_fips['jurisdiction_name'] = jurisdiction_fips['jurisdiction_name'].replace(' VILLAGE', '', regex=True)
jurisdiction_fips['jurisdiction_name'] = jurisdiction_fips['jurisdiction_name'].replace('GRANDVIEW', 'GRAND VIEW', regex=True)
jurisdiction_fips['jurisdiction_name'] = jurisdiction_fips['jurisdiction_name'].replace('MOUNT STERLING', "MT. STERLING")
jurisdiction_fips['county_fips'] = jurisdiction_fips['jurisdiction_fips'].str[0:5]
jurisdiction_fips['state'] = jurisdiction_fips['state'].str.upper()
raw['county_fips'] = raw['county_fips'].astype(str)
raw = raw.merge(jurisdiction_fips, on = ['state','county_fips','jurisdiction_name'], how = 'left')
#readme check
raw['readme_check'] = 'FALSE'

#get rid of writeins with 0 votes
raw = raw[~((raw['votes'] == 0) & (raw['writein'] == True))]

# change governor name
raw.loc[raw['office']=='GOVERNOR / LT. GOVERNOR', 'office'] = 'GOVERNOR'

raw.to_csv('2018-wi-precinct-general-updated.csv', index = None, quoting=csv.QUOTE_NONNUMERIC)


