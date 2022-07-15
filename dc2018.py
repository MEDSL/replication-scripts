#!/usr/bin/env python
# coding: utf-8

# - Add columns {'date', 'county_fips', 'jurisdiction_fips', 'magnitude', 'readme_check'}.
# - Remove periods and commas from candidate names. Be careful of double initial candidates, make sure the names remain separated (e.g. D.L. HUMPHREY to D L HUMPHREY).
# - Replace parentheses surrounding nicknames with double quotation marks (e.g. JOYCE (CHESTNUT) ROBINSON-PAUL to JOYCE "CHESTNUT" ROBINSON-PAUL). Similarly for single quotation marks (e.g. DUSTIN 'DC' CANTER to DUSTIN "DC" CANTER).
# - Replace candidate name [WRITE-IN] with WRITEIN.
# - Remove the double space in candidate name RENEE L. BOWSER (so RENEE L BOWSER).
# - Investigate GORDON - ANDREW FLETCHER and JOYCE ROBINSON - PAUL and see if they are double names (in which case, you'd want to remove the spaces surrounding the -), or a coding error.

# In[1]:


import pandas as pd
import numpy as np
import os
import csv

df = pd.read_csv('2018-dc-precinct-autoadapted.csv')
df = df.fillna("")


# In[5]:


df


# In[3]:


df['date'] = '2018-11-06'
df['readme_check'] = 'FALSE'
df['magnitude'] = 1


# In[4]:


# After county name fix, append on fips codes
fips = pd.read_csv('../../../help-files/county-fips-codes.csv')

fips = fips.applymap(str)
fips['state'] = fips['state'].str.upper()

df=df.applymap(lambda x: x.strip() if type(x)==str else x)
df = pd.merge(df, fips, on = ['state','county_name'], 
             how = 'left')


# In[6]:


df['jurisdiction_fips'] = df['county_fips']


# In[9]:


df['candidate'] = df['candidate'].str.replace(".", " ",regex=True)
df['candidate'] = df['candidate'].str.replace(",", " ",regex=True)
df['candidate'] = df['candidate'].str.replace(')', '"',regex=True)
df['candidate'] = df['candidate'].str.replace('(', '"',regex=True)
df['candidate'] = df['candidate'].str.replace("' ", '" ',regex=True)
df['candidate'] = df['candidate'].str.replace(" '", ' "',regex=True)
df['candidate'] = df['candidate'].str.replace('\s+', ' ',regex=True)


# In[10]:


df['candidate'] = df['candidate'].replace({'[WRITE-IN]': 'WRITEIN', 
                                           'JOYCE ROBINSON - PAUL': 'JOYCE ROBINSON-PAUL', 
                                           'GORDON - ANDREW FLETCHER': 'GORDON-ANDREW FLETCHER',
                                           '"TERRY" TERESA STITH':'TERESA "TERRY" STITH'})

### DC fixes ##################################################################

# district fixes
df['district'] = df['district'].replace(['WARD 6','WARD 1','WARD 3','WARD 5'],
	['006','001','003','005'])

# dataverse fixes
df.loc[df['office'] == 'US HOUSE','dataverse'] = 'HOUSE'
df.loc[df['dataverse'] == 'HOUSE','district'] = '000'
df.loc[df['office'] == 'US SENATE','dataverse'] = 'SENATE'
df.loc[df['office'] == 'BALLOTS CAST','dataverse'] = ''
# mag
df.loc[df['office'] == 'BALLOTS CAST','magnitude'] = 0
#party 
df.loc[df['party_detailed']=='NON-PARTISAN','party_detailed'] = 'NONPARTISAN'
df.loc[df['party_detailed']=='NONPARTISAN','party_simplified'] = 'NONPARTISAN'
# bools
df = df.replace([True,False],['TRUE','FALSE'])

df.loc[df['office'].isin(['MAYOR', 'CHAIRMAN OF THE DC COUNCIL',
       'ATTORNEY GENERAL', 'US SENATE']),'district'] = 'STATEWIDE'

#################################################################################

# Final step: Remove all trailing white space and put columns in correct order. 
df=df.applymap(lambda x: x.strip() if type(x)==str else x)

df=df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "county_name", "county_fips", "jurisdiction_name",
                      "jurisdiction_fips", "candidate", "district", "dataverse", "year", "stage", "state", "special", "writein", "state_po",
                      "state_fips", "state_cen", "state_ic", "date", "readme_check", "magnitude"]]

df.to_csv('2018-dc-precinct-general-updated.csv',quoting=csv.QUOTE_NONNUMERIC,index=False)

