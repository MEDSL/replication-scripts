#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 23:46:38 2021

@author: darsh
"""
import pandas as pd
import csv

path = '/Users/darsh/Documents/GitHub/2018-precincts/MN/2021adapt/2018-mn-precinct-autoadapted.csv'
df = pd.read_csv(path, ',')

#some values aren't capitalized
df = df.applymap(lambda x:x.upper() if type(x) == str else x)

def district(x):
    x = str(x)
    if len(x)<3:
        if x.isdigit():
            return x.zfill(3)
        else:
            return x
    elif ', COURT ' in x and 'STATEWIDE' not in x:
        return ''.join(['00',x])
    else:
        return x
df['district'] = df['district'].apply(district)

check = df.loc[df['district'].str.contains(', COURT ')]
print(check['district'].unique())
#-----------------------------------------------------------------------------------------------
# #find candidates with '(' in nicknames etc)
# check = df.loc[df['candidate'].str.contains('\)')]
# print(check['candidate'].unique())

def candidate(x):
    #remove '.' and ','
    x = x.replace('.','')
    x = x.replace(',','')
    
    #rename write in
    if x == '[WRITE-IN]':
        return 'WRITEIN'
    
    #nicknames
    elif x == 'CALVIN (CAL) K BAHR':
        return 'CALVIN K \"CAL\" BAHR'
    elif x == 'JOHN BACHMAN (JOHNNY B)':
        return 'JOHN \"JOHNNY B\" BACHMAN'
    elif x == 'BARBARA MCFADDEN (KRAEMER)':
        return 'BARBARA \"KRAEMER\" MCFADDEN'
    elif x == 'MICHAEL D CARR (JR)':
        return 'MICHAEL D CARR JR'
    elif x == 'HEIDI \'BLY\' JONES':
        return 'HEIDI \"BLY\" JONES'
    elif x == 'KAREN "KARRIE" S KELLY':
        return 'KAREN S "KARRIE" KELLY'
    elif x == 'KATHRYN "KATIE" M NORBY':
        return 'KATHRYN M "KATIE" NORBY'
    elif x == 'ROBERT "BOB" ARTHUR HARWARTH':
        return 'ROBERT ARTHUR "BOB" HARWARTH'
    
    #other 'similar names' in QA check all belong to different races
    
    else:
        x = x.replace(')','\"')
        x = x.replace('(','\"')
        return x
df['candidate'] = df['candidate'].apply(candidate)

#-----------------------------------------------------------------------------------------------
#office name 'JUDGE' is district court judge. The district column has info in same format for these
#example: '7, COURT 16' is 16th court of the 7th district. These values can remain, only change office

def office(x):
    if x == 'JUDGE':
        return 'DISTRICT COURT JUDGE'
    else:
        return x
df['office'] = df['office'].apply(office)
#-----------------------------------------------------------------------------------------------
def dataverse(office, dv):
    if office == 'DISTRICT COURT JUDGE':
        return 'STATE'
    else:
        return dv
df['dataverse'] = df.apply(lambda df: dataverse(df['office'],df['dataverse']), axis=1)
    
def party(x):
    if x == 'INDEPENDENT' or x == 'UNAFFILIATED':
        return 'NONPARTISAN'
    else:
        return x

df['party_detailed'] = df['party_detailed'].apply(party)
#-----------------------------------------------------------------------------------------------
#get fips code dataframe for MN counties
county_fips_path = '/Users/darsh/Documents/GitHub/2020-precincts/help-files/county-fips-codes.csv'
fips = pd.read_csv(county_fips_path, delimiter=',', header=0)
fips = pd.DataFrame(fips)
fips = fips.loc[fips['state']=='Minnesota']
fips_dict = dict(zip(fips.county_name, fips.county_fips))

def fips(x):
    if x == 'ST. LOUIS':
        x = 'SAINT LOUIS'
    code = fips_dict[x]
    return str(code)

df['county_fips'] = df['county_name'].apply(fips)
df['jurisdiction_fips'] = df['county_fips']
#-----------------------------------------------------------------------------------------------
def string(x):
    if x == True:
        return 'TRUE'
    elif x == False:
        return 'FALSE'

df['writein'] = df['writein'].apply(string)
df['special'] = df['special'].apply(string)
#-----------------------------------------------------------------------------------------------
#all for the 2018 general election under 'stage', being the 11/6 midterm election
df['date'] = '2018-11-06'
#unique office values show only 1 winner
df['magnitude'] = '1'
df['readme_check'] = 'FALSE'

df.to_csv('2018-mn-precinct-final.csv', index = False, quoting=csv.QUOTE_NONNUMERIC)
    
        