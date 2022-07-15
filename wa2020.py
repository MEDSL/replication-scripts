# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 13:34:56 2021

@author: abguh
"""
import pandas as pd
import numpy as np
import os

path = 'C:/Users/abguh/Desktop/urop/2020-precincts/precinct/WA'
os.chdir(path)

df = pd.read_csv('raw/20201103_allstateprecincts.csv')
df = df.replace(np.nan, '', regex = True).replace('  ', ' ', regex = True)
df = df.applymap(lambda x: x.strip() if type(x)==str else x)
df = df.set_index("PrecinctCode")
df = df.drop(-1, axis=0)    #remove all 'Total" aggregates 

df_c = pd.read_csv('raw/county-codes.csv')
df = pd.merge(df, df_c, on = 'CountyCode',how = 'left')

countyFips = pd.read_csv("C:/Users/abguh/Desktop/urop/2020-precincts/help-files/county-fips-codes.csv")
df['state'] = 'Washington'
df['county_name']=df['County'].str.upper()
df['jurisdiction_name'] = df.county_name


df = pd.merge(df, countyFips, on = ['state','county_name'],how = 'left')

df['county_fips'] = df['county_fips'].apply(str)
df['jurisdiction_fips'] = df['county_fips']
df['state'] = df.state.str.replace("Washington", "WASHINGTON") #now can chang
df['precinct'] = df.PrecinctName.str.upper()


def get_writein(x):
    if x == 'WRITE-IN': return 'TRUE'
    else: return 'FALSE'

def get_district(x):
    x = x.replace('DIST.',  'DISTRICT').replace('DIST ', 'DISTRICT ').replace('01','1').replace('- 001','DISTRICT 1').replace('NO 1', '1')
    if 'U.S. REPRESENTATIVE' in x: return x[23:x.find('-')-1].zfill(3).strip()
    elif 'COURT OF APPEALS' in x: return x[x.find('DIV'):x.find('-')].strip() + ', '+ x[x.find('POSI'):]
    elif 'PUBLIC UTILITY' in x:
        if 'DISTRICT' in x:
            return x
    elif 'LEGISLATIVE' in x: 
        if 'SENATOR' in x: return x[21:x.find('-')-1].zfill(3).strip()
        elif 'REPRE' in x: return x[12:x.find('-')].strip() + ', POSITION '+ x[-1]
    elif 'CHARTER REVIEW COMM' in x and '(' in x: return 'POSITION ' + x[-2:].strip()
    elif 'DISTRICT' in x and 'LEVY' not in x and 'PROPOSITION' not in x:
        if x[-10] == 'D' and x[-1] != ')': return x[-2:].strip()
        elif '- 0' in x: return x[x.find('-')+2:x.find('-')+5].strip()
        elif x[x.find('DIST')+9].isnumeric(): return x[x.find('DIST')+9:x.find('DIST')+11].strip()
        elif 'POS.' in x: return 'POSITION ' + x[-2:].strip()
        else: return ''
    elif 'PROPOSITION' not in x and ('POS.' in x or 'POSITION' in x) and 'LEVY' not in x:
        if 'POS.' in x: return ('POSITION '+ x[x.find('POS.')+5])
        elif 'POSITION' in x:
            return (x[x.find('POSI'):x.find('POSI')+11].strip())
    elif 'COUNTY COMMISSIONER' in x and x[-1].isnumeric(): return x[-1]
    elif 'COMMISSIONER' in x and 'PUBLIC' not in x and 'PUD' not in x and x[-1].isnumeric(): return x[-1]
    elif 'SUPERIOR COURT' in x and 'DEPARTMENT' in x: return x[x.find('DEPARTMENT'):]
    else: return ''
    
def fix_candidate(x):
    if x == 'WRITE-IN': return 'WRITEIN'
    elif 'FOR THE' in x: return 'FOR'
    elif 'YES' in x: return 'YES'
    elif 'AGAINST THE' in x: return 'AGAINST'
    elif '?' in x: return x[:-1]
    elif 'NO' in x and len(x)<10: return 'NO' #some names have NO in them, thus need length
    elif '/' in x: return x[:x.find(' /')]
    else: return x

def get_special(x): #only one special election for state senate dist 38
    if x == 'Legislative District 38 - State Senator': return 'TRUE'
    else: return 'FALSE'
    
def fix_office(x):
    if 'PRESIDENT' in x: return 'US PRESIDENT'
    elif 'U.S. REP' in x: return 'US HOUSE'
    elif 'COURT OF APPEALS' in x: return 'COURT OF APPEALS JUDGE'
    elif 'STATE SENATOR' in x: return 'STATE SENATE'
    elif 'REPRESENTATIVE' in x: return 'STATE HOUSE'
    elif 'LT. GOVERNOR' in x: return 'LIEUTENANT GOVERNOR'
    elif 'CHARTER REVIEW COMM' in x and '(' in x: return 'CHARTER REVIEW COMMISSIONER AT-LARGE'
    elif 'COUNTY COMMISSIONER' in x: return 'COUNTY COMMISSIONER'
    elif 'COMMISSIONER' in x and 'PUBLIC' not in x and 'PUD' not in x: return 'COUNTY COMMISSIONER'
    elif 'SUPREME COURT' in x: return 'SUPREME COURT JUSTICE'
    elif 'SUPERIOR COURT' in x: return 'SUPERIOR COURT JUDGE'
    elif 'PUBLIC UTIL' in x or ' PUD ' in x: return 'PUBLIC UTILITY DISTRICT COMMISSIONER'
    elif 'COUNTY COUNCIL' in x: return 'COUNTY COUNCILOR'
    elif 'PROPOSITION' not in x and 'LEVY' not in x:
        if 'DISTRICT' in x and x[-10] == 'D': return x[:-11]
        elif 'DISTRICT' in x and x[x.find('DIST')+9].isnumeric(): 
            if 'POS' in x: return x[:x.find('DIST')]
            else: return x[:x.find('DIST')-1] + x[x.find('DIST')+10:]
        elif 'POS.' in x: return  x[:x.find('POS.')]
        elif 'POSITION' in x and 'NO.' not in x:
            return x[:x.find('POSI')]+ x[x.find('POSI')+11:]
        elif 'POSITION' in x: return x[:x.find('POSITION')-1]
        else: return x
    else: return x
    
def get_dataverse(x):
    if x == 'US PRESIDENT' : return 'PRESIDENT'
    if x == 'US HOUSE': return 'HOUSE'
    if x in ['STATE HOUSE', 'STATE SENATE', 'GOVERNOR', 'LIEUTENANT GOVERNOR',
             'ATTORNEY GENERAL', 'SECRETARY OF STATE', 'COMMISSIONER OF PUBLIC LANDS',
             'STATE AUDITOR', 'STATE TREASURER', 'SUPERINTENDENT OF PUBLIC INSTRUCTION',
             'INSURANCE COMMISSIONER', 'SUPREME COURT JUSTICE', 'COURT OF APPEALS JUDGE',
             'REFERENDUM MEASURE 90', 'ADVISORY VOTE 32', 'ENGROSSED SENATE JOINT RESOLUTION 8212',
             'ADVISORY VOTE 33', 'ADVISORY VOTE 34', 'ADVISORY VOTE 35', 'SUPERIOR COURT JUDGE', 'CIRCUIT COURT JUDGE']:
            return 'STATE'
    if 'POSITION 0' in x: return 'POSITION '+ x[-1]
    else: return 'LOCAL'

def fix_district(x):
    if len(x) ==1 and x.isnumeric(): return x.zfill(3)
    elif x[:8] == 'DISTRICT': return x[9:x.find(',')].strip().zfill(3)+ x[x.find(','):]
    elif x[12:20] == 'DISTRICT': return x[x.find('DISTRICT')+9:x.find('DISTRICT')+10].strip().zfill(3)+', '+ x[:x.find('DISTRICT')]+x[x.find('POSITION'):]
    
    else: return x

df['special'] = df.Race.apply(get_special)
df['writein'] = df.Candidate.apply(get_writein)
df['office'] = df.Race.str.upper().str.replace('#', '').str.replace('NO. ', '')
df['district'] = df.office.apply(get_district).apply(str)
df['district'] = df.district.apply(fix_district)
df['candidate'] = df.Candidate.str.upper().str.replace('&QUOT;', '"').str.replace('&#237;', 'I').str.replace('(', '"').str.replace(')', '"')
df.candidate = df.candidate.str.replace('.','').str.replace('LEVY','').str.replace('SPECIAL','').str.replace(',','').str.replace("'", '"')
df.candidate = df.candidate.str.replace('O"ROURKE', "O'ROURKE").str.replace('O"BAN', "O'BAN").str.replace('JUSTIN FORSMAN','JUSTIN M FORSMAN')
df['candidate'] = df.candidate.apply(fix_candidate)
df['office'] = df.office.apply(fix_office)
df['dataverse'] = df.office.apply(get_dataverse)
df['state_fips'] = '53'
df['state_cen'] = '91'
df['state_ic'] = '73'
df['state_po'] = 'WA'
df['date'] = '2020-11-03'
df['stage'] = 'GEN'
df['mode'] = 'TOTAL'
df['readme_check'] = 'FALSE'
df['votes'] = df.Votes
df['year'] = '2020'
df['magnitude'] = 1
#print(sorted(df.candidate.unique()))
#print(sorted(df.office.unique()))
#print(sorted(df.district.unique()))


df_p = pd.read_csv('raw/20201103_allstate.csv')
df_p = df_p.drop_duplicates(subset=['Candidate'])
df = pd.merge(df, df_p[['Candidate', 'Party', 'JurisdictionName']], on = 'Candidate', how = 'left')

df = df.replace(np.nan, '', regex = True).replace('  ', ' ', regex = True)
#print(sorted(df.Party.unique()))
df['party_detailed'] = df['Party'].str.replace('Democractic','Democratic').str.replace('Democrat ', 'Democratic ').str.replace('Ind. ', '').str.replace('GOP', 'Republican').str.replace('Ind ', '').str.replace('&#39;',"'").str.replace(' R ',' REPUBLICAN ').str.upper()
#print(sorted(df.party_detailed.unique()))

df['party_detailed'] = df.party_detailed.replace({'(DEMOCRATIC PARTY NOMINEES)' : 'DEMOCRAT',
                                       '(PREFERS DEMOCRATIC PARTY)' : 'DEMOCRAT', '(DEMOCRATIC PARTY NOMINEES)': 'DEMOCRAT',
                                       '(PREFERS REPUBLICAN PARTY)': 'REPUBLICAN',
                                       '(REPUBLICAN PARTY NOMINEES)': 'REPUBLICAN',
                                       '(PREFERS LIBERTARIAN PARTY)' : 'LIBERTARIAN', '(LIBERTARIAN PARTY NOMINEES)':'LIBERTARIAN',
                                       '(GREEN PARTY NOMINEES)': 'GREEN',
                                       '(PREFERS WA PROGRESSIVE PARTY)': 'WA PROGRESSIVE',
                                       '(PREFERS INDEPENDENT PARTY)': 'INDEPENDENT',
                                       "(PREFERS SEATTLE PEOPLE'S PARTY)": "SEATTLE PEOPLES",
                                       "(SOCIALISM AND LIBERATION PARTY NOMINEES)": 'SOCIALISM AND LIBERATION',
                                       "(SOCIALIST WORKERS PARTY NOMINEES)":'SOCIALIST WORKERS',
                                       '(PREFERS THE ALLIANCE PARTY)': 'THE ALLIANCE',
                                       '(STATES NO PARTY PREFERENCE)': 'INDEPENDENT'})

df['party_simplified'] = df.party_detailed.replace({'Green': 'OTHER', 'THE ALLIANCE': 'OTHER',
                                       'WA PROGRESSIVE': 'OTHER', "SEATTLE PEOPLE'S": 'OTHER',
                                       'SOCIALISM AND LIBERATION': 'OTHER',
                                       'SOCIALIST WORKERS': 'OTHER', 'INDEPENDENT': 'OTHER'})
#print(sorted(df.party_detailed.unique()))
#print(sorted(df.party_simplified.unique()))




df.loc[df.JurisdictionName.str.contains('State Executive'), 'district'] = 'STATEWIDE'
df.loc[(df.JurisdictionName.str.contains('Federal'))&(df.district==''), 'district'] = 'STATEWIDE'


df = df.applymap(lambda x: x.strip() if type(x)==str else x)


parties = pd.read_csv('raw/local_party_crosswalk.csv')

df = pd.merge(df, parties, on='candidate', how = 'left')
#df['party_detailed'] = df['party_detailed'].fillna(df['party'])

df['party_detailed'] = df['party_detailed'] + df['party'].replace(np.nan,'')
#print(df.party_detailed.unique())

df.loc[df['candidate'] == 'JIM NELSON', 'party_detailed'] = 'NONPARTISAN'
df.loc[df['candidate'] == 'JUSTIN M FORSMAN', 'party_detailed'] = 'REPUBLICAN'
df.loc[df['candidate'] == 'WRITEIN', 'party_detailed'] = ''
df.loc[df['office']=='PIERCE SHERIFF','office'] = 'SHERIFF'
df.loc[df['party_detailed']=='NONPARTISANNONPARTISAN','party_detailed'] = 'NONPARTISAN'

df['party_simplified'] = df.party_detailed.replace({'GREEN': 'OTHER', 'THE ALLIANCE': 'OTHER',
                                       'WA PROGRESSIVE': 'OTHER', "SEATTLE PEOPLE'S": 'OTHER',
                                       'SOCIALISM AND LIBERATION': 'OTHER',
                                       'SOCIALIST WORKERS': 'OTHER', 'INDEPENDENT': 'OTHER',
                                       'CONSERVATIVE':'OTHER'})

df.loc[df.Race == 'PUBLIC UTILITY DISTRICT PUBLIC UTILITY COMMISSIONER 1', 'district']='001'
df.loc[df.Race == 'PUD ALL PUBLIC UTILITY DIST COMMISSIONER A', 'district']='A AT LARGE'
df.loc[df.Race == 'CLARK PUBLIC UTILITY DISTRICT COMMISSIONER, DISTRICT NO. 3', 'district']='003'
df.loc[df.Race == 'PUBLIC UTILITIES DISTRICT NO 1 Commissioner District 1', 'district']='001'
df.loc[df.Race == 'PUBLIC UTILITY DIST 1 Commissioner District No. 2', 'district']='002'
df.loc[df.Race == 'PUD ALL PUBLIC UTILITY DIST COMMISSIONER DIST 1', 'district']='001'
df.loc[df.Race == 'PUBLIC UTILITY DISTRICT # 1 Public Utility District #1 Commissioner Pos. 3', 'district']='001, SEAT 3'
df.loc[df.Race == 'PUBLIC UTILITY DISTRICT - 001 Commissioner #2', 'district']='001, SEAT 2'
df.loc[df.Race == 'PUBLIC UTILITY DISTRICT 1 Commissioner 1', 'district']='001, SEAT 1'
df.loc[df.Race == 'PUBLIC UTILITY DISTRICT COUNTYWIDE Commissioner #1', 'district']='SEAT 1'
df.loc[df.Race == 'PUBLIC UTILITY DISTRICT COUNTYWIDE Commissioner #3', 'district']='003'
df.loc[df.Race == 'PUD (COUNTYWIDE) PUBLIC UTILITY COMMISSIONER #3', 'district']='003'
df.loc[df.Race == 'PUBLIC UTILITY DIST 1 COMMISSIONER NO. 1', 'district']='001'
df.loc[df.Race == 'PUBLIC UTILITY DIST 1 Commissioner #3', 'district']='003'
df.loc[df.Race == 'PUD District 2 Public Utility Commissioner 1', 'district']='002, 001'
df.loc[df.Race == 'Public Utility Dist 3 Commissioner Dist 1 Commissioner District 2', 'district']='003, 002'
df.loc[df.Race == 'Public Utility Dist 1 Commissioner Dist 1 Commissioner District 2', 'district']='001, 002'
df.loc[df.Race == 'Public Utility Dist 3 Commissioner District 2', 'district']='001, 002'
df.loc[df.Race == 'Public Utility Dist 1 Commissioner District 2', 'district']='001, 002'

df.loc[df.Race == 'Public Utility District (ALL) PUBLIC UTILITY COMMISSIONER #2', 'district']='002'
df.loc[df.Race == 'Public Utility District 1 All Commissioner District 1', 'district']='001'
df.loc[df.Race == 'Public Utility District 1 All Commissioner 1', 'district']='001'
df.loc[df.Race == 'Public Utility District Commissioner, District 2', 'district']='002'
df.loc[df.Race == 'Thurston Public Utility District Commissioner, District No. 3', 'district']='003'
df.loc[df.Race == 'Public Utility District No. 1 Commissioner District 2', 'district']='001'
df.loc[df.Race == 'Public Utility District All Commissioner 1', 'district']='001'
df.loc[df.Race == 'Public Utility District Commissioner #2', 'district']='002'
df.loc[df.Race == 'Public Utility District Countywide PUD Commissioner #2', 'district']='002'
df.loc[df.Race == 'PUBLIC UTILITY DISTRICT Commissioner #3', 'district']='003'
df.loc[df.Race == 'Grant County PUD All Commissioner Dist #3', 'district']='003'
df.loc[df.Race == 'Grant County PUD All Commissioner Dist #A AL', 'district']='A'
df.loc[df.Race == 'PUD District PUD Comm (3)', 'district']='003'
df.loc[df.Race == 'OKANOGAN PUD ALL Commissioner Dist. 1', 'district']='001'
df.loc[df.Race == 'SKAGIT PUD DISTRICT COUNTYWIDE Commissioner 1', 'district']='001'



nonparts = ['PUBLIC UTILITY DISTRICT COMMISSIONER','SUPERIOR COURT JUDGE',
            'SUPERINTENDENT OF PUBLIC INSTRUCTION','SUPREME COURT JUSTICE',
            'COURT OF APPEALS JUDGE','CHARTER REVIEW COMMISSIONER AT-LARGE',
            'NORTHEAST ELECTORAL DISTRICT JUDGE']
for office in nonparts:
    df.loc[df.office == office,'party_detailed']='NONPARTISAN'
    df.loc[df.office == office,'party_simplified']='NONPARTISAN'


print(df.party_detailed.unique())

df_final = df[["precinct", "office", "party_detailed", "party_simplified", "mode", 
               "votes", "candidate", "district", "dataverse",  "stage", "special", 
               "writein","date", "year","county_name", "county_fips",
               "jurisdiction_name", "jurisdiction_fips", "state", "state_po",
               "state_fips", "state_cen", "state_ic","magnitude", "readme_check"]].copy()



df_final.to_csv("C:/Users/abguh/Desktop/urop/2020-precincts/precinct/WA/2020-wa-precinct-general.csv", index = False)
#df.to_csv('C:/Users/abguh/Desktop/urop/2020-precincts/precinct/WA/2020-wa-precicnt-general-alldata.csv', index = False)
'''
a = df[df.office.str.contains('UTIL')][['Race', 'district','candidate','county_name','office']]
a=a.drop_duplicates()
#df = df.iloc[:35000][:]

b = df[df.Race.str.contains(' PUD ')][['Race', 'district','candidate','county_name','office']]
b=b.drop_duplicates()

c = df[df.office.str.contains('COUNTY COUNCIL')][['Race', 'district','candidate','county_name','office']]
c=c.drop_duplicates()
'''

print(df.district.unique())

'''
PUD
asotin: judy ridge, district 1
chelan, steve mckenna, district a at large
clallam, rick paschall, district 2
cowlitz, bruce pollock, district 1
douglas, molly simpson, district 2
ferry, doug aubertin, district 3
franklin, bill gordon, district 2
kittitas, rick catlin, district 1
klickitat, dan g gunkel, district 1 pos 3
lincoln, grant wagner, district 1

okanogan, scott vejraska, district 1
pacific, pam hickey, district 1
pend orielle, curtis j knapp, none
skamania, liz green, district 3
wahkiakum


#CHECKS

for col in df:
    print(col)
    print("")
    print(sorted(df[col].unique()))
    print("\n\n----------------\n\n")
    

#check dataverse
for i in ["PRESIDENT","SENATE", "HOUSE", "STATE", "LOCAL"]:
    print(i)
    print(sorted(df_state['office'][df.dataverse==i].unique()))
    print("\n------------------\n")

print("number of columns/variables:", len(df.columns)) #should be 24
print("columns are: ", df.columns)
'''