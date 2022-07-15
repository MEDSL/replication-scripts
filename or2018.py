#!/usr/bin/env python
# coding: utf-8

# - ~Add columns {'magnitude', 'readme_check', 'jurisdiction_fips', 'county_fips', 'date'}.~
# - ~Remove periods from candidate names.~
# - ~Replace [WRITE-IN] with WRITEIN in the candidate column.~
# - Investigate similarly named candidates JARRED TAYLOR and JERRED TAYLOR, and decide whether they are the same candidate and not a writein mistake, and if so, unify their name. (CHECK W ELECTIONCLEANER)
# - Investigate empty office "" and decide what it stands for. == stands for total counts, unsure of which total they belong to, should i remove? 
# - ~Zero-pad numerical districts so they have length three.~
# - ~Replace candidate names OVER VOTES and UNDER VOTES with OVERVOTES and UNDERVOTES respectively.~
# - ~Several candidates appear running with multiple parties (e.g. GARY LYNDON DYE is CONSTITUTION and LIBERTARIAN). Investigate such instances and decide whether this is correct or whether the party information should be unified.~
# 

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
df = pd.read_csv('2018-or-precinct-autoadapted.csv', dtype = official_dtypes)
df = df.fillna("")


# In[2]:


pd.set_option('display.max_columns', None)


# In[3]:


df['date'] = '2018-11-06'
df['readme_check'] = 'FALSE'
df['magnitude'] = np.where(df['office'].str.contains('BALLOTS CAST'), 0 ,1)


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


df['candidate'] = df['candidate'].str.replace("\.", " ",regex=True)
df['candidate'] = df['candidate'].str.replace(",", "",regex=True)
df['candidate'] = df['candidate'].str.replace('\s+', ' ',regex=True)


# In[7]:


df['candidate'] = df['candidate'].replace({'OVER VOTES': 'OVERVOTES',
                                           'UNDER VOTES': 'UNDERVOTES',
                                           '[WRITE-IN]': 'WRITEIN',
                                           'JARRED TAYLOR': 'JERRED TAYLOR'
                                          })


# In[8]:


# Code to find candidates with multiple parties
'''for x in df['candidate'].unique():
    count = 0 
    lst = []
    temp = df.loc[df['candidate'] == x]
    for y in temp['party_detailed'].unique():
        count += 1
        lst.append(y)
    if count > 1:
        print(x)
        print(lst)'''


# In[9]:


df.loc[df['candidate'] == 'MARK R ROBERTS', 'party_detailed'] = 'INDEPENDENT PARTY OF OREGON'
df.loc[df['candidate'] == 'MARK R ROBERTS', 'party_simplified'] = 'OTHER'

df.loc[df['candidate'] == 'NICK CHEN', 'party_detailed'] = 'LIBERTARIAN'
df.loc[df['candidate'] == 'NICK CHEN', 'party_simplified'] = 'OTHER'

df.loc[df['candidate'] == 'PATRICK STARNES', 'party_detailed'] = 'DEMOCRAT'
df.loc[df['candidate'] == 'PATRICK STARNES', 'party_simplified'] = 'DEMOCRAT'

df.loc[df['candidate'] == 'RICHARD R JACOBSON', 'party_detailed'] = 'LIBERTARIAN'
df.loc[df['candidate'] == 'RICHARD R JACOBSON', 'party_simplified'] = 'OTHER'

df.loc[df['candidate'] == 'DAN SOUZA', 'party_detailed'] = 'LIBERTARIAN'
df.loc[df['candidate'] == 'DAN SOUZA', 'party_simplified'] = 'OTHER'

df.loc[df['candidate'] == 'MARK KARNOWSKI', 'party_detailed'] = 'LIBERTARIAN'
df.loc[df['candidate'] == 'MARK KARNOWSKI', 'party_simplified'] = 'OTHER'

df.loc[df['candidate'] == 'CYNTHIA HYATT', 'party_detailed'] = 'INDEPENDENT PARTY OF OREGON'
df.loc[df['candidate'] == 'CYNTHIA HYATT', 'party_simplified'] = 'OTHER'

df.loc[df['candidate'] == 'GARY LYNDON DYE', 'party_detailed'] = 'LIBERTARIAN'
df.loc[df['candidate'] == 'GARY LYNDON DYE', 'party_simplified'] = 'OTHER'

df.loc[df['candidate'] == 'MARC W KOLLER', 'party_detailed'] = 'INDEPENDENT PARTY OF OREGON'
df.loc[df['candidate'] == 'MARC W KOLLER', 'party_simplified'] = 'OTHER'

df.loc[df['candidate'] == 'KENNY SERNACH', 'party_detailed'] = 'LIBERTARIAN'
df.loc[df['candidate'] == 'KENNY SERNACH', 'party_simplified'] = 'OTHER'

df.loc[df['candidate'] == 'TIM E NELSON', 'party_detailed'] = 'LIBERTARIAN'
df.loc[df['candidate'] == 'TIM E NELSON', 'party_simplified'] = 'OTHER'

df.loc[df['candidate'] == 'BRIAN P HALVORSEN', 'party_detailed'] = 'INDEPENDENT PARTY OF OREGON'
df.loc[df['candidate'] == 'BRIAN P HALVORSEN', 'party_simplified'] = 'OTHER'

df.loc[df['candidate'] == 'FRANK L LENGELE JR ', 'party_detailed'] = 'LIBERTARIAN'
df.loc[df['candidate'] == 'FRANK L LENGELE JR ', 'party_simplified'] = 'OTHER'

df.loc[df['candidate'] == 'SKYE FARNAM', 'party_detailed'] = 'INDEPENDENT PARTY OF OREGON'
df.loc[df['candidate'] == 'SKYE FARNAM', 'party_simplified'] = 'OTHER'


# In[10]:


def district(x):
    if x == '':
        return '' 
    if x == 'STATEWIDE':
        return x
    else:
        return x.zfill(3)
df['district'] = df['district'].apply(district)

# drop total votes
df = df[~(df['office']=="")].copy()
# drop duplicates and double counting
df = df.drop_duplicates()
df = df[~(df['precinct'].isin(['CLACKAMAS OR', 'COOS OR', 'CROOK OR', 'GRANT OR', 'JOSEPHINE OR',
       'LANE OR', 'LINN OR', 'UNION OR']))].copy()

# In[11]:


# Final step: Remove all trailing white space and put columns in correct order. 
df=df.applymap(lambda x: x.strip() if type(x)==str else x)

df=df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "county_name", "county_fips", "jurisdiction_name",
                      "jurisdiction_fips", "candidate", "district", "dataverse", "year", "stage", "state", "special", "writein", "state_po",
                      "state_fips", "state_cen", "state_ic", "date", "readme_check", "magnitude"]]

df.to_csv('2018-or-precinct-general-updated.csv',quoting=csv.QUOTE_NONNUMERIC, index=False)



