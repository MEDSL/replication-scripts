# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 18:06:00 2021

@author: abguh
"""

import pandas as pd
import os
import numpy as np

path = '/Users/declanchin/Desktop/MEDSL/2020-precincts/precinct/UT/raw'
os.chdir(path)
df = pd.read_csv('20201103__ut__general__precinct.csv', dtype= 'string')
df = df.replace(np.nan, '', regex = True)
df = df.applymap(lambda x: x.strip() if type(x)==str else x)


df = pd.melt(df, id_vars = ['precinct', 'county', 'office', 'district', 'candidate', 'party'],
        value_vars=['votes', 'election_day', 'mail', 'early_voting'],
        var_name = 'mode', value_name = 'votes')
df.votes = df.votes.str.replace(',','').replace('',0).astype(int)

a = df[df.county == 'Duchesne']
tdic = {}
for c in a.candidate.unique():
    df1 = a[a.candidate == c]
    tot = df1.votes.sum()
    office = df1.office.unique()[0]
    tdic[c] = tot

df['mode'] = df['mode'].replace({'votes':'TOTAL'})
df.loc[(df['county'] == 'Salt Lake') & (df['mode'] == 'TOTAL'), 'mode'] = ''
df = df[df['mode'] != '']  #get rid of all salt lake total vote rows as this will overcount
df['mode'] = df['mode'].replace({'election_day':'ELECTION DAY', 'mail':'MAIL', 'early_voting':'EARLY'})

df['county_name'] = df.county.str.upper()
countyFips = pd.read_csv("/Users/declanchin/Desktop/MEDSL/2020-precincts/help-files/county-fips-codes.csv")
df['state'] = 'Utah'

df = pd.merge(df, countyFips, on = ['state','county_name'],how = 'left')
df.county_fips = df.county_fips.astype(str)
df['jurisdiction_name'] = df.county_name
df['jurisdiction_fips'] = df.county_fips


def get_writein(x):
    if ('WRITE-IN' in x.upper() or '(W)' in x.upper() or 'WRITE IN' in x.upper() 
    and x != 'WRITE-IN TOTALS'): return 'TRUE'
    else: return 'FALSE'

u = list()
def fix_candidate(x):
    x = x.upper()
    if x == 'DON BALLOTS CAST BLANKENSHIP': return 'DON BLANKENSHIP'
    if 'TYLER SCOTT' in x or 'GREGORY' in x: return 'TYLER SCOTT BATTY'
    if x.upper() == 'WRITE-IN' or x.upper() == 'WRITE-INS': return x.upper()
    if 'CHRIS PETERS' in x: return 'CHRIS PETERSON' #some mispellings with -en
    if 'JADE' in x.upper(): return 'JADE SIMMONS' #some entries are just 'write-in: jade'
    if 'WRITE' in x and ('TOTALS' in x or 'CERTIFIED' in x or 'REGISTERED' in x):
        if x == 'WRITE-IN TOTALS': return x
        elif 'CERTIFIED' in x: return 'UNCERTIFIED WRITE-IN'
        elif 'REGISTERED' in x: return 'UN-REGISTERED WRITE-IN'
    x = x.upper().replace(' (W)','').replace('WRITE-IN','').replace('.','').replace('~ ','').replace(': ','')
    #if 'REP' in x or ...
    x = x.replace('REP ', '').replace('LIB ', '').replace('UUP ','').replace('DEM ','').replace('CON ','').replace('IAP ','').replace('GRN ','')
    x = x.replace('DAMSHEN', 'DAMSCHEN').replace('LA RIVA', 'LARIVA')
    if '/' in x:
        return x[:x.find('/')].strip().upper()
    if ',' in x: 
        return x[:x.find(',')].upper()
    if x == "JESSICA O'LEARY": return x
    else: return x.replace('\\','').replace("'",'"').upper().replace('ED KENNEDY', '').strip().replace('  ',' ')


def get_dataverse(x):
    if x == 'US PRESIDENT': return 'PRESIDENT'
    if x == 'US HOUSE': return 'HOUSE'
    if x in ['ATTORNEY GENERAL', 'GOVERNOR', 'STATE AUDITOR', 'STATE HOUSE', 'STATE SENATE', 'STATE TREASURER']:
        return 'STATE'
    else: return ''
    
def fix_district(office, district):
    if office in ['US PRESIDENT', 'ATTORNEY GENERAL', 'GOVERNOR', 'STATE AUDITOR', 'STATE TREASURER']:
        return 'STATEWIDE'
    else: return district

def magnitude(office):
    if office in ['BALLOTS CAST', 'BALLOTS CAST BLANK','REGISTERED VOTERS']: return 0
    else: return 1

def add_writein(cand, w):
    if cand in ["MARCI GREEN CAMPBELL", "J L F", "TREY ROBINSON", "JONATHAN L PETERSON",
             "KRISTENA M CONLIN","MADELINE KAZANTZIS","RICHARD T WHITNEY", "DAVID A ELSE",
             'BRIAN CARROLL', 'JADE SIMMONS','KRISTENA M CONLIN',
             'PRESIDENT R BODDIE', 'PRINCESS KHADIJAH M JACOB-FAMBRO', 'RICHARD T WHITNEY',
             'TOM HOEFLING', 'TYLER SCOTT BATTY']:
        return 'TRUE'
    else: return w
    
df['writein'] = df.candidate.apply(get_writein)
df.candidate = df.candidate.apply(fix_candidate)
df.writein = df.apply(lambda x: add_writein(x.candidate, x['writein']),axis =1)

df.office = df.office.str.upper().replace({'PRESIDENT': 'US PRESIDENT'}).str.replace('.','')
df['dataverse'] = df.office.apply(get_dataverse)
df['district'] = df.apply(lambda x: fix_district(x['office'], x['district']), axis = 1)
df['district'] = df.district.apply(lambda x: x.zfill(3) if len(x)<=3 and len(x) != 0 else x)


df['party'] = df['party'].replace({'DEM': 'DEMOCRAT', 'LIB':'LIBERTARIAN', 'GRN': 'GREEN',
                               'REP': 'REPUBLICAN', 'UNA': 'INDEPENDENT', 'CON': 'CONSTITUTION',
                               'UUP': 'UTAH UNITED', 'IAP': 'INDEPENDENT AMERICAN', 'LBT':'LIBERTARIAN'})

#merge party info for candidates we didn't know about 
parties = pd.read_excel('party_crosswalk.xlsx')
df = pd.merge(df, parties, on = 'candidate', how = 'left').replace(np.nan, '', regex = True)

df.party = df['party'].replace('', np.nan)
df['party_detailed'] = df.party.fillna(df['party_detailed'])
df.loc[df.candidate == 'GLORIA LARIVA', 'party_detailed'] = 'SOCIALISM AND LIBERATION'
df['party_simplified'] = df.party_detailed.replace({'GREEN':'OTHER', 'INDEPENDENT': 'OTHER', 'CONSTITUTION': 'OTHER',
                                                    'UTAH UNITED':'OTHER', 'INDEPENDENT AMERICAN':'OTHER',
                                                    'SOCIALISM AND LIBERATION': 'OTHER', 'C.U.P': 'OTHER'})

df.state = df.state.str.upper()
df['year'] = '2020'
df['stage'] = 'GEN'
df['state_po'] = 'UT'
df['state_fips'] = '49'
df['state_cen'] = '87'
df['state_ic'] = '67'
df['date'] = '2020-11-03'
df['special'] = 'FALSE'
df['readme_check'] = 'FALSE'
df['magnitude'] = df.office.apply(magnitude).astype(int)

df.loc[df.candidate == 'MATT GWYNN', 'district'] = '029'
df.loc[df.candidate == 'TANNER GREENHALGH', 'district'] = '029'
df.loc[df.candidate == 'KERRY M WAYNE', 'district'] = '029'

df_final = df[["precinct", "office", "party_detailed", "party_simplified", 
               "mode", "votes", "candidate", "district", "dataverse",  
               "stage", "special", "writein","date", "year","county_name", 
               "county_fips","jurisdiction_name", "jurisdiction_fips", 
               "state", "state_po","state_fips", "state_cen", 
               "state_ic", "readme_check", 'magnitude']].copy()


df_final = df_final[df_final.candidate != 'WRITE-IN TOTALS']
df_final.loc[df_final.candidate.str.contains('WRITE-IN'), 'candidate'] = 'WRITEIN'

df_final = df_final.drop_duplicates()

#print(df_final.columns)
#df_final = df_final.set_index('precinct') #remove to fix dropping precinct column DC 6-10
print(df_final.columns)

df_final.to_csv("/Users/declanchin/Desktop/MEDSL/2020-precincts/precinct/UT/2020-ut-precinct-general.csv", index = False)

#af = pd.read_csv('C:/Users/abguh/Desktop/urop/2020-precincts/precinct/UT/2020-ut-precinct-general.csv')
'''
print(sorted(df_final.candidate.unique()))
df1 = df_final[df_final.candidate.str.contains('GLORIA LARIVA')]
print(sorted(df1.party_detailed.unique()))
print(sorted(df1.party_simplified.unique()))


df0 = df_final[df_final.county_name == 'SALT LAKE']

a = df_final[df_final.county_name == 'DUCHESNE']
tdic2 = {}
for c in a.candidate.unique():
    df1 = a[a.candidate == c]
    tot = df1.votes.sum()
    office = df1.office.unique()[0]
    tdic2[c] = tot

#for c in tdic.keys():
#    print(c ,': ',tdic[c])

#print('\nnew data:')
#for c in tdic2.keys():
#    print(c ,': ',tdic2[c])

#only salt lake has info by mode 

'''
'''
df1 = pd.read_csv('2020GeneralSOVC.csv')
df1 = df1.iloc[1:,:-1].replace(np.nan, '')

cands = df1.iloc[0:1,6:].T    #create a little crosswalk of office to candidate

print(df1.columns)
df = pd.melt(df1.iloc[2:,:], id_vars = ['COUNTY NUMBER', 'PRECINCT CODE', 'PRECINCT NAME'], 
        var_name = 'office', value_name = 'votes')

df = pd.merge(df, cands, left_on = 'office', right_index = True).rename(columns = {1:'candidate'})
print(df['COUNTY NUMBER'].unique())

'''