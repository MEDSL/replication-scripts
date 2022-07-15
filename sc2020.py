# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 18:22:57 2021
@author: abguh
"""
import pandas as pd
import os
import numpy as np

path = 'C:/Users/abguh/Desktop/urop/2020-precincts/precinct/SC/raw'
os.chdir(path)
df = pd.read_csv('SC2020_mostrecent.csv')
df = df.replace(np.nan, '', regex = True)
df = df.applymap(lambda x: x.strip() if type(x)==str else x)



df.loc[df.precinct == '-1', 'precinct'] = 'COUNTY FLOATING'
df = df[~((df['precinct'] == 'COUNTY FLOATING') & (df['type'] == 'in-person Absentee'))]
df = df[~((df['precinct'] == 'COUNTY FLOATING') & (df['type'] == 'election day'))]
df = df[~((df['precinct'] == 'COUNTY FLOATING') & (df['type'] == 'absentee'))]

#df = df.drop(df[(df['precinct'] == 'COUNTY FLOATING') & (df['type'] == 'absentee')].index)
#df = df.drop(df[(df['precinct'] == 'COUNTY FLOATING') & (df['type'] == 'election day')].index)
#df = df.drop(df[(df['precinct'] == 'COUNTY FLOATING') & (df['type'] == 'in person absentee')].index)

#df = df[df.precinct != 'COUNTY FLOATING']

'''drop all the non-COUNTY FLOATING precincts where mode is equal to FAILSAFE, 
FAILSAFE PROVISIONAL, or PROVISIONAL'''
df = df[~((df.precinct !='COUNTY FLOATING')&((df['type']=='failsafe')|(df['type']=='failsafe provisional')|(df['type']=='prov')))]


#a = df[(df.county == 'Charleston')&(df.precinct == 'Failsafe') & (df.precinct == 'Failsafe Provisional')&(df['type']=='total')] 
b = df[(df.county == 'Charleston')&(df.precinct == 'Provisional')&(df['type']=='total')]

#b=b[b['type']=='total']
b['type'] = 'PROVISIONAL' #make the mode the "type" which is the precinct value
b['precinct'] = 'COUNTY FLOATING'

df = df[df['type'] != 'total']
df = df[~((df.precinct == 'Failsafe') | (df.precinct == 'Failsafe Provisional') | (df.precinct == 'Provisional'))]
#df = df[~((df.precinct != 'COUNTY FLOATING')&(df['type']=='failsafe'))]


#df = pd.concat([df, a],axis =0)
df = pd.concat([df, b],axis =0)


stats = pd.melt(df, id_vars = ['race', 'candidates', 'county','precinct'], value_vars=['registration'],
                                var_name = 'stat', value_name = 'votes')
stats['stat'] = stats['stat'].replace({'registration':'REGISTERED VOTERS'})
stats['race'] = stats['stat']
stats['candidates'] = stats['stat']
stats['type'] = 'TOTAL'
stats = stats[stats.votes != '']
stats = stats.drop_duplicates()


df = pd.concat([df, stats], axis = 0)
df['mode'] = df['type'].replace({'in-person Absentee': 'IN PERSON ABSENTEE',
                           'failsafe':'FAILSAFE', 'failsafe provisional': 'FAILSAFE PROVISIONAL',
                           'election day': 'ELECTION DAY','absentee':'ABSENTEE', 'prov':'PROVISIONAL'})



def get_party(x):
    if len(x.split(' ')) == 1 and x.lower() != 'write-in' and x not in 'YesNo': return x #straight party tickets
    elif x[:4].isupper() and x[1] != ' ' and x[2] != ' ': return x[:3]
    else: return 'NONPARTISAN'


def get_district(x):
    x = x.replace('  ',' ')
    x = x.replace('District 1 District 1', 'District 1')
    if 'Board of Education' in x: return x[-2:].strip().zfill(3)
    elif 'City Council District' in x: return x[22:24].strip().zfill(3)
    elif 'City Council Ward' in x:
        if 'District' in x: return x[x.find('Ward'):]
        else: return x[13:19].strip() 
    elif x[-10:-8] == 'Di' or x[-11:-9] == 'Di': return x[x.find('District')+9:].strip().zfill(3)
    
    elif 'District Trustee Seat' in x or 'School District' in x:
        if 'Seat' in x: return x[x.find('Seat'):].upper()
        else: return ''
    elif 'Sch.' in x:
        if 'Cooper' in x: return '004,'+x[x.find('4')+1:]
        elif 'St. Andrews' in x: return '010, AREA ST ANDREWS'
        else: return x[x.find('Dist')+5:x.find('Dist')+8].strip().zfill(3) +', '+ x[x.find('Dist')+8:].replace('0','').replace('3','')
            #return x[x.find('Dist')+5:8].strip().zfill(3) + x[x.find('Dist')+7:]
    elif 'Soliticor' in x: return x[x.find(',')+1:]
    elif 'President and Vice President' in x or 'U.S. Senate' in x: return 'STATEWIDE'
    
    elif ('Area' in x or 'Seat' in x) and "Woodruff Roebuck Water" not in x and 'Dist' in x:
        return x[x.find('District '):]
    elif 'Ward' in x: return x[x.find('Ward'):x.find('Ward')+6]
    elif 'State House' in x or 'State Senate' in x: return x[-3:].strip().zfill(3)
    elif x[-6:-5] == 'Se' and 'Dist' not in x: return x[x.find('Seat'):]

    else: return ''

def fix_district(x):
    x = x.upper()
    if x.split(' ')[0] == 'DISTRICT':
        if len(x) <= 11: 
            return x[-3:].strip().zfill(3)
        else:
            x = x[x.find(' ')+1:]
            if ',' in x: return x[:x.find(',')].strip().zfill(3)+','+ x[x.find(' '):]
            else: return x[:x.find(' ')].strip().zfill(3)+','+ x[x.find(' '):]
    else: return x
    

def fix_candidate(x):
    x = x.replace('  ',' ').replace(',','').replace('.','')
    x = x.replace('DEM ','').replace('REP ','').replace('PET ','').replace('CON ','').replace('IND ','').replace('ALN ','').replace('LIB ','').replace('LAB ','').replace('GRN ','')
    if '|' in x: x=x[:x.find('|')-1]
    return x.upper()

def fix_office(x):
    x = x.replace('  ',' ')
    x= x.replace('.','').replace('#','')
    x = x.replace(' Unexpired Term','').replace(' Unexpired Te','')
    if 'STRAIGHT PARTY' in x: return 'STRAIGHT TICKET'
    if 'Seat' in x: x = x[:x.find(' Seat ')]
    if 'State Senate' in x: return 'STATE SENATE'
    elif 'State House' in x: return 'STATE HOUSE'
    elif 'Solicitor' in x: return 'SOLICITOR'
    elif 'House of Representatives' in x: return 'US HOUSE'
    elif "Town of Hilton Head Island" in x: return 'TOWN COUNCIL TOWN OF HILTON HEAD ISLAND'
    elif 'School Board' in x: return 'SCHOOL BOARD'
    elif 'Constituent Sch Board' in x: return 'CONSTITUENT SCHOOL BOARD'
    elif 'School Trustee' in x: return 'SCHOOL TRUSTEE'
    elif 'School District' in x and len(x) <26: return 'SCHOOL DISTRICT'
    elif 'School District Trustee' in x and 'At Large' not in x: return x[:x.find(' Seat')].upper()
    #elif 'School Board' in x: return x[:x.find('SCHOOL BOARD'+12)]
    elif 'County Council' in x and 'District' in x: return 'COUNTY COUNCIL'
    elif 'City Council' in x:
        if 'District' in x: return 'CITY COUNCIL ' + x[x.find('District')+11:].strip().upper()
        elif 'Ward' in x: return 'CITY COUNCIL' + x[x.find('Ward')+7:].strip().upper()
        else: return x
    elif 'Board of Education' in x: return 'BOARD OF EDUCATION'
    elif 'Hilton Head Island PSD' in x: return 'HILTON HEAD ISLAND PSD VOTING'
    elif x == 'President and Vice President': return 'US PRESIDENT'
    elif 'SCH BOARD' in x: return x[:x.find('DIST')] + x[x.find('DIST')+6:]
    else: return x.upper()
    
def get_dataverse(x):
    if x == 'US PRESIDENT': return 'PRESIDENT'
    elif x == 'US HOUSE': return 'HOUSE'
    elif x == 'US SENATE': return 'SENATE'
    elif 'STRAIGHT TICKET' in x or x == 'REGISTERED VOTERS': return ''
    elif 'STATE SEN' in x or 'STATE HOUSE' in x:  return 'STATE'
    else: return 'LOCAL'

df['party_detailed'] = df.candidates.apply(get_party).str.upper()
df['party_detailed'] = df['party_detailed'].replace({'GRN':'GREEN',
                                            'REP':'REPUBLICAN','DEM':'DEMOCRAT',
                                            'CON':'CONSTITUTION','LIB':'LIBERTARIAN',
                                            'IND':'INDEPENDENCE','LAB':'LABOR',
                                            'PET': 'PETITION', 'ALN':'ALLIANCE',
                                            'DEMOCRATIC':'DEMOCRAT', 'REG':''})
df['party_simplified'] = df['party_detailed'].replace({'GREEN':'OTHER',
                                            'CONSTITUTION':'OTHER',
                                            'INDEPENDENCE':'OTHER','LABOR':'OTHER',
                                            'ALLIANCE':'OTHER','PETITION': 'OTHER'})

df['district'] = df['race'].apply(get_district).str.upper()
df['district'] = df['district'].apply(fix_district)
df.loc[df.race.str.contains('STRAIGHT TICKET'), 'race'] = 'STRAIGHT TICKET'
df.loc[df.race.str.contains('STRAIGHT TICKET'), 'candidates'] = 'STRAIGHT TICKET'
df['candidate'] = df.candidates.apply(fix_candidate)
df['writein'] = 'FALSE'
df.loc[df.race.str.contains('Unexpired'),'writein'] = 'TRUE'
df['office'] = df.race.apply(fix_office).str.upper()
df['dataverse'] = df.office.apply(get_dataverse)
df['county_name'] = df.county.str.upper() 

countyFips = pd.read_csv("C:/Users/abguh/Desktop/urop/2020-precincts/help-files/county-fips-codes.csv").astype(str)
df['state'] = 'South Carolina'

df = pd.merge(df, countyFips, on = ['state','county_name'],how = 'left')

df.county_fips = df.county_fips.astype(str).astype(int).astype(str) #.apply(lambda x: x[:-2] if x != 'nan' else x)
df['jurisdiction_name'] = df.county_name
df['jurisdiction_fips'] = df.county_fips

df.state = df.state.str.upper()

df['year'] = '2020'
df['stage'] = 'GEN'
df['state_po'] = 'SC'
df['state_fips'] = '45'
df['state_cen'] = '57'
df['state_ic'] = '48'
df['date'] = '2020-11-03'
df['readme_check'] = 'FALSE'
df['magnitude'] = 1
df['special'] = 'FALSE'
df.loc[df.district == '107', 'special'] = 'TRUE'
df.loc[df.office.str.contains('STRAIGHT TICKET'), 'magnitude'] = 0
df.loc[df.office == 'REGISTERED VOTERS', 'magnitude'] = 0


#print(df.party_detailed.unique())
#print(df.party_simplified.unique())

'''
for office in sorted(df.office.unique()):
    print(office)
'''

df.candidate = df['candidate'].replace({'DANNY OWENS': 'DAN OWENS',
                                        'JAMES SMITH':'JAMES P SMITH',
                                        'LUKE RANKIN': 'LUKE A RANKIN',
                                        'JOHN GRIFFITH':'JOHN P GRIFFITH',
                                        'ROQUE DE LA FUENTE':'ROQUE ROCKY DE LA FUENTE'})


df['votes'] = df['votes'].astype(int) #.str.replace('.0','').astype(int)

df['candidate'] = df['candidate'].replace({'WRITE-IN':'WRITEIN',
                                           "YES IN FAVOR OF THE QUESTION":"YES",
                                           "NO OPPOSED TO THE QUESTION": "NO"})

df_final = df[['race.id',"precinct", "office", "party_detailed", "party_simplified", 
               "mode", "votes", "candidate", "district", "dataverse",  
               "stage", "special", "writein","date", "year","county_name", 
               "county_fips","jurisdiction_name", "jurisdiction_fips", 
               "state", "state_po","state_fips", "state_cen", 
               "state_ic", "readme_check", 'magnitude']].copy()


df_final = df_final.applymap(lambda x: x.replace('  ',' ') if type(x)==str else x)

'''take the votes in COUNTY FLOATING and subtract the sum of the votes from 
all the other precincts in the same county (by mode). 
That way, we only have the additional "floating" county votes in the 
COUNTY FLOATING precinct
'''

def fix_county_floating(votes, raceid, party, county, precinct, dist, cand, office, mode):
    if precinct == 'COUNTY FLOATING':
        print(county)
        #print(county+':'+ mode, office,dist, cand, votes)
        #a = df_final[(df_final['mode'] == mode)&(df_final["county_name"] == county) & (df_final['precinct'] != 'COUNTY FLOATING')].votes.sum()
        a = df_final[(df_final['race.id'] == raceid)&(df_final['mode']==mode)&(df_final.candidate ==cand)&(df_final.county_name==county)&(df_final.office==office)&(df_final.precinct!='COUNTY FLOATING')]
        #b = a[a["county_name"] == county]
        #d = b[b['candidate'] == cand]
        #e = d[d['office'] == office]
        #f = e[e['district'] == dist]
        #g = f[f['party_detailed']==party]
        #h = g[g['race.id']==raceid]
        c = a.votes.sum()
        if votes-c <0: 
            print(county+':'+ mode, office,dist, cand, votes)
            print(votes - c)
        return votes - c
    else: return votes

def get_writein(x):
    if x == 'WRITEIN': return 'TRUE'
    else: return 'FALSE'

df_final['writein'] = df_final['candidate'].apply(get_writein)
df_final.loc[df_final['county_name']=='CHARLESTON', 'readme_check'] = 'TRUE'

#df_final['votes'] = df_final.apply(lambda x: fix_county_floating(x['votes'], x['race.id'],x['party_detailed'],x['county_name'], x['precinct'], x['district'], x['candidate'], x['office'], x['mode']), axis=1)


df_final = df[["precinct", "office", "party_detailed", "party_simplified", 
               "mode", "votes", "candidate", "district", "dataverse",  
               "stage", "special", "writein","date", "year","county_name", 
               "county_fips","jurisdiction_name", "jurisdiction_fips", 
               "state", "state_po","state_fips", "state_cen", 
               "state_ic", "readme_check", 'magnitude']].copy()


g = df_final[df_final.votes < 0]
print(g.candidate.unique())
print(g.county_name.unique())
print(g.office.unique())
print(g['mode'].unique())

'''
['WRITEIN']
['ALLENDALE' 'CHARLESTON' 'ORANGEBURG' 'SUMTER' 'UNION']
['IN PERSON ABSENTEE' 'ELECTION DAY' 'ABSENTEE']
'''

x = df_final[(df_final.county_name=='CHARLESTON')&(df_final.candidate=='JOSEPH R BIDEN')]
print(x.votes.sum())


x = df_final[(df_final.county_name=='CHARLESTON')&(df_final.office=='STRIGHT TICKET 1')]
print(x.votes.sum())


df_final.to_csv("../2020-sc-precinct-general.csv", index = False)



'''
test = df_final[df_final['mode'] != 'TOTAL']
test = test[test.precinct != 'COUNTY FLOATING']
for cand in sorted(test.candidate.unique()):
    df = test[test['candidate'] == cand]
    tot = sum(df.votes)
    print(cand , ':\t', tot)
    if cand == 'LINDSEY GRAHAM': break
test = df_final[df_final['office'] == 'STRAIGHT TICKET 1']
parties = ['REPUBLICAN']
for party in sorted(test.party_detailed.unique()):
    df = test[test['party_detailed'] == party]
    tot = sum(df.votes)
    print(party , ':\t', tot)
    #if cand == 'LINDSEY GRAHAM': break
'''
'''
print(tot1)
print(len(df_final.county_name.unique()))
test = df[df['office'] == cand]
tot = sum(df.votes)
print(cand , ':\t', tot)
'''



#97,635 straight ticket rows 
#coded straight ticket magnitude as 0?