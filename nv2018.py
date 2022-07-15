#!/usr/bin/env python
# coding: utf-8

# - ~Add columns {'jurisdiction_fips', 'magnitude', 'date', 'county_fips', 'readme_check'}.~
# - ~Investigate candidates where suffixes seem to appear in the middle of the name (e.g. HARRY L. SR. DIMITROFF) and see whether this is intended or should be moved to the end of the name~
# - ~Remove periods from candidate names.~
# - ~Find the name of candidate "TICK" SEGERBLOM and add it.~
# - ~Remove extra spaces in ISMAEL "IZZY" GUTIERREZ~
# - ~Move district information in the office column to district.~
# - ~Zero-pad numerical districts so they have length three.~
# - ~Unify office names such as SCHOOL BOARD OF TRUSTEES, SCHOOL BOARD TRUSTEE, etc. (non-exhaustive list).~
# - ~Investigate what offices SP - 1 and WC - 1 stand for, and change the final data to reflect those full names.~
# - ~Remove named writein candidates wherever they appear as having received 0 votes.~

# In[1]:


import pandas as pd
import numpy as np
import os
import csv

official_dtypes = {'precinct':str,'office':str, 'party_detailed':str, 
'party_simplified':str,'mode':str,'votes':int, 'county_name':str, 
'county_fips':str, 'jurisdiction_name':str,'jurisdiction_fips':str, 'candidate':str, 
'district':str, 'dataverse':str,'year':int, 'stage':str, 'state':str, 'special':str, 
'writein':str, 'state_po':str, 'state_fips':str, 'state_cen':str, 'state_ic':str, 
'date':str, 'readme_check':str,'magnitude':int}
df = pd.read_csv('2018-nv-precinct-autoadapted.csv', dtype = official_dtypes)
df = df.fillna("")


# In[2]:


pd.set_option('display.max_columns', None)


# In[3]:


df['date'] = '2018-11-06'
df['readme_check'] = 'FALSE'
df['magnitude'] = 1


# In[4]:


# After county name fix, append on fips codes
fips = pd.read_csv('../../help-files/county-fips-codes.csv')

fips = fips.applymap(str)
fips['state'] = fips['state'].str.upper()

df=df.applymap(lambda x: x.strip() if type(x)==str else x)
df = pd.merge(df, fips, on = ['state','county_name'], 
             how = 'left')


# In[5]:


df['jurisdiction_fips'] = df['county_fips']


# In[6]:


df['candidate'] = df['candidate'].str.replace("\.", "",regex=True)
df['candidate'] = df['candidate'].str.replace('\s+', ' ',regex=True)


# In[7]:


df['candidate'] = df['candidate'].replace({'RICHARD SR KOONTZ': 'RICHARD KOONTZ SR',
                                           'HARRY L SR DIMITROFF': 'HARRY L DIMITROFF SR',
                                           '"TICK" SEGERBLOM': 'RICHARD "TICK" SEGERBLOM',
                                          'GENNADY II STOLYAROV': 'GENNADY STOLYAROV II'})


# In[8]:


def district(x):
    if x == '""':
        return ""
    if x == "1-2-5":
        return "125"
    for i in ['F', 'C', 'G', 'D', 'E', 'A', 'B', 'V', 'IV', 'III']:
        if x == i:
            return x
        
    else:
        return x.zfill(3)
df['district'] = df['district'].apply(district)


# In[9]:


df['office'] = df['office'].replace({"SCHOOL BOARD TRUSTEE AT-LARGE": "SCHOOL BOARD TRUSTEE",
                                     "BOARD OF SCHOOL TRUSTEES": "SCHOOL BOARD TRUSTEE",
                                     "SCHOOL BOARD OF TRUSTEES": "SCHOOL BOARD TRUSTEE",
                                     "SCHOOL DISTRICT BOARD OF TRUSTEES": "SCHOOL BOARD TRUSTEE",
                                     "SCHOOL DISTRICT BOARD TRUSTEE, SEAT F": "SCHOOL BOARD TRUSTEE, SEAT F"})


# In[10]:


