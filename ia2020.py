# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 14:26:25 2021

@author: abguh
"""

import pandas as pd
import numpy as np
import os
import csv

# path = 'C:/Users/abguh/Desktop/urop/2020-precincts/precinct/IA/'
# os.chdir(path)

df = pd.read_csv('raw/IA2020_mostrecent.csv')#,encoding='ANSI',dtype= 'string')
#print(df.columns)

df = df.replace(np.nan, '', regex = True).replace('  ', ' ', regex = True)
df = df.applymap(lambda x: x.strip() if type(x)==str else x)
df = df[['race','candidates','county','precinct','type','votes','registration']]
print(df.type.unique())


df.loc[df.precinct == '-1', 'precinct'] = 'COUNTY FLOATING'
df = df[df.type != 'total']
stats = pd.melt(df, id_vars = ['race', 'candidates', 'county', 'precinct','type'],
        value_vars=['registration'],
        var_name = ['stats'], value_name = 'votes')
print(df.columns)
   

stats['type'] = 'TOTAL'
stats['stats'] = stats['stats'].replace({'registration':'REGISTERED VOTERS'})
stats['race'] = stats['stats']
stats['candidates'] = stats['stats']
stats = stats[stats.stats != 0]

stats = stats[['race', 'candidates', 'county', 'precinct','type','votes']].drop_duplicates()
stats = stats[stats.precinct != 'COUNTY FLOATING']
df = pd.concat([df, stats], axis = 0)


def get_special(office):
    if ('VACANCY' in office.upper() or 'UNEXP' in office or 'TFV ' in office 
        or 'Un-Expired' in office or '(Vac)' in office or 'UNEX' in office): return 'TRUE'
    else: return 'FALSE'
    
def get_magnitude(office):
    if 'Vote for ' == office[-10:-1]: return int(office[-1])
    #elif 'Question 1' in office: return 0
    elif 'REGISTERED VOTERS' in office: return 0
    else: return 1

def get_district(x):
    x= x.replace('Dist. One', 'Dist. 1')
    x=x.upper()
    if 'BOARD OF SUPERVISORS' in x.upper() and 'Dist' in x: return x[-1].zfill(3)
    elif 'COUNTY SUPERVISOR' in x.upper(): 
        if 'AT-LARGE' in x.upper(): return 'AT LARGE'
        return x[-1].zfill(3)
    if 'DISTRICT' == x[:8].upper() and 'JUDGE' in x.upper():
        return x[9:12].strip()
    if x[:4] == 'SUPV' or x[:11]=='SUPERVISOR ': return x[-1].zfill(3)
    if 'STATE REPRESENTATIVE' in x or 'STATE SENATOR' in x: return x[-3:].replace('T','').strip().zfill(3)
    if 'UNITED STATES REP' in x: return x[-1].zfill(3)
    if x == 'PRESIDENT AND VICE PRESIDENT' or 'SUPREME COURT' in x or 'QUESTION 1 - SHALL' in x: return 'STATEWIDE'
    else: return ''

a=list()
def fix_office(x):
    x=x.replace('Co.', 'COUNTY').replace(' To Fill Vacancy','').replace('TFV','')
    x = x.replace('.','').upper().replace(',','')
    x = x.replace(' EXT ',' EXTENSION ').replace('AG ','AGRICULTURAL ')
    x = x.replace('TWP','TOWNSHIP').replace('BD OF', 'BOARD OF')
    if x[:4] == 'FOR ': x=x.replace('FOR ','')
    if 'SOIL AND WATER' in x or 'SOIL & WATER' in x: return 'SOIL AND WATER CONSERVATION DISTRICT COMMISSIONER'
    if 'STATE REPRESENTATIVE' in x: return 'STATE HOUSE'
    if 'STATE SENATOR' in x: return 'STATE SENATE'
    if 'UNITED STATES REP' in x: return 'US HOUSE'
    if 'UNITED STATES SENATOR' in x: return 'US SENATE'
    if x == 'PRESIDENT AND VICE PRESIDENT': return 'US PRESIDENT'
    elif 'JUDGE' in x and 'APPEALS' not in x:
        if x[:8]=='DISTRICT': 
            print(x.replace(x[8:11],' COURT '))
            return x.replace(x[8:11],' COURT ')
        return x[11:].strip()
    elif 'HOSPITAL TRUSTE' in x: return 'COUNTY HOSPITAL TRUSTEE'
    elif 'BOARD OF SUPERVISORS' in x: return 'COUNTY BOARD OF SUPERVISORS'
    elif 'TOWNSHIP TRUSTEE' in x: return 'TOWNSHIP TRUSTEE'
    elif 'COUNTY SUPERVISOR ' in x: return 'COUNTY SUPERVISOR'
    elif 'SHERIFF' in x: return 'COUNTY SHERIFF'
    elif 'COUNCIL' in x: 
        if x not in a: a.append(x)
        return "COUNTY AGRICULTURAL EXTENSION COUNCIL"
    elif 'TOWNSHIP CLERK' in x: return 'TOWNSHIP CLERK'
    elif 'COUNTY SUPERVISOR' in x or 'SUPV' in x: return 'COUNTY SUPERVISOR'
    else: return x

def get_writein(x):
    if 'write-in' in x.lower(): return 'TRUE'
    else: return 'FALSE'
    
def fix_candidate(x):
    x = x.replace('Write-in:  ','')
    x= x.replace('.','')
    x= x.replace('(','')
    x=x.replace(')','')
    x=x.replace(',','')
    if x.lower == 'write-in': return 'WRITEIN'
    if ' and ' in x: return x[:x.find(' and')]
    return x
    
def get_dataverse(x):
    if x == 'US PRESIDENT': return 'PRESIDENT'
    elif x == 'US HOUSE': return 'HOUSE'
    elif x == 'US SENATE': return 'SENATE'
    elif x == 'REGISTERED VOTERS': return ''
    elif ('STATE SEN' in x or 'STATE HOUSE' in x or 'COURT' in x
          or 'QUESTION 1 - SHALL' in x or 'APPEALS' in x or 'SUPREME COURT' in x
          or 'DISTRICT COURT' in x):  return 'STATE'
    else: return 'LOCAL'

df['special'] = df['race'].apply(get_special)
df['magnitude'] = df['race'].apply(get_magnitude)
df['district'] = df['race'].apply(get_district)
df['writein'] = df['candidates'].apply(get_writein)
df['candidate'] = df['candidates'].apply(fix_candidate).str.upper()
df['county_name'] = df['county'].str.replace('_',' ').str.upper()
df['office'] = df['race'].apply(fix_office)
df['mode'] = df['type']

countyFips = pd.read_csv("../../help-files/county-fips-codes.csv").astype(str)
df['state'] = 'Iowa'
df = pd.merge(df, countyFips, on = ['state','county_name'],how = 'left')

df.county_fips = df.county_fips #.astype(str).astype(int).astype(str) #.apply(lambda x: x[:-2] if x != 'nan' else x)
df['jurisdiction_name'] = df.county_name
df['jurisdiction_fips'] = df.county_fips

df.state = df.state.str.upper()

df['year'] = '2020'
df['stage'] = 'GEN'
df['state_po'] = 'IA'
df['state_fips'] = '19'
df['state_cen'] = '42'
df['state_ic'] = '31'
df['date'] = '2020-11-03'
df['readme_check'] = 'FALSE'

df['dataverse'] = df['office'].apply(get_dataverse)

parties = pd.read_csv('raw/party_crosswalk.csv')
parties['candidate'] = parties['candidate'].str.replace('.','').str.upper()
parties = parties.applymap(lambda x: x.strip()) # if type(x)==str else x)
df = pd.merge(df, parties, on='candidate', how = 'left')


df['party_detailed'] = df.party_detailed.str.upper().replace({np.nan:'',
                                        'DEMOCRATIC':'DEMOCRAT','NO PARTY':'INDEPENDENT'})
df.loc[df.candidate=='WRITEIN','party_detailed'] = ''
df.loc[df.office.str.contains('JUDGE'), "party_detailed"] = 'NONPARTISAN'
df.loc[df.office.str.contains('SUPREME COURT'), "party_detailed"] = 'NONPARTISAN'
df['party_simplified'] = df['party_detailed'].replace({'KAMAL HAMMOUDA FOR IOWA HOUSE':'OTHER',
                                                       'ALLIANCE PARTY':'OTHER','CONSTITUTION PARTY':'OTHER',
                                                       'GENEALOGY KNOW YOUR FAMILY HISTORY':'OTHER','GREEN':'OTHER',
                                                      'INDEPENDENT':'OTHER'})


#for d in sorted(df.candidates.unique())[200:500]:
#    print(d)
print(df.party_detailed.unique())
print(df.party_simplified.unique())
df['mode'] = df['mode'].replace({'absentee':'ABSENTEE', 'election day':'ELECTION DAY'})

df['candidate'] = df['candidate'].replace({'WRITE-IN':'WRITEIN'})


def fix_judges(office, cand):
    if ('SUPREME COURT JUSTICE' in office or 'JUDGE' in office):
        return office[office.find('-')+2:] + ' - ' + cand
    else: return cand
    
df['candidate'] = df.apply(lambda x: fix_judges(x.office, x.candidate), axis=1)
df['office'] = df.office.apply(lambda x: x[:x.find(' -'):] if '-' in x else x)


'''
df.loc[(df['office'] == 'SUPREME COURT JUSTICE - SUSAN KAY CHRISTENSEN') & (df['candidate'] = 'YES'), 'candidate'] = 'SUSAN KAY CHRISTENSEN - YES'
 'SUPREME COURT JUSTICE - EDWARD MANSFIELD'
 'SUPREME COURT JUSTICE - CHRISTOPHER MCDONALD'
 'SUPREME COURT JUSTICE - THOMAS WATERMAN'
 'COURT OF APPEALS JUDGE - THOMAS N BOWER'
 'COURT OF APPEALS JUDGE - DAVID MAY'
 'COURT OF APPEALS JUDGE - JULIE A SCHUMACHER'
 'COURT OF APPEALS JUDGE - SHARON SOORHOLTZ GREER
'''

df = df.replace(np.nan, '', regex = True).replace('  ', ' ', regex = True)
df['district'] = df['district'].replace({'4 A':'004','4 J': '004', '6 A':'006',
                                         '7 A':'007', '7 J':'007', '6 J':'006',
                                         '1B':'001, B','2A':'002, A','2B':'002, B',
                                         '3A':'003, A','3B':'003, B','5A':'005, A',
                                         '5B':'005, B','8A':'008, A', '8B':'008, B',
                                         '1A':'001, A', '5C':'005, C'})



df['candidate'] = df['candidate'].str.replace('Ö','O')
df['candidate'] = df['candidate'].replace('BJ�RN JOHNSON','BJORN JOHNSON')
df['precinct'] = df['precinct'].str.upper().str.strip()

#df.loc[(df.office == 'US HOUSE') & (df.district == '002')&(df.county_name == 'SCOTT'),'readme_check'] = 'TRUE'

# replacing with official data for scott. STILL does not match agg totals but now matches official precinct results
s = pd.read_excel('raw/scott-us-house-2-results.xlsx')
s.columns = ['precinct','mode'] + list(s.columns[2:])
s = s[s['mode']!='Total'].copy().drop(columns = 'Total')
s['precinct'] = s['precinct'].ffill()
s = pd.melt(s, id_vars = ['precinct','mode'], value_vars = s.columns[2:],
           value_name = 'votes',var_name='candidate')
s['party_detailed'] = [i.split(', ')[-1] if ',' in i else "" for i in s['candidate']]
s['party_detailed'] = s['party_detailed'].replace({"DEM":"DEMOCRAT", 'REP':"REPUBLICAN"})
s['party_simplified'] = s['party_detailed']
s['candidate'] = [i.split(', ')[0] for i in s['candidate']]
s['candidate'] = s['candidate'].str.upper().str.replace('\.','',regex=True).replace('WRITE-IN','WRITEIN',regex=False)
s['precinct'] = s['precinct'].str.upper().str.strip()
s['mode'] = s['mode'].str.upper()
s['office'] = 'US HOUSE'
s['district'] = '002'
s['county_name'] = 'SCOTT'
s['dataverse'] = 'HOUSE'
s['stage'] = 'GEN'
s['writein'] = np.where(s['candidate']=='WRITEIN','TRUE','FALSE')
s['special'] = 'FALSE'
s['date'] = '2020-11-03'
s['year'] = 2020
s['county_fips'] = '19163'
s['jurisdiction_name'] = s['county_name']
s['jurisdiction_fips'] = s['county_fips']
s['readme_check'] = 'FALSE'
s['magnitude']=1

df = df[~((df.office == 'US HOUSE') & (df.district == '002')&(df.county_name == 'SCOTT'))]
df = pd.concat([df,s])
for col in ['state', 'state_po', 'state_fips', 'state_cen', 'state_ic']:
    df[col] = df[col].ffill()

df_final = df[["precinct", "office", "party_detailed", "party_simplified", 
               "mode", "votes", "candidate", "district", "dataverse",  
               "stage", "special", "writein","date", "year","county_name", 
               "county_fips","jurisdiction_name", "jurisdiction_fips", 
               "state", "state_po","state_fips", "state_cen", 
               "state_ic", "readme_check", 'magnitude']].copy()


df_final = df_final[df_final.dataverse != 'LOCAL']

df_final = df_final[df_final.precinct != 'COUNTY FLOATING']
df_final['votes'] = df_final['votes'].astype(int)

df_final.to_csv("2020-ia-precinct-general.csv", index = False,quoting=csv.QUOTE_NONNUMERIC)

a= df_final[df_final.candidate == 'WRITEIN']
print(a.office.unique())


'''
for p in sorted(df_final.precinct.unique()):
    p = p.lower()
    if ('early' in p or 'abn' in p or 'prov' in p or 'vote' in p or 'elec' in p
        or 'fail' in p or 'safe' in p):
        print(p)
    

nonpartisan local offices:
    1. county agricultural extension council
    2. soili and water district conservation
    3. township trustee
    4. public hospital trustee
'''