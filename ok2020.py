# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 15:32:38 2021

@author: abguh
"""

import pandas as pd
import numpy as np
import os
import zipfile

path = 'C:/Users/abguh/Desktop/urop/2020-precincts/precinct/OK/raw'
os.chdir(path)

with zipfile.ZipFile('20201103_PrecinctResults_csv.zip', 'r') as zip_ref:
        zip_ref.extractall("targetdir")
df = pd.read_csv('targetdir/20201103_PrecinctResults.csv', index_col = False)

df = df.replace(np.nan, '', regex = True).replace('  ', ' ', regex = True).astype(str)
df = df.applymap(lambda x: x.strip() if type(x)==str else x)

df = pd.melt(df, id_vars = ['precinct', 'entity_description', 'race_description', 
        'cand_name', 'cand_party'],
        value_vars=['cand_absmail_votes', 'cand_early_votes', 'cand_elecday_votes'],
        var_name = 'mode', value_name = 'votes')
df['mode'] = df['mode'].replace({'cand_absmail_votes': 'ABSENTEE BY MAIL', 'cand_early_votes': 'EARLY', 
                                 'cand_elecday_votes': 'ELECTION DAY'})


def get_county_code(x):
    if len(x) == 5: return x[0]
    else: return x[:2]
    
def get_district(x):
    x = x.replace('THREE', '3')
    if x == 'FOR CORPORATION COMMISSIONER' or '805' in x or '814' in x: return 'STATEWIDE'
    if 'STATE SENATOR' in x: return x[-2:].strip().zfill(3)
    elif 'STATE REP' in x: 
        if len(x)>=36: return x[-3:].strip().zfill(3)
        else: return x[-1].zfill(3)
    elif 'STATES REP' in x: return x[-2:].zfill(3)
    elif 'SUPREME COURT' in x: return x[x.find('DIST')+9:x.find(' -')].zfill(3)
    elif 'COUNTY COMMISSIONER' in x: return '002'
    elif 'WARD' in x: return x[x.find('WARD'):x.find('WARD')+6].zfill(3)
    elif 'CIVIL APPEALS' in x: return 'DISTRICT '+x[32]+', OFFICE '+x[43]
    elif 'CRIMINAL APPEALS' in x: return x[x.find('DISTRICT')+9].zfill(3)
    elif 'DISTRICT' in x and 'FIRE' not in x: return x[x.find('DIST')+9:x.find('DIST')+10].strip().zfill(3)
    else: return ''

def fix_office(x):
    x = x.replace('FOR ', '')
    if 'PROPOSITION' not in x:
        if 'CIVIL AP' in x: return 'COURT OF CIVIL APPEALS JUDGE'
        elif 'CRIMINAL' in x: return 'COURT OF CRIMINAL APPEALS JUDGE'
        elif 'WEATHERFORD' in x: return 'WEATHERFORD CITY COMMISSIONER'
        elif 'TULSA' in x: return 'TULSA CITY COUNCIL'
        elif 'TECUMSEH' in x: return 'TECUMSEH CITY COUNCIL'
        elif 'EL RENO' in x: return 'EL RENO CITY COUNCIL'
        elif 'BARTLESVILLE' in x: return 'BARTLESVILLE CITY COUNCIL'
        elif 'COUNTY COMMISSIONER' in x: return 'COUNTY COMMISSIONER'
        elif 'PRESIDENT' in x: return 'US PRESIDENT'
        elif 'COMMERCE' in x: return 'CITY OF COMMERCE MAYOR'
        elif 'CLINTON' in x: return 'CITY OF CLINTON MAYOR'
        elif 'STATE REP' in x: return 'STATE HOUSE'
        elif 'STATE SENAT' in x: return 'STATE SENATE'
        elif 'UNITED STATES REP' in x: return 'US HOUSE'
        elif 'SENATOR' in x: return 'US SENATE'
        elif 'SUPREME COURT' in x: return 'SUPREME COURT JUDGE'
        else: return x.replace('#','').replace('.','')
    else: return x.replace('#','').replace('.','')
 
def fix_candidate(x):
    x = x.replace('.', '')
    if '|' in x: return x[:x.find('|')-1]
    elif 'AGAINST THE' in x: return 'NO'
    elif 'FOR THE' in x: return 'YES'
    else: return x

def func(office, cand):
    if 'CIVIL APPEALS' in office or 'SUPREME COURT' in office or 'CRIMINAL APPEALS' in office:
        dicto = {'COURT OF CIVIL APPEALS DISTRICT 1 - OFFICE 2 - JANE P. WISEMAN': 'JANE P WISEMAN', 
                      'COURT OF CIVIL APPEALS DISTRICT 2 - OFFICE 1 - DEBORAH B. BARNES': 'DEBORAH B BARNES',
                      'COURT OF CIVIL APPEALS DISTRICT 2 - OFFICE 2 - KEITH RAPP': 'KEITH RAPP',
                      'SUPREME COURT DISTRICT 1 - MATTHEW JOHN KANE, IV': 'MATTHEW JOHN KANE IV',
                      'SUPREME COURT DISTRICT 6 - TOM COLBERT':'TOM COLBERT',
                      'SUPREME COURT DISTRICT 9 - RICHARD B. DARBY' : 'RICHARD B DARBY',
                      'COURT OF CRIMINAL APPEALS DISTRICT 2 - ROBERT L. HUDSON':'ROBERT L HUDSON',
                      'COURT OF CRIMINAL APPEALS DISTRICT 3 - GARY L. LUMPKIN': 'GARY L LUMPKIN'}
        return dicto[office] + ' - ' + cand
    else: return cand


df['candidate'] = df.cand_name.apply(fix_candidate).str.upper()
df['candidate'] = df.apply(lambda x: func(x['race_description'], x['candidate']), axis=1)

df['county_code'] = df.precinct.apply(get_county_code)
df['district'] = df.race_description.apply(get_district)
df['office'] = df.race_description.apply(fix_office)
df['special'] = 'FALSE'
df.loc[df.office == 'CITY OF COMMERCE MAYOR', 'special'] = 'TRUE'


counties = pd.read_csv('county_codes.csv').astype(str)
df = pd.merge(df, counties, on = 'county_code', how = 'left')
#print(len(df.county_name.unique())) #should be 77

df['party_detailed'] = df.cand_party.replace({'REP' : 'REPUBLICAN',
                                       'DEM' : 'DEMOCRAT','LIB' : 'LIBERTARIAN',
                                       'IND' : 'INDEPENDENT'})
   
nonpart_offices = ['SUPREME COURT JUDGE','COURT OF CRIMINAL APPEALS JUDGE', 'COURT OF CIVIL APPEALS JUDGE', 'WEATHERFORD CITY COMMISSIONER', 'TULSA CITY COUNCIL', 'TECUMSEH CITY COUNCIL', 'BARTLESVILLE CITY COUNCIL', 'EL RENO CITY COUNTIL'] 
for office in nonpart_offices:
    df.loc[df.office==office, 'party_detailed'] = 'NONPARTISAN'

df['party_simplified'] = df.party_detailed.str.replace('INDEPENDENT', 'OTHER')

countyFips = pd.read_csv("C:/Users/abguh/Desktop/urop/2020-precincts/help-files/county-fips-codes.csv")
df['state'] = 'Oklahoma'
df['jurisdiction_name'] = df.county_name

df = pd.merge(df, countyFips, on = ['state','county_name'],how = 'left')

df['county_fips'] = df['county_fips'].apply(str)
df['jurisdiction_fips'] = df['county_fips']
df['state'] = df.state.str.upper() #now can chang
df['state_fips'] = '40'
df['state_cen'] = '73'
df['state_ic'] = '53'
df['state_po'] = 'OK'
df['stage'] = 'GEN'
df.loc[df.office == 'TULSA CITY COUNCIL', 'stage'] = 'GEN RUNOFF'
df['readme_check'] = 'FALSE'
df['date'] = '2020-11-03'
df['year'] = '2020'
df['writein'] = 'FALSE'
df['dataverse'] = 'LOCAL'
df.loc[df.entity_description == 'FEDERAL, STATE AND COUNTY', 'dataverse'] = 'STATE'
df.loc[df.office == 'US PRESIDENT', 'dataverse'] = 'PRESIDENT'
df.loc[df.office == 'US HOUSE', 'dataverse'] = 'HOUSE'
df.loc[df.office == 'US SENATE', 'dataverse'] = 'SENATE'



print(sorted(df.district.unique()))
print(sorted(df.office.unique()))
print(sorted(df.party_detailed.unique()))
print(sorted(df.party_simplified.unique()))
print(sorted(df.candidate.unique()))


df_final = df[["precinct", "office", "party_detailed", "party_simplified", 
               "mode", "votes", "candidate", "district", "dataverse",  
               "stage", "special", "writein","date", "year","county_name", 
               "county_fips","jurisdiction_name", "jurisdiction_fips", 
               "state", "state_po","state_fips", "state_cen", 
               "state_ic", "readme_check"]].copy()

df_final.to_csv("C:/Users/abguh/Desktop/urop/2020-precincts/precinct/OK/2020-ok-precinct-general.csv", index = False)


#CHECKS
for col in df_final:
    print(col)
    print("")
    print(sorted(df_final[col].unique()))
    print("\n\n----------------\n\n")
    

#check dataverse
for i in ["PRESIDENT","SENATE", "HOUSE", "STATE", "LOCAL"]:
    print(i)
    print(sorted(df_final['office'][df_final.dataverse==i].unique()))
    print("\n------------------\n")

print("number of columns/variables:", len(df_final.columns)) #should be 24
print("columns are: ", df_final.columns)


'''
nonpart: supreme court; criminal appeals; civil appeals; city council; city commissioner weatherford
district: corporation commissioner - statewide

RUNOFF: FOR COUNCIL DISTRICT 5 CITY OF TULSA (dists 5,6,7)

no write-ins
'''