df.loc[df.office.str.contains("SCHOOL BOARD TRUSTEE, DISTRICT E"), "district"] = 'E'
df.loc[df.office.str.contains("SCHOOL BOARD TRUSTEE, DISTRICT C"), "district"] = 'C'
df.loc[df.office.str.contains("SCHOOL BOARD TRUSTEE, DISTRICT B"), "district"] = 'B'
df.loc[df.office.str.contains("SCHOOL BOARD TRUSTEE, DISTRICT F AT-LARGE"), "district"] = 'F'
df.loc[df.office.str.contains("WHITE PINE TV DISTRICT NO. 1, SEAT B"), "district"] = '001, SEAT B'


# In[11]:


df['office'] = df['office'].replace({"WHITE PINE TV DISTRICT NO. 1, SEAT B":"WHITE PINE TV DISTRICT",
                                    "SCHOOL BOARD TRUSTEE, DISTRICT E": "SCHOOL BOARD TRUSTEE",
                                    "SCHOOL BOARD TRUSTEE, DISTRICT C": "SCHOOL BOARD TRUSTEE",
                                    "SCHOOL BOARD TRUSTEE, DISTRICT B": "SCHOOL BOARD TRUSTEE",
                                    "SCHOOL BOARD TRUSTEE, DISTRICT F AT-LARGE": "SCHOOL BOARD TRUSTEE AT-LARGE",
                                    'LYON COUNTY SCHOOL DISTRICT TRUSTEES, DISTRICT 4 - SILVER SPRINGS/STAGECOACH': 'LYON COUNTY SCHOOL DISTRICT TRUSTEES',
                                    "LINCOLN COUNTY SCHOOL DISTRICT TRUSTEE, DISTRICT B": "LINCOLN COUNTY SCHOOL DISTRICT TRUSTEE",
                                    "SCHOOL BOARD OF TRUSTEES, DISTRICT 6": "SCHOOL BOARD OF TRUSTEES",
                                    "SCHOOL BOARD OF TRUSTEES, DISTRICT 1": "SCHOOL BOARD OF TRUSTEES", 
                                    "TRUSTEE, CLARK COUNTY SCHOOL DISTRICT G": "TRUSTEE, CLARK COUNTY SCHOOL DISTRICT",
                                    "TRUSTEE, CLARK COUNTY SCHOOL DISTRICT D": "TRUSTEE, CLARK COUNTY SCHOOL DISTRICT",
                                    "TRUSTEE, CLARK COUNTY SCHOOL DISTRICT F": "TRUSTEE, CLARK COUNTY SCHOOL DISTRICT"

})


# In[12]:


df = df.loc[~((df['writein'].str.contains('TRUE')) & (df['votes']==0))]


##### DC Fixes ############
df.loc[df['office']=='DISTRICT COURT JUDGE', 'dataverse'] = "STATE"

def fix_district(x):
    if x == 'III': return '003'
    if x == 'IV': return '004'
    if x == 'V': return '005'
    if (len(x) == 3) or (x in ['STATEWIDE','A','B','C','D','E','F','G']): 
        return x
    if 'DEPT' in x:
        return x[0].zfill(3) + ',' + x.split(',')[-1]
    else: return x
df['district'] = df['district'].apply(fix_district)


# Final step: Remove all trailing white space and put columns in correct order. 
df=df.applymap(lambda x: x.strip() if type(x)==str else x)

# drop corrupted local offices that dont appear in official results, cleared with JCuriel, https://www.nvsos.gov/silverstate2018gen/county-results/washoe.shtml
df = df[~(df['office'].isin(['WC - 1', 'SP - 1']))].copy()

df=df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "county_name", "county_fips", "jurisdiction_name",
                      "jurisdiction_fips", "candidate", "district", "dataverse", "year", "stage", "state", "special", "writein", "state_po",
                      "state_fips", "state_cen", "state_ic", "date", "readme_check", "magnitude"]]

#df = df.replace([True,False], ['TRUE','FALSE'])

df.to_csv('2018-nv-precinct-general-updated.csv',quoting=csv.QUOTE_NONNUMERIC, index=False)

