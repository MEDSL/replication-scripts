import pandas as pd
import csv
import numpy as np

raw = pd.read_csv('2018-ri-precinct-autoadapted.csv')

county_fips = {

    'BRISTOL': '44001',
    'NEWPORT': '44005',
    'WASHINGTON': '44009',
    'KENT': '44003',
    'PROVIDENCE': '44007',
    '""': ''

    }

def get_fips(county):
    return county_fips[county]

def fix_party_detailed(party):
    if party == 'NON-PARTISAN': return 'NONPARTISAN'
    return party

def party_simplified(party):
    if party == 'DEMOCRAT': return 'DEMOCRAT'
    elif party == 'REPUBLICAN': return 'REPUBLICAN'
    elif party == 'LIBERTARIAN': return 'LIBERTARIAN'
    elif party == 'NONPARTISAN': return 'NONPARTISAN'
    return 'OTHER'
    
def fix_juris(name):
    if name == 'FEDERAL PRECIN': return 'FEDERAL PRECINCT'
    return name

def fix_candidate(name):
    if 'WRITE-IN' in name: return 'WRITEIN'

    fixed = name.replace('.', '')
    fixed = fixed.replace('  ', '')
    fixed = fixed.replace(',', '')
    fixed = fixed.strip()

    return fixed

def get_writein(name):
    if name == 'WRITEIN': return 'TRUE'
    return 'FALSE'


def fix_district(dist):
    if dist == '""': return '' 
    fixed = str(dist)
    if fixed[0] in numeric: fixed = str(int(fixed))
    if len(fixed) == 1: return '00' + fixed
    elif len(fixed) == 2: return '0' + fixed
    elif fixed == 'None': return ''
    return fixed

def delete_after(word1, word2):
    if word2 not in word1:
        return word1

    n = len(word2)

    for i in range(len(word1)):
        if word1[i:i+n] == word2:
            return word1[:i]

numeric = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}

def fix_office(office):
    fixed = office
    fixed = delete_after(fixed, 'WARD ')
    fixed = fixed.replace('  ', ' ')
    fixed = fixed.strip()
    fixed = fixed.replace('NON-PARTISAN ', '')

    # if fixed[0] in numeric:
    #     if fixed[1] in numeric:
    #         fixed = fixed[4:]
    #     else:
    #         fixed = fixed[3:]
    #town
    if fixed[0:8] != 'TOWN OF ' and 'TOWN OF ' in fixed:
        fixed = fixed.replace('TOWN OF ', '- ')

    #city
    if 'CITY' in fixed:
        fixed = fixed.replace('CITY OF', '-')
        if 'COUNCIL' in fixed and 'CITY COUNCIL' not in fixed:
            fixed = fixed.replace('COUNCIL', 'CITY COUNCIL')

    #council, no city or town
    if 'COUNCIL' in fixed and 'CITY' not in fixed and 'TOWN' not in fixed:
        fixed = fixed.replace('COUNCIL', 'CITY COUNCIL')
        if 'VACANCY' not in fixed:
            fixed = fixed.replace('COUNCIL', 'COUNCIL -')

    if 'COUNCIL -' not in fixed and 'CHARTER AMENDMENT REGARDING QUORUM' not in fixed:
        fixed = fixed.replace('COUNCIL', 'COUNCIL -')
    
    #remove at large

    atlarges = [' --AT LARGE', ' - AT-LARGE', '-AT-LARGE', ' AT-LARGE', '-AT LARGE']

    for phrase in atlarges:
        fixed = fixed.replace(phrase, '')

    #school committee

    if 'COMMITTEE' in fixed and '-' not in fixed and fixed != 'SCHOOL COMMITTEE':
        fixed = fixed.replace('COMMITTEE', 'COMMITTEE -')
    elif 'BRISTOL/WARREN' in fixed: fixed = 'SCHOOL COMMITTEE - BRISTOL/WARREN REGIONAL'
    
    
    fixed = fixed.replace('- -', '-')
    fixed = fixed.replace('-CITY WIDE', '')
        
    return fixed
        

def get_ward_district(name):
    for i in range(len(name)):
        if name[i:i+5] == 'WARD ':
            return name[i+5:]

def ward_district(df):

    wards = {}

    for x in df.index:
        val = df.loc[x, 'office']
        if 'WARD' in val:
            wards[x] = val

    for x in wards:
        df.loc[x, 'district'] = get_ward_district(wards[x])

def fix_county(county):
    if county == '""': return ''
    return county

def add_at_large(df):

    for x in df.index:
        office = df.loc[x, 'office']
        if 'AT' in office and 'LARGE' in office:
            string = df.loc[x, 'district']
            if string == '': df.loc[x, 'district'] = 'AT LARGE'
            else: df.loc[x, 'district'] = 'AT LARGE, ' + string

def fix_writein(thing):
    if str(thing) == 'TRUE' or str(thing) == 'True': return 'TRUE'
    elif str(thing) == 'False' or str(thing) == 'FALSE': return 'FALSE'
    return 'FALSE'

ward_district(raw)

raw['jurisdiction_name'] = raw['jurisdiction_name'].apply(fix_juris)
raw['readme_check'] = 'FALSE'
raw['county_fips'] = raw['county_name'].apply(get_fips)
raw['jurisdiction_fips'] = raw['county_fips']
raw['date'] = '2018-11-06'

raw['district'] = raw['district'].apply(fix_district) #pad 0s, remove '""'
raw['district'] = raw['district'].astype(str)

add_at_large(raw)

#get district
raw['candidate'] = raw['candidate'].apply(fix_candidate)
raw['writein'] = raw['candidate'].apply(get_writein)

#fix office
raw['office'] = raw['office'].apply(fix_office)

#empty string weirdness
raw['county_name'] = raw['county_name'].apply(fix_county)
raw['county_name'] = np.where(raw['precinct'] == 1802, 'NEWPORT', raw['county_name'])

#special
raw['special'] = 'FALSE'
raw['special'] = raw['special'].astype(str)

#writein
raw['writein'] = raw['writein'].apply(fix_writein)
raw['writein'] = raw['writein'].astype(str)

#empty fips
raw['jurisdiction_fips'] = np.where(raw['precinct'] == 1802, '44005', raw['jurisdiction_fips'])
raw['county_fips'] = np.where(raw['precinct'] == 1802, '44005', raw['county_fips'])

#party
raw['party_detailed'] = raw['party_detailed'].apply(fix_party_detailed)
raw['party_simplified'] = raw['party_detailed'].apply(party_simplified)

#DC district update
raw['district'] = np.where((raw['district']=="")&(raw['dataverse']!="LOCAL"), 'STATEWIDE',raw['district'])

#for thing in set(raw['district']): print(thing)

raw.to_csv('2018-ri-precinct-general-updated.csv', index = False, quoting=csv.QUOTE_NONNUMERIC)


