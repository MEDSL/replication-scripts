#!/usr/bin/env python
# coding: utf-8

# - ~Add columns {'county_fips', 'date', 'county_name', 'readme_check', 'magnitude', 'jurisdiction_fips'}.~
# - ~Remove periods from candidate names.~
# - ~Recode judicial retention races so they follow the new format.~
# - ~Zero-pad numerical districts so they have length three.~
# - ~Verify whether candidate CHRIS KENNEDY actually ran for both STATE HOUSE and STATE SENATE.~ two chris kennedys 
# - ~Replace candidate names YES VOTES and NO VOTES with YES and NO respectively.~
# - Remove named writein candidate rows wherever they are shown as having 0 votes and here appropriate.

# In[1]:


import pandas as pd
import numpy as np
import os
import csv

df = pd.read_csv('2018-co-precinct-autoadapted.csv')
df = df.replace(np.nan, '', regex = True)


# In[2]:


df


# In[3]:


df['date'] = '2018-11-06'
df['readme_check'] = 'FALSE'
df['magnitude'] = 1


# In[4]:


# After county name fix, append on fips codes
fips = pd.read_csv('../../help-files/county-fips-codes.csv')

fips = fips.applymap(str)
fips['state'] = fips['state'].str.upper()
df['county_name'] = df['jurisdiction_name']

df=df.applymap(lambda x: x.strip() if type(x)==str else x)
df = pd.merge(df, fips, on = ['state','county_name'], 
             how = 'left')


# In[5]:

df['county_fips'] = df['county_fips'].str.zfill(5)
df['jurisdiction_fips'] = df['county_fips']


# In[6]:


df['candidate'] = df['candidate'].str.replace("- NO VOTES", "- NO", regex=True)
df['candidate'] = df['candidate'].str.replace("- YES VOTES", "- YES", regex=True)
df['candidate'] = df['candidate'].str.replace(".", " ", regex=True)

# In[7]:


df['candidate'] = df['candidate'].str.replace('\s+', ' ', regex=True)
df['candidate'] = df['candidate'].replace('MARGARET (PEGGY) A CATLIN','MARGARET "PEGGY" A CATLIN')


# In[8]:


def cleanDist(x):
    if x == 'STATEWIDE' or x == 'C' or x == 'L' or x == 'N' or x == 'B' or x == 'K' or x == 'O' or x == 'J':
        return x
    elif len(x) < 4:
        return x.zfill(3)
    else: 
        return x
    
df['district'] = df['district'].apply(cleanDist)


# In[9]:


df['district'] = df['district'].replace({'000': ''})


# In[10]:


df['candidate'] = df['candidate'].replace({'NO VOTES': 'NO'})
df['candidate'] = df['candidate'].replace({'YES VOTES': 'YES'})


# DC
df.loc[df['office'] == 'DISTRICT COURT', 'dataverse'] = "STATE"
df.loc[(df['office']=='REGENT OF THE UNIVERSITY OF COLORADO')&
  (df['district']==''), 'district'] = 'AT-LARGE'
df = df.replace([True,False], ['TRUE','FALSE'])
df = df[~((df['writein']=='TRUE')&(df['votes']==0))]

#Readme Check - Setting as FALSE for now 
df["readme_check"] = "FALSE"

# Final step: Remove all trailing white space and put columns in correct order. 
df=df.applymap(lambda x: x.strip() if type(x)==str else x)

df=df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "county_name", "county_fips", "jurisdiction_name",
                      "jurisdiction_fips", "candidate", "district", "dataverse", "year", "stage", "state", "special", "writein", "state_po",
                      "state_fips", "state_cen", "state_ic", "date", "readme_check", "magnitude"]]

df = df.fillna("")

df.to_csv('2018-co-precinct-general-updated.csv', quoting=csv.QUOTE_NONNUMERIC,index=False)


# In[75]:


#df = df.loc[~((df['writein'] == False) & (df['votes'] != 0))]

