# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 06:36:56 2021

@author: abguh
"""

import pandas as pd
import os
import numpy as np

path = 'C:/Users/abguh/Desktop/urop/2020-precincts/precinct/HI'
os.chdir(path)
df = pd.read_csv('hi_raw_precinct.txt')
df = df.replace(np.nan, '', regex = True)
df = df.applymap(lambda x: x.strip() if type(x)==str else x)

af = pd.melt(df, id_vars = ['Precinct_Name', 'Split_Name', 'precinct_splitId', 
                            #'Ballots','Reg_voters',  'Reporting',
                            'Contest_title', 'Candidate_name'],
        value_vars=['Absentee_votes', 'Early_votes', 'Election_Votes'],
        var_name = 'mode', value_name = 'votes')
#df.votes = df.votes.str.replace(',','').replace('',0).astype(int)
af['mode'] = af['mode'].replace({'Absentee_votes': 'ABSENTEE',
                           'Early_votes':'EARLY', 'Election_Votes': 'ELECTION DAY'})

stats = pd.melt(df, id_vars = ['Precinct_Name', 'Split_Name', 'precinct_splitId', 
                            
                            'Contest_title', 'Candidate_name'],
        value_vars=['Ballots','Reg_voters'],
        var_name = 'stat', value_name = 'votes')
stats['mode'] = 'TOTAL'
stats['stat'] = stats['stat'].replace({'Ballots': 'BALLOTS CAST',
                           'Reg_voters':'REGISTERED VOTERS'})
stats['Contest_title'] = stats['stat']
stats['Candidate_name'] = stats['stat']
stats = stats[['Precinct_Name', 'Split_Name', 'precinct_splitId', 'Contest_title', 
         'Candidate_name', 'votes', 'mode']]

df = pd.concat([af, stats], axis = 0)


'''
print(sorted(df.precinct_splitId.unique()))
print(sorted(df.Split_Name.unique()))
print(sorted(df.Reporting.unique()))
'''

def get_district(x):
    x=x.upper()
    if 'COUNCILMEMBER' in x:
        if 'DIST' in x: return x[x.find('DIST')+5:x.find(', C')].replace('III','3').replace('IX','4').replace('VII','7').zfill(3)
        else: return ''
    elif 'STATE REPRESEN' in x: return x[-2:].strip().zfill(3)
    elif 'STATE SENATOR' in x:
        if 'VACANCY' in x: return '016'
        else: return x[-2:].strip().zfill(3)
    elif 'U.S. REP' in x: return x[-2:].strip().replace('II','002').replace('I','001')
    elif 'PRESIDENT' in x: return 'STATEWIDE'
    elif 'TRUSTEE' in x: return 'STATEWIDE'
    else: return ''
def fix_office(x):
    x=x.upper()
    if 'COUNCILMEMBER' in x:
        if '(' in x: return 'COUNCILMEMBER, '+ x[x.find('(')+1:].strip(')')
        else: return 'COUNCILMEMBER, ' + x[x.find(' C')+1:]
    elif 'STATE REP' in x: return 'STATE HOUSE'
    elif 'STATE SEN' in x: return 'STATE SENATE'
    elif 'U.S. REP' in x: return 'US HOUSE'
    elif 'PRESIDENT' in x: return 'US PRESIDENT'
    else: return x

def get_dataverse(x):
    if x == 'US PRESIDENT': return 'PRESIDENT'
    elif x == 'US HOUSE': return 'HOUSE'
    elif x == 'US SENATE': return 'SENATE'
    elif 'TRUSTEE' in x or 'STATE SEN' in x or 'STATE HOUSE' in x: return 'STATE'
    else: return 'LOCAL'

def get_party(x):
    if x[0] == '(': return x[:3].strip(')').strip('(')
    else: return 'NONPARTISAN'

def fix_candidate(x):
    if x[0] =='(': x= x[x.find(' ')+1:]
    if '/' in x:
        return x.replace('/','AND')
    elif x =='NO' or x == 'YES': return x
    
    if 'Jr.' in x or 'Sr' in x: suffix =  x[x.find('r.')-2:x.find('.')].upper()
    else: suffix = ''
        
    if '(' in x: middle = (x[x.find("("):].replace('(','"').replace(')','"') + ' ').upper()
    else: middle = ''
    
    last = x[:x.find(',')]
    
    if '(' not in x:
        first = (x[x.find(',')+2:]).upper() + ' '  
    else: first = (x[x.find(',')+2 : x.find(' (')].upper() + ' ')
    return (first+middle+last+suffix).replace('.','').replace(', JR','').replace(', SR','').replace('DeCOSTA','DECOSTA')



#for office in sorted(df.Contest_title.unique()):
#    print(office)
    
df['district'] = df.Contest_title.apply(get_district) 
df['office'] = df.Contest_title.apply(fix_office) 
df['special'] = 'FALSE'
df['party_detailed'] = df.Candidate_name.apply(get_party).replace({
                        'A': 'ALOHA AINA', 'D':'DEMOCRAT',
                        'C': 'CONSTITUTION', 'G':'GREEN', 
                        'L': 'LIBERTARIAN', 'R':'REPUBLICAN',
                        'N':'INDEPENDENT', 'AS': 'AMERICAN SHOPPING'})
df['party_simplified'] = df.party_detailed.replace({'GREEN':'OTHER',
                        'ALOHA AINA':'OTHER','AMERICAN SHOPPING':'OTHER',
                        'INDEPENDENT':'OTHER', 'CONSTITUTION':'OTHER'})

df['candidate'] = df.Candidate_name.apply(fix_candidate)
df['dataverse'] = df.office.apply(get_dataverse)

df.loc[(df.district == '016') & (df.office == 'STATE SENATE'), 'special'] = 'TRUE'
#df.loc[df.office == 'MOLOKAI RESIDENT TRUSTEE', 'district'] = 'STATEWIDE'

hi2018 = pd.read_csv('2018-hi-precinct.txt')
hi2018 = hi2018[['precinct','county']]
hi2018 = hi2018.drop_duplicates()

df = df.rename(columns={'Precinct_Name':'precinct'})
df = pd.merge(df, hi2018, on =['precinct'],how = 'left')

#df = df.rename(columns={'county':'precinct'})
df['county_name'] = df.county.str.upper()
df.loc[df.precinct == '39-05','county_name'] = 'HONOLULU'

countyFips = pd.read_csv("C:/Users/abguh/Desktop/urop/2020-precincts/help-files/county-fips-codes.csv").astype(str)
df['state'] = 'Hawaii'

df = pd.merge(df, countyFips, on = ['state','county_name'],how = 'left')
df.loc[df.precinct == 'Presidential','county_fips'] = '0'

df.county_fips = df.county_fips.astype(str).astype(int).astype(str) #.apply(lambda x: x[:-2] if x != 'nan' else x)
df['jurisdiction_name'] = df.county_name
df['jurisdiction_fips'] = df.county_fips

df.state = df.state.str.upper()
df['year'] = '2020'
df['stage'] = 'GEN'
df['state_po'] = 'HI'
df['state_fips'] = '15'
df['state_cen'] = '95'
df['state_ic'] = '82'
df['date'] = '2020-11-03'
df['readme_check'] = 'FALSE'
df['writein'] = 'FALSE'
df['magnitude'] = 1


#print(df.district.unique())
#for cand in (sorted(df.candidate.unique())):
#    print(cand)

#print(sorted(df.party_detailed.unique()))

df.loc[(df.office == "COUNCILMEMBER, CITY AND COUNTY OF HONOLULU") & (df.district == '004'), 'district'] = '009'

df.loc[df.office == 'BALLOTS CAST','dataverse'] = ''
df.loc[df.office == 'REGISTERED VOTERS','dataverse'] = ''

df.loc[df.office == 'BALLOTS CAST','party_detailed'] = ''
df.loc[df.office == 'REGISTERED VOTERS','party_detailed'] = ''

df.loc[df.office == 'BALLOTS CAST','party_simplified'] = ''
df.loc[df.office == 'REGISTERED VOTERS','party_simplified'] = ''

df.loc[df.office == 'BALLOTS CAST','magnitude'] = 0
df.loc[df.office == 'REGISTERED VOTERS','magnitude'] = 0

df.loc[df.office == 'BALLOTS CAST','candidate'] = 'BALLOTS CAST'
df.loc[df.office == 'REGISTERED VOTERS','candidate'] = 'REGISTERED VOTERS'


df = df.applymap(lambda x: x.strip() if type(x)==str else x)
df.votes = df.votes.astype(int)

#drop all presidential rows
df = df[df.precinct != 'Presidential']
df['candidate'] = df['candidate'].replace({'BLANKENSHIP AND MOHR': 'DON BLANKENSHIP',
                                           'BIDEN AND HARRIS':'JOSEPH R BIDEN',
                                           'HAWKINS AND WALKER': 'HOWIE HAWKINS',
                                            'JORGENSEN AND COHEN': 'JO JORGENSEN',
                                            'TRUMP AND PENCE': 'DONALD J TRUMP',
                                            'PIERCE AND BALLARD': 'BROCK PIERCE'})

df_final = df[["precinct", "office", "party_detailed", "party_simplified", 
               "mode", "votes", "candidate", "district", "dataverse",  
               "stage", "special", "writein","date", "year","county_name", 
               "county_fips","jurisdiction_name", "jurisdiction_fips", 
               "state", "state_po","state_fips", "state_cen", 
               "state_ic", "readme_check", 'magnitude']].copy()

df_final.to_csv("2020-hi-precinct-general.csv", index = False)

a = df_final[df_final.office == 'BALLOTS CAST']
#print(sorted(a.office.unique()))
#print(len(hi2018.precinct.unique()))
#print(len(df_final.precinct.unique()))

#got the county names from 2018 data but 39-05 wasn't in there?
#I looked it up and it's in Honolulu so I hardcoded that; make note of no 
#crosswalk here 
