#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 22:26:29 2021

@author: jennifermiranda
"""

import pandas as pd
import numpy as np
import csv
import unidecode


df = pd.read_csv('November_3_2020_General_Election_Certified_Results.csv', delimiter=",")
df = df.replace(np.nan, "", regex = True)

df = df.rename(columns={"PrecinctNumber": "precinct", "ContestName": "office", 
                        "Party": "party_detailed", "Votes": "votes", 
                        "Candidate": "candidate", "ElectionName": "stage",
                        "ElectionDate": "date"})

df["votes"] = df["votes"].apply(str)
df["stage"] = "GEN"
df["date"] = "2020-11-03"
df["year"] = "2020"
df["mode"] = "TOTAL"
df['special'] = 'FALSE'

df["precinct"]= df["precinct"].astype(str) 
df["precinct"]= df["precinct"].str.zfill(3) 

df["writein"] = df["candidate"].str.contains('Write-in')  

df['writein'] = df['writein'].apply(str)
df['writein'] = df['writein'].str.upper()

df['district'] = ""
df = df.drop(['ContestNumber'], axis=1)

# Use merge_on_statecodes.csv to get info for DC: 

df["state"] = 'DISTRICT OF COLUMBIA'
df["state_po"] = 'DC'
df["state_fips"] = '11'
df["state_cen"] = '53'
df["state_ic"] = '55'

df['candidate'] = df['candidate'].str.replace('Gordon-Andrew "The People\'s Champion"',
  'Gordon-Andrew "The people\'s champion" Fletcher').replace('"Steptoe"- Carolyn C.',
  'Carolyn C Steptoe').replace('Nate Brown "Mw6"',
  'Nate "MW6" Brown').replace("Eboni - Rose Thompson", 
  "Eboni-Rose Thompson").replace('Trupti "Trip" J. Patel','Trupti J "Trip" Patel')
                                    
def cleanCandidate(x):
    """
    Extract clean candidate name from candidate column.
    
     Parameters
    ---------
    x: str
      "candidate" in the DC data

    Returns
    -------
    candidate: str,
      The formatted name of the candidate. 
    """
    accentedCand = ['Claudia Barragán', 'Jeanné Lewis', 'Mónica Palacio', 
                    'Martín Miguel Fernandez', 'Renée L. Bowser', 'R. Andrè Speaks']
    
    if ("LIB" in x or "STG" in x or 
    "DEM" in x or "IND" in x or 
    "REP" in x or "SWP" in x):
        x = x[4:]
        if " - " in x:
            index = x.index("- ")
            x = x[:index].upper()
    if "(" in x or ")" in x:
        x = x.replace("(", "").replace(")", "")
    if x in accentedCand: 
        x = unidecode.unidecode(x)
    if "." in x or "," in x:
        x = x.replace(".", "").replace(",", "")
    if "Write-in" in x:
        x = "WRITEIN"
    if ("Moshe 'Mo' Pasternak" in x or "Carolyn C" in x 
    or "Nate 'Ward 8' Derenge" in x or "Shekita 'Ki-Ki' McBroom" in x):
        x = x.replace("'", '"').replace('"-', '"')
    if "Robin Ward 8 McKinney" in x:
        x = 'Robin "Ward 8" McKinney'
    if len(x) < 1:
        x = ""
    else: 
        return x.upper() 
    return x.upper()

df['candidate'] = df['candidate'].apply(cleanCandidate)
df['candidate'] = df['candidate'].str.replace('\s+', ' ', regex=True)

df['county_name'] = 'DISTRICT OF COLUMBIA'
df['county_fips'] = '11001'

df['jurisdiction_name'] = 'WARD ' + df['WardNumber'].apply(str)
df = df.drop(['WardNumber'], axis=1)
df['jurisdiction_fips'] = df['county_fips']

df.loc[df['office'].str.contains('-ANC'), 'precinct'] = df['precinct'] + df.office.str[-10:]

def cleanOffice(x):
    """
    Extract ANC from office name.
    
     Parameters
    ---------
    x: str
      "office" in the DC data

    Returns
    -------
    office: str,
      The clean name of the office. 
    """
    if "ANC" in x:
        return x[11:-11]
    if "PRESIDENT" in x:
        return "US PRESIDENT"
    if "SENATOR" in x:
        return "US SENATE"
    if "UNITED STATES REPRESENTATIVE" in x:
        return "US HOUSE"
    if "WARD" in x and "BOARD OF EDUCATION" in x:
        return "BOARD OF EDUCATION"
    if "AT-LARGE" in x and "BOARD OF EDUCATION" in x:
        return "AT LARGE - BOARD OF EDUCATION"
    if "AT-LARGE" in x and "COUNCIL" in x: 
        return "AT LARGE - MEMBER OF THE COUNCIL"
    if "WARD" in x and "COUNCIL" in x: 
        return "MEMBER OF THE COUNCIL"
    
    else: 
        return x.upper() 
    
df['office'] = df['office'].apply(cleanOffice)

def get_dataverse(x):
    if 'PRESIDENT' in x:
        return 'PRESIDENT'
    elif "DELEGATE" in x:
        return "HOUSE"
    elif "TOTAL" in x:
        return ""
    elif x in ["STATE SENATE", "STATE HOUSE", "STATE SENATOR", "GOVERNOR",
               "SECRETARY OF STATE", "ATTORNEY GENERAL",
               "AUDITOR", "SUPERINTENDENT OF PUBLIC INSTRUCTION",
               "COMMISSIONER OF AGRICULTURE", "COMMISSIONER OF LABOR",
               "COMMISSIONER OF INSURANCE", "SUPREME COURT ASSOCIATE JUSTICE",
               "SUPREME COURT CHIEF JUSTICE", "SUPERIOR COURT", "US SENATE",
               "US HOUSE", "AT LARGE - BOARD OF EDUCATION", "AT LARGE - MEMBER OF THE COUNCIL"]: 
        return "STATE"
    else: # all others are local
        return "LOCAL"
    
df['dataverse'] = df['office'].apply(get_dataverse)

df.loc[df['office'].str.contains('AT LARGE'), 'district'] = 'STATEWIDE'

df['party_detailed'] = df['party_detailed'].replace({"LIB": "LIBERTARIAN",
                                                    "STG": "STATEWIDE GREEN",
                                                    "DEM": "DEMOCRAT",
                                                    "IND": "INDEPENDENT",
                                                    "REP": "REPUBLICAN",
                                                    "NPN": "NONPARTISAN",
                                                    "SWP": "SOCIALIST WORKERS",
                                                    "CITYWIDE": ""})

df.loc[df['candidate'].str.contains('KATHY HENDERSON'), 'party_detailed'] = 'INDEPENDENT'

df['party_simplified'] = df['party_detailed']
df['party_simplified'] = df['party_simplified'].replace({"STATEWIDE GREEN": "OTHER",
                                                        "INDEPENDENT": "OTHER",
                                                        "SOCIALIST WORKERS": "OTHER"})

df.loc[df['candidate'].str.contains('WRITEIN'), 'party_simplified'] = 'OTHER'

df.loc[df['office'].str.contains('BOARD OF EDUCATION'), 'party_detailed'] = 'NONPARTISAN'
df.loc[df['office'].str.contains('BOARD OF EDUCATION'), 'party_simplified'] = 'NONPARTISAN'

df.loc[df['office'].str.contains('INITIATIVE MEASURE NO. 81'), 'party_detailed'] = ""
df.loc[df['office'].str.contains('INITIATIVE MEASURE NO. 81'), 'party_simplified'] = ""

df['magnitude'] = 1
df.loc[df.office == 'AT LARGE - MEMBER OF THE COUNCIL', 'magnitude'] = 2

# Readme Check - No issues 
df["readme_check"] = "FALSE"

# fix district for HOUSE datavers
df.loc[df['dataverse']=='HOUSE','district'] = '000'


# Final step: Remove all trailing white space and put columns in correct order. 
df=df.applymap(lambda x: x.strip() if type(x)==str else x)

df=df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "county_name", "county_fips", "jurisdiction_name",
                      "jurisdiction_fips", "candidate", "district", "dataverse", "year", "stage", "state", "special", "writein", "state_po",
                      "state_fips", "state_cen", "state_ic", "date", "readme_check", "magnitude"]]


df.to_csv('2020-dc-precinct-general.csv',index=False, quoting=csv.QUOTE_NONNUMERIC)







