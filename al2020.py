# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 07:37:07 2021

@author: abguh
"""

import pandas as pd
import os
import numpy as np
import re

path = '/Users/declanchin/Desktop/MEDSL/2020-precincts/precinct/AL/raw/2020 General Precinct Results'
os.chdir(path)

df_final = pd.DataFrame()
for file in os.listdir():
    df = pd.read_excel(file)
    df = df.replace(np.nan, '0', regex = True).replace('_','', regex = True)
    df = pd.melt(df, id_vars = ['Contest Title','Party', 'Candidate'], var_name = 'precinct', value_name = 'votes')
    df['county_name'] = file[13:-4].upper()
    df['mode'] = 'TOTAL'
    df.votes = df.votes.replace('', '0', regex = True).astype(int)
    df.loc[df.precinct == 'ABSENTEE', 'mode'] = 'ABSENTEE'
    df.loc[df.precinct == 'PROVISIONAL', 'mode'] = 'PROVISIONAL'
    df.precinct = df.precinct.apply(lambda x: 'COUNTY FLOATING' if x == 'ABSENTEE' or x=='PROVISIONAL' else x)
    df_final = pd.concat([df_final, df], axis = 0).astype(str).applymap(lambda x: x.strip() if type(x)==str else x)


#print(sorted(df_final['Contest Title'].unique()))

l = list()
def get_district(x):
    x = x.replace('NO. ', '')
    if 'CONGRESSIONAL' in x: return x[x.find('CONGRESS')-4].zfill(3)
    if 'CIRCUIT COURT' in x: 
        return 'CIRCUIT ' + (x[21:23].strip('T')) + ', PLACE ' + x[-2:].strip()
    elif ('RUSSELL COUNTY CONSTABLE' in x) and ('PLACE' in x):
        return re.findall('\d+', x)[0].zfill(3) + ', PLACE ' + re.findall('\d+', x)[1]
    elif 'MEMBER ST. CLAIR COUNTY BOARD OF EDUCATION' in x:
        return x.replace('MEMBER ST. CLAIR COUNTY BOARD OF EDUCATION ','')
    elif 'MEMBER ST. CLAIR COUNTY BD OF EDUCATION' in x:
        return x.replace('MEMBER ST. CLAIR COUNTY BD OF EDUCATION ',"")
    elif ('MEMBER, BLOUNT COUNTY, DISTRICT' in x) and ('BOARD OF EDUCATION' in x):
        return '003'
    elif 'PLACE' in x: return x[x.find('PLACE'):]
    elif 'CONSTABLE' in x:
        if 'PLACE' in x: 
            #print(x)
            return x[x.find('DISTRICT'):]
        if 'PRECINCT' in x: return x[x.find('PRECINCT'):]
        elif 'DISTRICT' in x: 
           return x[x.find('DISTRICT')+9:x.find('DISTRICT')+11].strip().zfill(3)
        elif 'BEAT' in x: return x[x.find('BEAT'):]
    elif 'LIMESTONE COUNTY COMMISSION, DIST' in x:
        return x[-1].zfill(3)
    elif ('DISTRICT' in x) and ('DISTRICT COURT' not in x):
        return x[-2:].strip().zfill(3)
    elif 'SENATOR' in x or 'PUBLIC SERVICE COMMISSION' in x or 'PRESIDENT' in x: return 'STATEWIDE'
    else: return ''
        

def fix_office(x):
    if x.split(' ')[1] == 'COUNTY': x = ' '.join(x.split(' ')[2:])
    x = x.replace(' JEFFERSON COUNTY','')
    if '(' in x: x = x[:x.find(' (')]
    if 'CONSTABLE' in x: return 'COUNTY CONSTABLE'
    if 'STATE BOARD OF EDUCATION' in x: return 'STATE BOARD OF EDUCATION'
    elif 'MEMBER,' in x and 'BOARD OF EDUCATION' not in x: 
        return 'COUNTY COMMISSION MEMBER'
    elif 'MEMBER' in x: 
        #l.append(x)
        return 'COUNTY BOARD OF EDUCATION MEMBER'
    elif 'SUPERINTENDENT' in x: return 'COUNTY BOARD OF EDUCATION SUPERINTENDENT'
    elif 'DISTRICT COURT' in x: return 'DISTRICT COURT JUDGE'
    elif 'CIRCUIT COURT' in x: return 'CIRCUIT COURT JUDGE'
    elif 'ASSOCIATE JUSTICE' in x: return 'SUPREME COURT ASSOCIATE JUSTICE'
    elif 'CIVIL APPEALS' in x: return 'COURT OF CIVIL APPEALS JUDGE'
    elif 'CRIMINAL APPEALS' in x: return 'COURT OF CRIMINAL APPEALS JUDGE'
    elif 'UNITED STATES REPRESENTATIVE' in x: return 'US HOUSE'
    elif 'STATES SENATOR' in x: return 'US SENATE'
    elif 'CHAIRMAN' in x:
        if 'EDUCATION' not in x: return 'COUNTY COMMISSION CHAIRMAN'
        else: return 'COUNTY BOARD OF EUDUCATION CHAIRMAN'
    elif x == 'PRESIDENT, PUBLIC SERVICE COMMISSION': return 'PUBLIC SERVICE COMMISSION PRESIDENT'
    elif 'PRESIDENT AND VICE' in x: return 'US PRESIDENT'
    elif x == 'SPECIAL ELECTION': 
        return 'SPECIAL ELECTION PROPOSED TAXATION'
    elif x == 'STRAIGHT PARTY': return 'STRAIGHT TICKET'
    if 'DEPUTY TREASURER' in x: return 'DEPUTY TREASURER BESSEMER DIVISION'
    if 'REVENUE COMMISSIONER' in x: return 'REVENUE COMMISSIONER'
    else: return x
    
def fix_candidate(x):
    if x == 'Christopher T. Carter (Chris Carte': return 'CHRISTOPHER T "CHRIS" CARTER'
    if "T. Andre'" in x: return 'T ANDRE DOUCET'
    x = x.upper().replace('.','').replace('(','"').replace(')','"').replace(',','').replace("'",'"')
    if 'ALABAMA' in x: return 'STRAIGHT TICKET'
    if x == 'WRITE-IN': return 'WRITEIN'
    if x in ['DONALD J TRUMP MICHAEL R PENC', 'JOSEPH R BIDEN KAMALA D HARRI']: return ' '.join(x.split()[0:3])
    if 'JO JORGENSEN' in x: return 'JO JORGENSEN'
    return x

def get_dataverse(x):
    if 'BALLOTS CAST' in x: return ''
    if x == 'US PRESIDENT': return 'PRESIDENT'
    if x == 'US HOUSE': return 'HOUSE'
    if x == 'US SENATE': return 'SENATE'
    if x == 'STRAIGHT TICKET': return ''
    if x == 'REGISTERED VOTERS - TOTAL': return ''
    if x in ['STATE BOARD OF EDUCATION', 'PUBLIC SERVICE COMMISSION PRESIDENT', 
             'CIRCUIT COURT JUDGE', 'SUPREME COURT ASSOCIATE JUSTICE',
             'COURT OF CRIMINAL APPEALS JUDGE', 'COURT OF CIVIL APPEALS JUDGE']: return 'STATE'
    else: return 'LOCAL'

df_final.county_name = df_final.county_name.replace({'STCLAIR': 'ST. CLAIR'})
df_final['district'] = df_final['Contest Title'].apply(get_district).replace('  ', ' ', regex = True)
df_final['office'] = df_final['Contest Title'].apply(fix_office).str.replace(',','').str.replace('  ',' ')
df_final['candidate'] = df_final.Candidate.apply(fix_candidate)
df_final['party_detailed'] = df_final.Party.replace({'DEM': 'DEMOCRAT','REP':'REPUBLICAN',
                                                     'LIB': 'LIBERTARIAN','IND':'INDEPENDENT', 'NON': 'NONPARTISAN'})
df_final['party_simplified'] = df_final.party_detailed.replace({'INDEPENDENT': 'OTHER'})
df_final['dataverse'] = df_final.office.apply(get_dataverse)
df_final['state'] = 'Alabama'
countyFips = pd.read_csv("/Users/declanchin/Desktop/MEDSL/2020-precincts/help-files/county-fips-codes.csv").astype(str)
df_final = pd.merge(df_final, countyFips, on = ['state','county_name'],how = 'left')
df_final.county_fips = df_final.county_fips.astype(str).str.upper().str.zfill(5)
df_final['jurisdiction_fips'] = df_final.county_fips

df_final.state = df_final.state.str.upper()
# df_final['mode'] = 'TOTAL'
df_final['year'] = '2020'
df_final['stage'] = 'GEN'
df_final['state_po'] = 'AL'
df_final['state_fips'] = '1'
df_final['state_cen'] = '63'
df_final['state_ic'] = '41'
df_final['date'] = '2020-11-03'
df_final['special'] = 'FALSE'
df_final['writein'] = 'FALSE'
df_final['readme_check'] = 'FALSE'
df_final['jurisdiction_name'] = df_final.county_name
df_final.loc[df_final.candidate == 'WRITEIN', 'writein'] = 'TRUE'
df_final.loc[df_final.candidate == 'WRITEIN', 'party_simplified'] = ''
df_final.loc[df_final.candidate == 'WRITEIN', 'party_detailed'] = ''


#print(sorted(df_final.Candidate.unique()))
#print(sorted(df_final.Party.unique()))

a = list()
for item in l:
    if item not in a:
        print(item)
        a.append(item)

#editing this to set magnitude == 0 for registered/ballots cast
#in accordance with the precinct readme. Declan Chin 3/30/21
def magnitude(cand, office):
    if cand in ['BALLOTS CAST - BLANK', 'BALLOTS CAST - TOTAL', 'REGISTERED VOTERS - TOTAL',
             'STRAIGHT TICKET']: return 0
    if office == 'STRAIGHT TICKET': return 0
    else: return 1
    
df_final['magnitude'] = df_final.apply(lambda x: magnitude(x['candidate'], x['office']), axis=1)

df_final.loc[df_final.candidate == 'BELINDA PALMER MCRAE', 'district'] = '007'

df_final = df_final[["precinct", "office", "party_detailed", "party_simplified", 
               "mode", "votes", "candidate", "district", "dataverse",  
               "stage", "special", "writein","date", "year","county_name", 
               "county_fips","jurisdiction_name", "jurisdiction_fips", 
               "state", "state_po","state_fips", "state_cen", 
               "state_ic", "readme_check", 'magnitude']].copy()

df_final.to_csv("/Users/declanchin/Desktop/MEDSL/2020-precincts/precinct/AL/2020-al-precinct-general.csv", index = False)

df1 = df_final[df_final.office == 'STATE BOARD OF EDUCATION']
print(sorted(df1.district.unique()))

''' 
state board of education -> 4 seats
for the provisional and absentee write COUNTY FLOATING in the preccinct variable 

straight party ticket - put "STRAIGHT TICKET" as the value in office, 
"STRAIGHT TICKET" as the value in candidate, the full party name in party 
(following directions for party labels for that variable), and an NA value for dataverse

statistics:put in office, candidate blank, party if applicable

for constable: there's only one per county, but they put the district/precinct/beat that
the voters are in, so i put that in district column
    '''