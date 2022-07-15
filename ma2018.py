import pandas as pd
import csv

raw = pd.read_csv('2018-ma-precinct-autoadapted.csv',
                  dtype = {'district': str})

###COUNTY/JURISDICTION MAPS###
county_fips = pd.read_csv('../../../help-files/county-fips-codes.csv')
county_fips = county_fips[county_fips['state'] == 'Massachusetts']

jurisdiction_fips = pd.read_csv('../../../help-files/jurisdiction-fips-codes.csv')
jurisdiction_fips = jurisdiction_fips[jurisdiction_fips['state'] == 'Massachusetts']


county_fips_map = {}
for i in range(len(county_fips['county_name'].values)):
    county_fips_map[county_fips['county_name'].values[i]] = county_fips['county_fips'].values[i]
    
jurisdiction_fips_map = {}
for i in range(len(jurisdiction_fips['jurisdiction_name'].values)):
    name = jurisdiction_fips['jurisdiction_name'].values[i]
    name = name.replace(' TOWN', '')
    jurisdiction_fips_map[name] = jurisdiction_fips['jurisdiction_fips'].values[i]


###CLEANING FUNCTIONS###
    
def fix_candidate(name):
    name = name.replace('.', '')
    name = name.replace(',', '')
    if name == "WILLIAM 'SMITTY' PIGNATELL":
        return 'WILLIAM "SMITTY" PIGNATELL'
    name = name.replace('BLANKS', 'UNDERVOTES')


    return name

numeric = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}

def fix_dist(dist):
    if dist in numeric:
        dist = '00' + dist

    return dist

def fix_party_det(party):
    party = party.replace('BLANKS', '')
    party = party.replace('ALL OTHERS', '')

    return party

def fix_party_sim(party):
    party = party.replace('OTHER', '')

    return party

def get_county_fips(name):
    try:
        return county_fips_map[name]
    except:
        print(name)

def fix_juris(name):
    name = name.replace('N.', 'NORTH')
    name = name.replace('W.', 'WEST')
    name = name.replace('S.', 'SOUTH')
    name = name.replace('E.', 'EAST')

    return name

bad_jur = set()
def get_jur_fips(name):
    try:
        return jurisdiction_fips_map[name]
    except:
        bad_jur.add(name)

###FIX CSV###

#candidate
raw['candidate'] = raw['candidate'].apply(fix_candidate)

#dist
raw['district'] = raw['district'].apply(fix_dist)

#parties
raw['party_detailed'] = raw['party_detailed'].apply(fix_party_det)
raw['party_simplified'] = raw['party_simplified'].apply(fix_party_sim)

#county/jurs
raw['county_fips'] = raw['county_name'].apply(get_county_fips)
raw['jurisdiction_name'] = raw['jurisdiction_name'].apply(fix_juris) #replace abbreviations
raw['jurisdiction_fips'] = raw['jurisdiction_name'].apply(get_jur_fips)

#magnitude
raw['magnitude'] = 1

#date
raw['date'] = '2018-11-06'

#read me
raw['readme_check'] = 'FALSE'
raw['readme_check'] = raw['readme_check'].astype(str)

#DC boolean to string fix
# no writeins or special
raw['writein'] = 'FALSE'
raw['special'] = 'FALSE'

raw.to_csv('2018-ma-precinct-general-updated.csv', index = None, quoting=csv.QUOTE_NONNUMERIC)
            
