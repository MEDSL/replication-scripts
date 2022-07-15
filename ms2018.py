#!/usr/bin/env python
# coding: utf-8

# - 2018 issue is still open. Resolve issues there first.
# - ~Add column {'magnitude'}.~
# - ~Several candidates appear as running with similar names (e.g. JEFFERY HARNESS and JEFFREY HARNESS). Investigate such instances, and if they correspond to the same candidate name and are not writeins, unify the candidate names.~
# - ~Unify the format of the names for judicial court races (e.g. CHANCERY COURT vs. JUSTICE COURT JUDGE).~
# - Redo the district column so it follows the current rules.
# - ~Investigate office name COAHOMA COAHOMA COUNTY JUDGE and decide whether COAHOMA should appear once or twice.~
# - Investigate candidate MERLE MCANALLY, who appears in some rows as running with party INDEPENDENT and others as NONPARTISAN. Decide whether the parties are correct, and if not, fix them.

# In[37]:


import pandas as pd
import numpy as np
import os
import csv

df = pd.read_csv('2018-ms-precinct-autoadapted.csv')
df = df.drop_duplicates()
df = df.fillna("")


# In[38]:


df['magnitude'] = 1


# In[39]:


df['party_detailed'] = df['party_detailed'].replace({'""': ''})
def get_party_simplified(x):
    if x in ["",'DEMOCRAT','REPUBLICAN',"LIBERTARIAN",'NONPARTISAN']:
        return x
    else:
        return "OTHER"
df['party_simplified'] = df['party_detailed'].apply(get_party_simplified)

# In[40]:


df['candidate'] = df['candidate'].replace({'CARNELLA FONDREN': 'CARNELIA FONDREN', 
                                          'D NEILL HARRIS SR': 'D NEIL HARRIS SR',
                                          'GERALD W CHATMAN SR': 'GERALD W CHATHAM SR',
                                          'JEFFREY HARNESS': 'JEFFERY HARNESS', 
                                          'PAULA DRUNGHOLE ELLIS': 'PAULA DRUNGOLE ELLIS',
                                          'ELIZABETHBETSYPERSON': 'ELIZABETH "BETSY" PERSON',
                                          'CARLOYN STEELE JOHNSON':'CAROLYN STEELE JOHNSON',
                                          'FOR THE BOND ISSUE':'YES',
                                          'AGAINST THE BOND ISSUE':'NO'})


# In[41]:


# wrong party listed for this candidate

df.loc[df['candidate'].str.contains("JEFFERY HARNESS"), 'party_detailed'] = 'DEMOCRAT'
df.loc[df['candidate'].str.contains("JEFFERY HARNESS"), 'party_simplified'] = 'DEMOCRAT'


# In[42]:


df['office'] = df['office'].replace({'COUNTY COURT JUDGE': 'COUNTY COURT', 
                                          'COAHOMA COUNTY JUDGE': 'COAHOMA COAHOMA COUNTY',
                                          'COUNTY YOUTH COURT JUDGE': 'COUNTY YOUTH COURT',
                                          'JUSTICE COURT JUDGE': 'JUSTICE COURT', 
                                          'VOTE FOR ONE': 'BOND ISSUE'
                                          })


# In[43]:


df.loc[df['candidate'].str.contains("MERLE MCANALLY"), 'party_detailed'] = 'NONPARTISAN'
df.loc[df['candidate'].str.contains("MERLE MCANALLY"), 'party_simplified'] = 'NONPARTISAN'


# In[44]:


def cleanDistrict(x):
    if "DIST" in x:
        if len(x) > 5:
            if x[0] == '0':
                return '0' + x[5:].replace(" , ", ", ")
            if ',' not in x:
                return x.split(' ')[-1].zfill(3)
            else: 
                return '00' + x[5:].replace(" , ", ", ")
        else:
            if len(x) == 1:
                return '00' + x
            if len(x) == 2:
                return '0' + x
    if x == '""':
        return ''
    else:
        return x
        
df['district'] = df['district'].apply(cleanDistrict)


# In[45]:


def cleanDistrict2(x):
    if ',' in x:
        index = x.index(',')
        if index == 4:
            return x[1:]
        else: 
            return x
    else:
        return x
        
df['district'] = df['district'].apply(cleanDistrict2)


#DC
df.loc[df['office']=='CIRCUIT COURT','dataverse'] = 'STATE'
df = df.replace([True,False], ['TRUE','FALSE'])
df.loc[df['office']=='STATE HOUSE','special'] = 'TRUE'



# Final step: Remove all trailing white space and put columns in correct order. 
df=df.applymap(lambda x: x.strip() if type(x)==str else x)

df=df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "county_name", "county_fips", "jurisdiction_name",
                      "jurisdiction_fips", "candidate", "district", "dataverse", "year", "stage", "state", "special", "writein", "state_po",
                      "state_fips", "state_cen", "state_ic", "date", "readme_check", "magnitude"]]

df.to_csv('2018-ms-precinct-general-updated.csv', index=False,quoting=csv.QUOTE_NONNUMERIC)


# In[48]:


# for x in df['stage'].unique():
#     print(x)


# ### weird candidate names
# 
# FOR THE BOND ISSUE
# AGAINST THE BOND ISSUE
# 
# CARNELIA FONDREN
# CARNELLA FONDREN
# 
# D NEIL HARRIS SR
# D NEILL HARRIS SR
# 
# GERALD W CHATHAM SR
# GERALD W CHATMAN SR # may need to change district from DIST 2 , PLACE 4 to DIST 17 , PLACE 4
# 
# JEFFERY HARNESS
# JEFFREY HARNESS
# 
# PAULA DRUNGHOLE ELLIS
# PAULA DRUNGOLE ELLIS
# 
# ELIZABETHBETSYPERSON

# In[47]:


# get_ipython().system('jupyter nbconvert --to script mississippi_2021_updates.ipynb')

