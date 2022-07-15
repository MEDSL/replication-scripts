#!/usr/bin/env python
# coding: utf-8

# - Add columns {'county_fips', 'readme_check', 'jurisdiction_fips', 'date', 'magnitude'}.
# - Remove periods from candidate names. Be careful of double initial names, make sure they remain separated (e.g. ALAN J.K. YIM to ALAN J K YIM).
# - Replace parentheses surrounding nicknames with double quotation marks (e.g. REBECCA (SHUTE) VILLEGAS to REBECCA "SHUTE" VILLEGAS).
# - Unify the format of COUNCILMEMBER (EAST MAUI) (and similar) and COUNCILMEMBER, COUNTY OF HAWAII: either have parentheses or commas.
# - Replace MAUI RESIDENT TRUSTEE with RESIDENT TRUSTEE - MAUI or similar (similarly with OAHU RESIDENT TRUSTEE and AT-LARGE TRUSTEE if the latter represents a similar office).
# - Zero-pad numerical districts so they have length three.

# In[1]:


import pandas as pd
import numpy as np
import os
import csv

df = pd.read_csv('2018-hi-precinct-autoadapted.csv')
df = df.fillna("")


# In[5]:


df


# In[3]:


df['date'] = '2018-11-06'
df['readme_check'] = 'FALSE'
df['magnitude'] = np.where(df['office']=='AT-LARGE TRUSTEE', 3, 1)


# In[4]:


# After county name fix, append on fips codes
fips = pd.read_csv('../../help-files/county-fips-codes.csv')

fips = fips.applymap(str)
fips['state'] = fips['state'].str.upper()

df=df.applymap(lambda x: x.strip() if type(x)==str else x)
df = pd.merge(df, fips, on = ['state','county_name'], 
             how = 'left')


# In[6]:


df['jurisdiction_fips'] = df['county_fips']


# In[7]:


df['candidate'] = df['candidate'].str.replace(".", " ",regex=True)
df['candidate'] = df['candidate'].str.replace(')', '"',regex=True)
df['candidate'] = df['candidate'].str.replace('(', '"',regex=True)
df['candidate'] = df['candidate'].str.replace('\s+', ' ',regex=True)


# In[19]:


df['office'] = df['office'].replace({'COUNCILMEMBER, COUNTY OF HAWAII': 'COUNCILMEMBER (HAWAII)', 
                                           'COUNCILMEMBER, COUNTY OF KAUAI': 'COUNCILMEMBER (KAUAI)', 
                                           'COUNCILMEMBER, CITY AND COUNTY OF HONOLULU': 'COUNCILMEMBER (HONOLULU)', 
                                           'MAUI RESIDENT TRUSTEE': 'RESIDENT TRUSTEE - MAUI',
                                           'OAHU RESIDENT TRUSTEE': 'RESIDENT TRUSTEE - OAHU'
                                          })


# In[18]:


def cleanDistrict(x): 
  if x == "I": return '001'
  if x == "II": return '002'
  if x == "IV": return '004'
  if x == "VII": return '007'
  if ('I' not in x) and (x != ""): 
      return x.zfill(3)
  else: 
      return x
df['district'] = df['district'].apply(cleanDistrict)


# In[20]:
df = df.replace([True,False],['TRUE','FALSE'])

# Final step: Remove all trailing white space and put columns in correct order. 
df=df.applymap(lambda x: x.strip() if type(x)==str else x)

df=df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "county_name", "county_fips", "jurisdiction_name",
                      "jurisdiction_fips", "candidate", "district", "dataverse", "year", "stage", "state", "special", "writein", "state_po",
                      "state_fips", "state_cen", "state_ic", "date", "readme_check", "magnitude"]]

df.to_csv('2018-hi-precinct-general-updated.csv', index=False,quoting=csv.QUOTE_NONNUMERIC)

