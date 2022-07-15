#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 17:17:54 2021

@author: jennifermiranda
"""

import pandas as pd
import numpy as np
import csv

df = pd.read_csv('raw/resultsbyprecinct.txt', delimiter=",")
df = df.fillna("")

df = df.rename(columns={"Race Statistics": "office", "Number of Precincts": "candidate", "HD99 Fed Overseas Absentee ": "precinct", "NP.2": "party_detailed", "0": "votes"})

df = df.drop([ 'Unnamed: 8', 'NP', 'NP.1', 'Total'], axis=1)

# Use merge_on_statecodes.csv to get info for AK: 

df["state"] = 'ALASKA'
df["state_po"] = 'AK'
df["state_fips"] = '02'
df["state_cen"] = '94'
df["state_ic"] = '81'

df["votes"] = df["votes"].apply(str)
df["stage"] = "GEN"
df["date"] = "2020-11-03"
df["year"] = "2020"

df["mode"] = "ELECTION DAY"
df.loc[df['precinct'].str.contains('Early Voting'), 'mode'] = 'EARLY VOTING'
df.loc[df['precinct'].str.contains('Absentee'), 'mode'] = 'ABSENTEE'
 
df["special"] = "FALSE"

df['writein'] = 'FALSE'
df['county_name'] = ""
df['county_fips'] = ""
df['magnitude'] = 1

def makeDummyColumn(x):
    
    if ('Absentee - 1' in x or 'Absentee - 2' in x) and len(x) >= 49: 
        x = x[:-27]
    elif ('Absentee - 1' in x or 'Absentee - 2' in x) and len(x) < 49: 
        x = x[:-26]
    elif ('Early Voting - 1' in x or 'Early Voting - 2' in x) and len(x) >= 57:
        x = x[:-31]
    elif ('Early Voting - 1' in x or 'Early Voting - 2' in x) and len(x) < 57:
        x = x[:-30]
    elif ('Question - 1' in x or 'Question - 2' in x) and len(x) >= 50:
        x = x[:-28]
    elif ('Question - 1' in x or 'Question - 2' in x) and len(x) < 50:
        x = x[:-27]
    elif '32-847' in x:
        x = '32-847 Seldovia/Kachemak Bay'
    elif '31-370' in x:
        x = '31-370 Kachemak/Fritz Creek'
    else: 
        return x
    return x

df['precinct_dummy'] = df['precinct'].apply(makeDummyColumn)
df['precinct_dummy'] = df['precinct_dummy'].str.replace('\s+', ' ',regex=True)

fips = pd.read_csv('../../help-files/ak_jurisdiction_crosswalk.csv')

fips = fips.rename(columns={"precinct": "precinct_dummy"})
fips = fips.applymap(str)
df=df.applymap(lambda x: x.strip() if type(x)==str else x)
df = pd.merge(df, fips, on = ['precinct_dummy'], 
             how = 'left')

df = df.drop(['precinct_dummy'], axis=1)

df.loc[df['candidate'].str.contains('Number of Precincts for Race'), 'office'] = 'Number of Precincts for Race'
df.loc[df['candidate'].str.contains('Number of Precincts'), 'office'] = 'Number of Precincts'
df.loc[df['candidate'].str.contains('Number of Precincts Reporting'), 'office'] = 'Number of Precincts Reporting'
df.loc[df['candidate'].str.contains('Registered Voters'), 'office'] = 'Registered Voters'
df.loc[df['candidate'].str.contains('Times Counted'), 'office'] = 'Times Counted'

df.loc[df['office'].str.contains('Number of Precincts for Race'), 'mode'] = 'TOTAL'
df.loc[df['office'].str.contains('Number of Precincts'), 'mode'] = 'TOTAL'
df.loc[df['office'].str.contains('Number of Precincts Reporting'), 'mode'] = 'TOTAL'
df.loc[df['office'].str.contains('Registered Voters'), 'mode'] = 'TOTAL'
df.loc[df['office'].str.contains('Times Counted'), 'mode'] = 'TOTAL'

df['candidate'] = df['candidate'].replace({'Number of Precincts for Race': "",
                                           'Number of Precincts': "",
                                              'Number of Precincts Reporting': "",
                                              'Registered Voters': "",
                                               'Times Counted': ""})

df['party_detailed'] = df['party_detailed'].replace({'NP': "",
                                                     '"': "",
                                                    'CON""': "CONSTITUTION",
                                                    'DEM""': "DEMOCRAT",
                                                    'ALI""': "ALLIANCE",
                                                    'GRN""': "GREEN",
                                                    'LIB""': "LIBERTARIAN",
                                                    'NOM""': "INDEPENDENT",
                                                    'REP""': "REPUBLICAN",
                                                    'AIP""': "ALASKA INDEPENDENCE"})

df['party_simplified'] = df['party_detailed']
df['party_simplified'] = df['party_detailed'].replace({"CONSTITUTION": "OTHER",
                                                    "ALLIANCE": "OTHER",
                                                    "GREEN": "OTHER",
                                                    "INDEPENDENT": "OTHER",
                                                    "ALASKA INDEPENDENCE": "OTHER"})

def cleanCandidate(x):

    if "YES" in x or "NO" in x or "Number of Precincts" in x:
        if '""' in x:
            return x[:-2]
        else:
            return x
    if '""' in x:
        x = x[:-2]
    if " /" in x:
        index = x.index(" /")
        x = x[:index]
    if len(x) < 1:
        x = ""
    else: 
        return x.upper() 
    return x.upper()

df['candidate'] = df['candidate'].apply(cleanCandidate)
df['candidate'] = df['candidate'].str.replace('\s+', ' ',regex=True)

temp = df.candidate.str.split(expand=True,)
temp = temp.replace(np.nan, "", regex = True)

temp['candidateName'] = temp[1] + " " + temp[2] + " " + temp[3] + " " + temp[4] + " " + temp[0]

temp['candidateName'] = temp['candidateName'].str.replace('\s+', ' ',regex=True)
temp['candidateName'] = temp['candidateName'].str.strip()
temp['candidateName'] = temp['candidateName'].str.replace("\.", "",regex=True)

def cleanTempCand(x):
 
    if "JOSEPH R JR BIDEN" in x:
        return "JOSEPH R BIDEN JR"
    elif "ROBERT H JR MYERS" in x:
        return "ROBERT H MYERS JR"
    elif "JAMES A SR CANITZ" in x:
        return "JAMES A CANITZ SR"
    elif 'LA FUENTE ROCQUE "ROCKY" DE' in x:
        return 'ROCQUE "ROCKY" DE LA FUENTE'
    elif 'IMHOF NATASHA A VON' in x:
        return 'NATASHA VON IMHOF'
    else: 
        return x.upper() 
    
temp['candidateName'] = temp['candidateName'].apply(cleanTempCand)
df['candidate'] = temp['candidateName']

df.loc[(df['office'].str.contains('- [a-zA-Z]')), 'candidate'] = df['candidate'] + df['office']


def cleanCourtCand(x):

    if "YES" in x and '-' in x:
        # index = x.index(" -")
        # x = 'YES' + x[index+2:-2].upper()
        return x.split(' - ')[-1].strip('""').upper() + ' - YES'
    elif 'NO' in x and '-' in x: 
        # index = x.index(" -")
        # x = 'NO' + x[index+2:-2].upper()
        return x.split(' - ')[-1].strip('""').upper() + ' - NO'
    else: 
        return x
    # return x

df['candidate'] = df['candidate'].apply(cleanCourtCand)

df.loc[df['candidate'].str.contains('GAVIN S CHRISTIANSEN'), 'party_simplified'] = 'LIBERTARIAN'
df.loc[df['candidate'].str.contains('GAVIN S CHRISTIANSEN'), 'party_detailed'] = 'LIBERTARIAN'
df.loc[df['candidate'].str.contains('SCOTT A KOHLHAAS'), 'party_simplified'] = 'LIBERTARIAN'
df.loc[df['candidate'].str.contains('SCOTT A KOHLHAAS'), 'party_detailed'] = 'LIBERTARIAN'
df.loc[df['candidate'].str.contains('WILLY KEPPEL'), 'party_detailed'] = "VETERAN'S PARTY"

df['district'] = df['precinct']
df.loc[df['office'].str.contains('House District'), 'district'] = df['office']
df.loc[df['office'].str.contains('Senate District'), 'district'] = df['office']
df.loc[df['office'].str.contains('Superior Court'), 'district'] = df['office']
df.loc[df['office'].str.contains('District Court'), 'district'] = df['office']

df.loc[df['office'].str.contains('Number of Precincts Reporting'), 'district'] = ''
df.loc[df['office'].str.contains('Number of Precincts'), 'district'] = ''
df.loc[df['office'].str.contains('Registered Voters'), 'district'] = ''
df.loc[df['office'].str.contains('Times Counted'), 'district'] = ''

def getDistrict(x):
    if '""' in x:
        x = x[:-2]
    if 'House District' in x: 
        x = x[-2:]
    if 'Senate District' in x:
        x = x[-1:]
    if 'Superior Court' in x or 'District Court' in x: 
        index = x.index('Court')
        x = x[index+6:index+9]
    if ' - ' in x and 'Court' not in x: 
        index = x.index("District ")
        return x[index+8:index+11]
    elif 'HD99 Fed Overseas Absentee' in x:
        return 'HD99 FED OVERSEAS ABSENTEE' 
    else: 
        return x
    return x
    
df['district'] = df['district'].apply(getDistrict)
df["district"]= df["district"].str.strip()
df["district"]= df["district"].astype(str) 
df.loc[df['district'].str.contains('HD99 FED OVERSEAS ABSENTEE'), 'district'] = ""

def padDistrict(x):
    if len(x) < 3: 
        if x not in ['B', 'D', 'F', 'H', 'J', 'L', 'M', 'N', 'P', 'R', 'T', '']:
            x = x.zfill(3)
            return x
        else:
            return(x)
    elif '-' in x: 
        return x[:6]
    else:
        return(x)
        
df['district'] = df['district'].apply(padDistrict)
df["district"]= df["district"].str.strip()

def cleanOffice(x):

    if '""' in x:
        x = x[:-2]
    if ('-' in x) and ('Ballot Measure' not in x):
        index = x.index(" -")
        x = x[:index]
    if "President" in x:
        return "US PRESIDENT"
    if "Senator" in x:
        return "US SENATE"
    if "Representative" in x:
        return "US HOUSE"
    if "Superior Court" in x:
        return "SUPERIOR COURT"
    if "District Court" in x:
        return "DISTRICT COURT"
    if "Senate District" in x: 
        return "STATE SENATE"
    if "House District" in x: 
        return "STATE HOUSE"
    else: 
        return x.upper() 
    return x.upper()
    
df['office'] = df['office'].apply(cleanOffice)

df.loc[df['office'].str.contains('US HOUSE'), 'district'] = "000"

df.loc[df['office'].str.contains('US PRESIDENT'), 'district'] = "STATEWIDE"
df.loc[df['office'].str.contains('US SENATE'), 'district'] = "STATEWIDE"
df.loc[df['office'].str.contains('BALLOT MEASURE NO.'), 'district'] = "STATEWIDE"
df.loc[df['office'].str.contains('SUPREME COURT'), 'district'] = "STATEWIDE"
df.loc[df['office'].str.contains('COURT OF APPEALS'), 'district'] = "STATEWIDE"

def getDataverse(x):
    
    if 'NUMBER' in x or 'REGISTERED VOTERS' in x or 'TIMES COUNTED' in x or 'RACE STATISTICS' in x:
        return ""
    if 'US PRESIDENT' in x:
        return 'PRESIDENT'
    if "US SENATE" in x:
        return 'SENATE'
    if "US HOUSE" in x:
        return 'HOUSE'
    if "DISTRICT COURT" in x:
        return "LOCAL"
    if x in ['STATE HOUSE', 'SUPREME COURT', 'COURT OF APPEALS', 'SUPERIOR COURT', 
             'BALLOT MEASURE NO. 1 - 19OGTX', 'BALLOT MEASURE NO. 2 - 19AKBE', 'STATE SENATE']:
        return 'STATE'
    else: 
        return "" 
    
df['dataverse'] = df['office'].apply(getDataverse)

df = df[df.office != 'RACE STATISTICS']

# Readme Check - No issues 
df["readme_check"] = "FALSE"

df['precinct'] = df['precinct'].str.upper()
# drop number of precincts reporting info (complete reporting in file)
df = df[~(df['office'].str.contains('NUMBER OF PRECINCTS|TIMES COUNTED'))].drop_duplicates().copy()

# Final step: Remove all trailing white space and put columns in correct order. 
df=df.applymap(lambda x: x.strip() if type(x)==str else x)

df=df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "county_name", "county_fips", "jurisdiction_name",
                      "jurisdiction_fips", "candidate", "district", "dataverse", "year", "stage", "state", "special", "writein", "state_po",
                      "state_fips", "state_cen", "state_ic", "date", "readme_check", "magnitude"]]



# df=df.set_index('precinct')


df.to_csv('2020-ak-precinct-general.csv',index=False, quoting=csv.QUOTE_NONNUMERIC)



