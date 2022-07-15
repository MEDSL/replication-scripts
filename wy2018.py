#!/usr/bin/env python
# coding: utf-8

# - extra indentation for some rows in county_2018.csv for Wyoming data
# - Add columns {'magnitude', 'jurisdiction_fips', 'readme_check', 'date', 'county_fips'}.
# - Remove periods and commas from candidate names.
# - Investigate candidate "TRACI CIEPIELA*" having an asterisk in the name. (removed, withdrew from election)
# - Replace "[WRITE-IN]" with "WRITEIN" in the candidate column
# - Zero-pad numerical districts so they have length three.

# In[2]:


import pandas as pd
import numpy as np
import os
import csv

df = pd.read_csv('2018-wy-precinct-autoadapted.csv')



# After county name fix, append on fips codes
fips = pd.read_csv('../../../help-files/county-fips-codes.csv')

df = df.drop(['jurisdiction_name'], axis=1)
fips = fips.applymap(str)
df['county_name'] = df['county_name'].str.upper()
fips['state'] = fips['state'].str.upper()

df=df.applymap(lambda x: x.strip() if type(x)==str else x)
df = pd.merge(df, fips, on = ['state','county_name'], 
             how = 'left')


# In[5]:


df['jurisdiction_name'] = df['county_name']
df['jurisdiction_fips'] = df['county_fips']


# In[6]:


df['date'] = '2018-11-06'
df['readme_check'] = 'FALSE'
df['magnitude'] = 1


# In[7]:


df['candidate'] = df['candidate'].replace({'[WRITE-IN]': 'WRITEIN'})
df['candidate'] = df['candidate'].replace({'TRACI CIEPIELA*': 'TRACI CIEPIELA'})


# In[8]:


df['candidate'] = df['candidate'].str.replace("\.", "",regex=True)
df['candidate'] = df['candidate'].str.replace(",", "",regex=True)


def cleanDist(x):
    if len(x) < 4:
        return x.zfill(3)
    if x == 'FIRST JUDICIAL DISTRICT': return '001'
    if x == 'SECOND JUDICIAL DISTRICT': return '002'
    if x == 'THIRD JUDICIAL DISTRICT': return '003'
    if x == 'FOURTH JUDICIAL DISTRICT': return '004'
    if x == 'FIFTH JUDICIAL DISTRICT': return '005'
    if x == 'SIXTH JUDICIAL DISTRICT': return '006'
    if x == 'SEVENTH JUDICIAL DISTRICT': return '007'
    if x == 'EIGHTH JUDICIAL DISTRICT': return '008'
    if x == 'NINTH JUDICIAL DISTRICT': return '009' 
    else: 
        return x
    
df['district'] = df['district'].apply(cleanDist)
df.loc[df['office']=='DISTRICT COURT JUDGE','dataverse'] = 'STATE'

#### DC duplicate fix
# solve issue where overvotes/undervotes not linked to respective retention candidate
fix_over_under = []
for cand_name in df[df['office']=='CIRCUIT COURT JUDGE']['candidate']:
    if ' - ' in cand_name:
        save = cand_name.split(' - ')[0]
        fix_over_under = fix_over_under + [cand_name]
    if ' - ' not in cand_name:
        cand_name = save + ' - ' + cand_name
        fix_over_under = fix_over_under + [cand_name]
        
df.loc[df['office']=='CIRCUIT COURT JUDGE', 'candidate'] = fix_over_under

fix_over_under2 = []
for cand_name in df[df['office']=='DISTRICT COURT JUDGE']['candidate']:
    if ' - ' in cand_name:
        save = cand_name.split(' - ')[0]
        fix_over_under2 = fix_over_under2 + [cand_name]
    if ' - ' not in cand_name:
        cand_name = save + ' - ' + cand_name
        fix_over_under2 = fix_over_under2 + [cand_name]
        
df.loc[df['office']=='DISTRICT COURT JUDGE', 'candidate'] = fix_over_under2

# Final step: Remove all trailing white space and put columns in correct order. 
df=df.applymap(lambda x: x.strip() if type(x)==str else x)

df = df.replace([True,False], ['TRUE','FALSE'])

df=df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "county_name", "county_fips", "jurisdiction_name",
                      "jurisdiction_fips", "candidate", "district", "dataverse", "year", "stage", "state", "special", "writein", "state_po",
                      "state_fips", "state_cen", "state_ic", "date", "readme_check", "magnitude"]]


df.to_csv('2018-wy-precinct-general-updated.csv', index=False, quoting=csv.QUOTE_NONNUMERIC)

