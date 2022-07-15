#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 11:29:04 2021

@author: jennifermiranda
"""

import pandas as pd
import numpy as np
import csv


df = pd.read_csv('2020 November General.csv', delimiter=",")

df = df.replace(np.nan, '', regex = True)

# Creating formatted 'candidate' column from name columns and removing whitespace:
df['candidate'] = df["FirstName"] + " " + df["MiddleName"] + " " + df["LastName"] + " " + df["Suffix"]
df['candidate'] = df['candidate'].str.replace('[^\w\s]','',regex=True)
df['candidate'] = df['candidate'].str.upper()
df['candidate'] = df['candidate'].str.replace('WRITE IN VOTES', 'WRITEIN')
df['candidate'] = df['candidate'].str.replace('\s+', ' ',regex=True)


# Make column for write in votes: 
df['writein'] = df["LastName"].str.contains('write in votes', case=False)  

# Drop unnecessary columns:
df = df.drop(['FirstName', 'MiddleName', 'LastName', 'WriteInVote', 
              'Suffix', 'ElectionName', 'DistrictType'], axis=1)
df = df.drop(['CandidateUid', 'LocalityUid', 'PrecinctUid', 'OfficeUid',
              'ElectionUid', 'DistrictUid', 'LocalityCode'], axis=1)

# Rename columns and fix format of variables: 
df = df.rename(columns={"PrecinctName": "precinct", "OfficeTitle": "office",
                        "Party": "party_detailed", "TOTAL_VOTES": "votes", 
                        "LocalityName": "county_name", "ElectionType": "stage",
                        "ElectionDate": "date"})

# Adding 'date', 'stage', 'year', 'party_detailed' columns
df['date'] = '2020-11-03'
df['stage'] = 'GEN'
df['year'] = '2020'
df['party_detailed'] = df['party_detailed'].str.upper() 

# 'special' column
df["special"] = df["office"].str.contains('Special')  
df['special'] = df['special'].apply(str)
df['special'] = df['special'].str.upper()

# 'votes' columns; int to str
df['votes'] = df['votes'].replace({'' : 0})
df["votes"] = df["votes"].apply(np.int64)
df["votes"] = df["votes"].apply(str)

# 'writein' column
df['writein'] = df['writein'].apply(str)
df['writein'] = df['writein'].str.upper()

# 'mode' column; extracting mode from precinct column
df['mode'] = 'ELECTION DAY' 
df.loc[df['precinct'].str.contains('Central Absentee Precinct'), 'mode'] = 'ABSENTEE'
df.loc[df['precinct'].str.contains('Provisional'), 'mode'] = 'PROVISIONAL'


def get_office(x):
    """
    Extract the office name from the range name.

    Parameters
    ---------
    x: str
      "office" in the VA data

    Returns
    -------
    office: str,
      The name of the office extracted from the race name
    """
    if "United States Senate" in x:
        return "US SENATE"
    elif "President" in x:
        return "US PRESIDENT"
    elif "House of Representatives" in x:
        return "US HOUSE"
    elif "Mayor" in x:
        return "MAYOR"
    # elif "Town Council" in x:
    #     return "TOWN COUNCIL"
    # elif "Member City Council" in x: 
    #     return "CITY COUNCIL"
    # elif "School Board" in x:
    #     return "SCHOOL BOARD"
    elif "Member House of Delegates" in x:
        return "STATE HOUSE"
    # elif "Board of Supervisors" in x:
    #     return "BOARD OF SUPERVISORS"
    # elif "County Board" in x:
    #     return "COUNTY BOARD"
    else:
        return x.upper()
    
df['office'] = df['office'].apply(get_office).str.upper()

df['party_detailed'] = df['party_detailed'].replace({"DEMOCRATIC" : "DEMOCRAT",
                                                      "WRITE-IN": "WRITEIN"})
df['party_simplified'] = df['party_detailed'].replace({"DEMOCRATIC" : "DEMOCRAT",
                                                      "WRITE-IN": "WRITEIN"})   

df.loc[df['office'].str.contains('COUNCIL'), 'party_detailed'] = 'NONPARTISAN'
df.loc[df['office'].str.contains('COUNCIL'), 'party_simplified'] = 'NONPARTISAN'

df.loc[df['office'].str.contains('MAYOR'), 'party_detailed'] = 'NONPARTISAN'
df.loc[df['office'].str.contains('MAYOR'), 'party_simplified'] = 'NONPARTISAN'

df.loc[df['office'].str.contains('BOARD'), 'party_detailed'] = 'NONPARTISAN'
df.loc[df['office'].str.contains('BOARD'), 'party_simplified'] = 'NONPARTISAN'

df.loc[df['office'].str.contains('ATTORNEY'), 'party_detailed'] = 'NONPARTISAN'
df.loc[df['office'].str.contains('ATTORNEY'), 'party_simplified'] = 'NONPARTISAN'

df.loc[df['office'].str.contains('CLERK OF COURT'), 'party_detailed'] = 'NONPARTISAN'
df.loc[df['office'].str.contains('CLERK OF COURT'), 'party_simplified'] = 'NONPARTISAN'
    

def get_party_simp(x):
    """
    Extract the simplified party name from the range name.

    Parameters
    ---------
    x: str
      "party_detailed" in the data

    Returns
    -------
    office: str,
      The name of the simplified party from the race name
    """
    if "DEMOCRAT" in x or "REPUBLICAN" in x or "LIBERTARIAN" in x or "NONPARTISAN" in x or "WRITEIN" in x:
        return x
    if "" == x:
        return x
    else:
        return "OTHER"
    
df['party_simplified'] = df['party_simplified'].apply(get_party_simp)

df["county_name"] = df['county_name'].str.replace('COUNTY', '')  
 
def get_district(x):
    if 'DISTRICT' in x:
        x = x.replace("DISTRICT", "").strip()
        x = x.zfill(3)
    elif '' == x:
        return x
    else:
        x = x.zfill(3) 
    return x.upper()
    
df['DistrictName'] = df['DistrictName'].apply(str)
df['district'] = df['DistrictName'].apply(get_district)
df = df.drop(['DistrictName'], axis=1)

# Use merge_on_statecodes.csv to get info for VA: 

df["state"] = 'VIRGINIA'
df["state_po"] = 'VA'
df["state_fips"] = '51'
df["state_cen"] = '54'
df["state_ic"] = '40'

# Make fips columns:
# After county name fix, append on fips codes
df["county_name"] = df['county_name'].str.replace('KING & QUEEN','KING AND QUEEN')

fips = pd.read_csv('../../help-files/county-fips-codes.csv')
fips['state'] = fips['state'].str.upper()
fips = fips.applymap(str)
df=df.applymap(lambda x: x.strip() if type(x)==str else x) 
df = pd.merge(df, fips, on = ['state','county_name'], 
             how = 'left')

  
df['jurisdiction_name'] = df['county_name']
df['jurisdiction_fips'] = df['county_fips']

# Adding 'special' election for STATE HOUSE election in 2020
df.loc[(df['office'] == 'STATE HOUSE') & (df['district'] == '029'), 'special'] = 'TRUE'

def get_dataverse(x):
    if 'PRESIDENT' in x:
        return 'PRESIDENT'
    elif "US SENATE" in x:
        return "SENATE"
    elif "US HOUSE" in x:
        return "HOUSE"
    elif x in ["STATE SENATE", "STATE HOUSE", "STATE SENATOR", "GOVERNOR",
               "SECRETARY OF STATE", "ATTORNEY GENERAL",
               "AUDITOR", "SUPERINTENDENT OF PUBLIC INSTRUCTION",
               "COMMISSIONER OF AGRICULTURE", "COMMISSIONER OF LABOR",
               "COMMISSIONER OF INSURANCE", "SUPREME COURT ASSOCIATE JUSTICE",
               "SUPREME COURT CHIEF JUSTICE", "SUPERIOR COURT"]: 
        return "STATE"
    else: # all others are local
        return "LOCAL"
    
df['dataverse'] = df['office'].apply(get_dataverse)

# Readme Check - No issues 
df["readme_check"] = "FALSE"
    
df['magnitude'] = 1
# Final step: Remove all trailing white space and put columns in correct order. 
df=df.applymap(lambda x: x.strip() if type(x)==str else x)

df=df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "county_name", "county_fips", "jurisdiction_name",
                      "jurisdiction_fips", "candidate", "district", "dataverse", "year", "stage", "state", "special", "writein", "state_po",
                      "state_fips", "state_cen", "state_ic", "date", "readme_check","magnitude"]]

official_dtypes = {'district':str,'precinct':str,'office':str, 'party_detailed':str,
                   'party_simplified':str,'mode':str,'votes':int, 'county_name':str, 'county_fips':str,
                   'jurisdiction_name':str,'jurisdiction_fips':str, 'candidate':str, 'district':str,
                   'dataverse':str,'year':int, 'stage':str, 'state':str, 'special':str, 'writein':str,
                   'state_po':str, 'state_fips':str, 'state_cen':str, 'state_ic':str, 'date':str,
                   'readme_check':str,'magnitude':int}
df = df.fillna("").astype(official_dtypes)
# removing a couple near duplicates with 0 votes
df=df[~(df.drop(columns = 'votes').duplicated(keep = False) & (df['votes']==0))].copy()
df['precinct'] = df['precinct'].str.upper()

df.to_csv('2020-va-precinct-general.csv',quoting=csv.QUOTE_NONNUMERIC, index=False)


