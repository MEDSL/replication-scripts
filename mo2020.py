#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 24 07:27:55 2021

@author: darsh
"""
import pandas as pd
import numpy as np
import csv

#read data + setup
path = 'raw/Files/Final Precinct data 2020 - amendments on same tab as candidates.xlsx'
df = pd.read_excel(path, header = 5, skipfooter=3)
df = pd.DataFrame(df)

#remove blank rows
df = df[['County Name', 'Precinct Code', 'Precinct Name', 'Office Title',
       'Candidate Ballot Name', 'Political Party', 'Yes votes', 'No votes']]

#CAPITALIZE and remove extraneous saces
df = df.applymap(lambda x:x.upper() if type(x) == str else x)
df = df.applymap(lambda x:x.strip() if type(x) == str else x)
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# print(df['Office Title'].unique()) #only a few offices in data

def get_office(x):
    if 'U.S. PRESIDENT AND VICE PRESIDENT' in x:
        return 'US PRESIDENT'
    elif 'U.S. REPRESENTATIVE' in x:
        return 'US HOUSE'
    elif 'STATE REPRESENTATIVE' in x:
        return 'STATE HOUSE'
    elif 'STATE SENATOR' in x:
        return 'STATE SENATE'
    elif 'CIRCUIT JUDGE' in x:
        return 'CIRCUIT JUDGE'
    else:
        return x

df['office']=df['Office Title'].apply(get_office)
#---------------------------------------------------------------------------------------------------------------------------------------------------
statewide =  ['U.S. PRESIDENT AND VICE PRESIDENT', 'GOVERNOR', 'LIEUTENANT GOVERNOR','SECRETARY OF STATE',
              'STATE TREASURER', 'ATTORNEY GENERAL','CONSTITUTIONAL AMENDMENT']

def get_district(x):
    if 'CIRCUIT JUDGE' in x:
        dist = x[16:]
    elif 'DISTRICT' in x:
        dist = ''.join([str(n) for n in list(x) if n.isdigit()])
    elif any(i in x for i in statewide):
        dist = 'STATEWIDE'
    else:
        return ''
    return dist.zfill(3)

df['district'] = df['Office Title'].apply(get_district)
# #---------------------------------------------------------------------------------------------------------------------------------------------------
#Votes also have a 'NO' section for amendment elections, we can melt that down and put it in candidate
df = pd.melt(df, id_vars = ['County Name', 'Precinct Code', 'Precinct Name', 'Office Title',
                            'Candidate Ballot Name', 'Political Party','office', 'district'],
             value_vars = ['Yes votes','No votes'],
             var_name = 'y_or_n', value_name = 'votes')

df = df.loc[df['votes'].notnull()] #remove the extra rows for elections with only "yes" (all except the amendments)

def y_or_n(office, y_or_n):
    if 'CONSTITUTIONAL AMENDMENT' in office:
        if y_or_n == 'Yes votes':
            return 'YES'
        else:
            return 'NO'
    else:
        return ''
df['y_or_n'] = df.apply(lambda df: y_or_n(df['office'], df['y_or_n']), axis=1)
df['Candidate Ballot Name'].replace(np.nan,'', inplace = True)
df['candidate'] = df['Candidate Ballot Name'].astype(str) + df['y_or_n']

def votes(x):
    return int(x)
df['votes'] = df['votes'].apply(votes)
#---------------------------------------------------------------------------------------------------------------------------------------------------
# check = df.loc[df['Candidate Ballot Name'].notnull()]
# check = check.loc[check['Candidate Ballot Name'].str.contains(',')]
# check = check.loc[check['office'] == 'STATE HOUSE']
# print(check['Candidate Ballot Name']) --> only "JOHN D. BOYD, JR." is a non-prez candidate with ","


def candidate(x):
    #removing the name of VP from presidents
    if type(x) == str and ',' in x and x != 'JOHN D. BOYD, JR.':
        return x.split(',')[0]
    elif x == 'KASEY WELLS RACHEL WELLS':
        return 'KASEY WELLS' 
    elif x == 'ALISSIA CANADAY':
        return 'ALISSIA CANADY' 
    elif x == 'NARTIN SCHULTE':
        return 'MARTIN SCHULTE' 
    elif x == 'EMMANUEL CLEAVER II':
        return 'EMANUEL CLEAVER II'
    else:
        return x
df['candidate'] = df['candidate'].apply(candidate)

def punctuation(x):
    x = str(x)
    x = x.replace(".","")
    x = x.replace(",","")
    x = x.replace("(",'"')
    x = x.replace(")",'"')
    return x
df['candidate'] = df['candidate'].apply(punctuation)


# #---------------------------------------------------------------------------------------------------------------------------------------------------
# 'WI' under party is write-ins

def writein(x):
    if x == 'WI':
        return 'TRUE'
    else:
        return 'FALSE'

df['writein'] = df['Political Party'].apply(writein)
# #---------------------------------------------------------------------------------------------------------------------------------------------------
# print(df['party'].unique()) ---> only ['REP' 'DEM' 'LIB' 'GRE' 'CST' 'WI' 'IND']

def party_det(x):
    if x == 'REP':
        return 'REPUBLICAN'
    elif x == 'DEM':
        return 'DEMOCRAT'
    elif x == 'LIB':
        return 'LIBERTARIAN'
    elif x == 'GRE':
        return 'GREEN'
    elif x == 'WI': #leave party blank for write ins
        return ''
    elif x == 'CST':
        return 'CONSTITUTION'
    else:
        return 'NONPARTISAN'

df['party_detailed'] = df['Political Party'].apply(party_det)
# #---------------------------------------------------------------------------------------------------------------------------------------------------
main_parties = ['REPUBLICAN','DEMOCRAT','LIBERTARIAN']
other_parties = ['GREEN','CONSTITUTION']

def party_sim(x):
    for p in main_parties:
        if x == p:
            return p
    if any(x == i for i in other_parties):
        return 'OTHER'
    else:
        return x

df['party_simplified'] = df['party_detailed'].apply(party_sim)
# #---------------------------------------------------------------------------------------------------------------------------------------------------
state = ['GOVERNOR','LIEUTENANT GOVERNOR','SECRETARY OF STATE','STATE TREASURER','ATTORNEY GENERAL',
          'STATE HOUSE','STATE SENATE','CIRCUIT JUDGE','CONSTITUTIONAL AMENDMENT']

def dataverse(x):
    if x == 'US PRESIDENT':
        return 'PRESIDENT'
    elif x == 'US HOUSE':
        return 'HOUSE'
    elif any(s in x for s in state):
        return 'STATE'
    else:
        return 'LOCAL'

df['dataverse'] = df['office'].apply(dataverse)
#---------------------------------------------------------------------------------------------------------------------------------------------------
#get fips code dataframe for MO counties
df['county'] = df['County Name'].fillna('')

county_fips_path = '../../help-files/county-fips-codes.csv'
fips = pd.read_csv(county_fips_path, delimiter=',', header=0)
fips = pd.DataFrame(fips)
fips = fips.loc[fips['state']=='Missouri']
fips_dict = dict(zip(fips.county_name, fips.county_fips))
fips_dict['']=''

def fips(x):
    if x == 'DE KALB': #standardize spelling to the fips format
        x = 'DEKALB'
    code = fips_dict[x]
    return str(code)

df['county_fips'] = df['county'].apply(fips)
df['jurisdiction_fips'] = df['county_fips']

df['county_name'] = df['county']
df['jurisdiction_name'] = df['county']
#---------------------------------------------------------------------------------------------------------------------------------------------------
#MAIN ISSUE: UNDER 'precinct' EACH COUNTY HAS THE SOME ADDITIONAL VALUES AS "PRECINCTS":
    
#"ABSENTEE" OR "PROVISIONAL" - Net Absentee votes for the county, without precinct level breakdown:
#                  ACTION -> we will label precicnt as 'COUNTY FLOATING' and the mode 'ABSENTEE'/'PROVISIONAL'
   
#"FEDERAL"/"MIL/OS ABSENTEES" - Net UOCAVA (Uniformed and Overseas Citizens Absentee Voting Act)
#                               votes of people from that county, but no precinct level breakdown:
#                  ACTION -> we will lablel precint as 'COUNTY FLOATING' and mode 'UOCAVA'

def mode(x):
    
    if x == 'FEDERAL' or x == 'MIL/OS ABSENTEES':
        return 'UOCAVA'
    elif type(x) == str and 'ABSENTEE' in x:
        return 'ABSENTEE'
    elif type(x) == str and 'PROVISIONAL' in x:
        return 'PROVISIONAL'
    elif type(x) == str and x=='MAIL-IN':
        return 'MAIL'
    else:
        return 'ELECTION DAY'
df['mode'] = df['Precinct Name'].apply(mode)

def precinct(x):
    if type(x) == str:
        if 'ABSENTEE' in x or x == 'FEDERAL' or 'PROVISIONAL' in x or x == 'MAIL-IN':
            return 'COUNTY FLOATING'
        elif any (z in x for z in ['WRITE-IN','WRITE-INS','WRITE INS','WRITE IN','WRITE - IN']):
            return 'COUNTYWIDE WI' #standardize ['precinct'] == 'WRITE-IN' rows
        else:
            return x
    else:
        return x
#df['precinct'] = df['Precinct Name'].apply(precinct)
df['Precinct Code']=df['Precinct Code'].astype(str)
df['precinct'] = df['Precinct Code'] + '_' + df['Precinct Name'].apply(precinct).astype(str)

#"WRITE-IN" - listed as ['WRITE-IN' 'WRITE-INS' 'WRITE INS' 'WRITE IN','WRITE - IN']

#Irrelevent in pointing out write-ins since in the 'party' column all actual write-ins are marked "WI"

#The check below shows that all "WRITE-IN" 'precincts' that are NOT "WI" under 'party' have 0 votes. 
# check = df.loc[df['precinct'] == 'COUNTYWIDE WI']
# check = check.loc[check['writein']=='FALSE']
# print(check['votes'].unique()) 
# #-------------> returns [0, nan] <---------------
# ACTION -> DELETE THESE by marking which rows to delete

indexNames = df[(df['precinct'] == 'COUNTYWIDE WI') & (df['writein'] == 'FALSE')].index
df.drop(indexNames, inplace = True)

#Only actual write-in candidates have non-zero votes in 3 different ways:
    # 1) Votes under precinct breakdown are NaN, there is a county vote total under ['precinct'] == 'WRITE-IN'
    # ACTION --> Delete the NaN values and kept the total
    # 2) Votes ARE under precinct breakdown, the ['precinct'] == 'WRITE-IN' is NaN
    # ACTION --> Delete the "Total" which is null, keep precinct breakdown
    # 3) Votes are under BOTH precinct breakdown and "Total" under ['precinct'] == 'WRITE-IN'
    # ACTION --> Check if the votes add up, if yes delete "Total" Row to avoid double counting
    #                                       if no mark 'TRUE' in readme_check

#dropping rows with writeins having 0 votes 
indexNames = df[(df['writein'] == 'TRUE') & (df['votes']==0)].index
df.drop(indexNames, inplace = True)

to_check = df.loc[df['writein'] == 'TRUE']
to_check = to_check[['county','precinct','candidate','votes','mode']]
# print(to_check) #---> only 133 rows, check by creating its own csv --.
# #                                                                    |
# to_check.to_csv('check-write-ins.csv', index = False)           #<---'

#---> after dropping votes = 0 all counties are:
    #either only total county floating write-in or
    #write-in with precinct level breakdown
    #No chance of double counting! Yay!

#go back to replace 'COUNTYWIDE WI" with "COUNTY FLOATING"
df['precinct'].replace('COUNTYWIDE WI', 'COUNTY FLOATING', inplace=True)
#---------------------------------------------------------------------------------------------------------------------------------------------------
#all only have one winner from lookig at unique values of office and candidates
df['magnitude'] = '1'
#sec of state website and ballotopedia indicated no special elections
df['year']='2020'
df['date']='2020-11-03'
df['special'] = 'FALSE'
df['stage'] = 'GEN'
df['state'] = 'MISSOURI'
df['state_po']='MO'
df['state_fips']= '29'
df['state_cen']= '43'
df['state_ic']= '34'
df['readme_check']='FALSE'

df = df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes",
          "candidate", "district", "dataverse","state", "special", "writein","date","year",
          "county_name","county_fips", "jurisdiction_name","jurisdiction_fips", "stage",  "state_po",
          "state_fips", "state_cen", "state_ic", "readme_check", 'magnitude']]

df = df.applymap(lambda x:x.strip() if type(x) == str else x)
df.fillna('', inplace=True)
df.to_csv('2020-mo-precinct-general.csv', index = False, quoting=csv.QUOTE_NONNUMERIC)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
