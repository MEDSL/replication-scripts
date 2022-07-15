#!/usr/bin/env python
# coding: utf-8

# 1. Add columns {'jurisdiction_fips', 'readme_check', 'date', 'magnitude', 'county_fips'}.
# 2. Remove periods from candidate names.
# 3. Investigate extraneous spaces after dashes in these candidate names:
# *CAROL RIMEDIO - RIGHETTI
# *CASSANDRA COLLIER - WILLIAMS
# *MARY E. PIERCE- BROADWATER
# *SHARON BUCKLEY- MIRHAIDARI
# 4. Replace candidate name LON' CHERIE' D. BILLINGSLEY with LON D "CHERIE" BILLINGSLEY.
# 5. Move district information from judicial courts to the district column where appropriate (e.g. in "JUDGE OF THE COUNTY COURT - AREA 1 - TERM COMMENCING 01/02/2019`).
# 6. Zero-pad numerical districts so they have length three.
# 7. Change "TREASURER OF THE STATE" to "STATE TREASURER" in the office column.
# 8. Investigate candidates "JIM HUGHES" and "JOE MILLER", who appear in different rows with multiple party affiliations.

# In[1]:


import pandas as pd
import os
import numpy as np
import re
import warnings
import csv
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None  # default='warn'


# In[2]:


df = pd.read_csv("2018-oh-precinct-autoadapted.csv")

df = df.replace(np.nan, '', regex = True)
df=df.applymap(lambda x: x.strip().upper() if type(x)==str else x)


# In[3]:


df[df.office.str.contains('JUDGE OF THE COUNTY COURT')].party_detailed.unique()


# In[4]:


df.head(3)


# In[5]:


#MERGING COUNTY_FIPS
df['state'] = 'Ohio' #need it like this to merge; CHANGE LATER
countyFips = pd.read_csv("../..//help-files/county-fips-codes.csv")
#print(countyFips.head)
df = pd.merge(df, countyFips, on = ['state','county_name'],how = 'left')
df['county_fips'] = df['county_fips'].apply(str)
df['jurisdiction_fips'] = df['county_fips']
#now can change 'state' column  back to NC
df['state'] = df['state'].str.upper()


# In[6]:


df['magnitude'] = 1
df['readme_check'] = 'FALSE'
df['date'] = '2018-11-06' #check formatting


# candidate fixes
# 2. Remove periods from candidate names.
# 3. Investigate extraneous spaces after dashes in these candidate names:
# *CAROL RIMEDIO - RIGHETTI
# *CASSANDRA COLLIER - WILLIAMS
# *MARY E. PIERCE- BROADWATER
# *SHARON BUCKLEY- MIRHAIDARI
# 4. Replace candidate name LON' CHERIE' D. BILLINGSLEY with LON D "CHERIE" BILLINGSLEY.

# In[7]:


def fix_cand(x):
    x=x.replace('.','')
    if ' - ' in x: return x.replace(' - ','-')
    elif '- ' in x: return x.replace('- ','-')
    if x =="LON' CHERIE' D BILLINGSLEY": return 'LON D "CHERIE" BILLINGSLEY'
    return x

df['candidate'] = df['candidate'].apply(fix_cand)


# In[8]:


df[df.candidate.str.contains('RIGHETTI')].candidate.unique()


# fix courts & judge district info
# 5. Move district information from judicial courts to the district column where appropriate (e.g. in "JUDGE OF THE COUNTY COURT - AREA 1 - TERM COMMENCING 01/02/2019`).
# 

# In[9]:


l = list()
def fix_district(of, dist):
    dist = str(dist)
    if 'AREA' in of: return of[of.find('- ')+2:of.find('TERM')-3]
    elif 'DISTRICT' in of: return of.split()[6]  
    if dist.isnumeric(): return dist.zfill(3)
    return dist

def fix_office(x):
    if 'AREA' in x: return x[:x.find('-')] + x[x.find('- TE'):]
    elif 'DISTRICT' in x and 'JUDGE' in x: return x[:x.find('-')] + x[x.find('ICT')+4:]
    elif x == "TREASURER OF STATE": return "STATE TREASURER"
    return x

df['district'] = df.apply(lambda x: fix_district(x['office'],x['district']),axis=1)
#now remove that district info from the office names 
df['office'] = df['office'].apply(fix_office)


# In[10]:


# ERROR - one entry is still 'JUDGE OF THE COUNTY COURT -' #fixed
df[df.office == 'JUDGE OF THE COUNTY COURT -'][['office']].drop_duplicates()


# In[11]:


df.special.unique()


# In[12]:


df['special'] = df['special'].replace({False:'FALSE'})
df['writein'] = df['writein'].astype(str).apply(lambda x: x.upper()) #.replace({False:'FALSE'})
df.loc[df.office.str.contains('UNEXP'),'special'] = 'TRUE'
print(df.special.unique())
df.writein.unique()


# In[13]:


df.district.unique()


# In[14]:


df[df.party_detailed==''].office.unique()


# In[15]:


df.loc[(df.party_detailed=='')&~(df.office.str.contains('COUNTY'))&~(df.office.str.contains('STATE ISSUE 1')), 'party_detailed'] = 'NONPARTISAN'
df.loc[df.party_detailed=='NONPARTISAN', 'party_simplified'] = 'NONPARTISAN'


# In[ ]:


df.loc[df.office.str.contains('JUDGE OF THE COUNTY COURT'),'party_detailed']


# In[47]:


df[df.party_detailed=='NONPARTISAN'].office.unique()


# In[ ]:





# 8. Investigate candidates "JIM HUGHES" and "JOE MILLER", who appear in different rows with multiple party affiliations.

# In[48]:


df[df.candidate=='JIM HUGHES'][['candidate','office','party_detailed','district','county_name']].drop_duplicates()


# In[49]:


df[df.candidate=='JOE MILLER'][['candidate','office','party_detailed','district','county_name']].drop_duplicates()


# In[50]:


df = df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "candidate", 
                     "district","dataverse","stage", "special", "writein","date", "year","county_name","county_fips",
                     "jurisdiction_name", "jurisdiction_fips","state", "state_po","state_fips", "state_cen", 
                   "state_ic", "readme_check",'magnitude']].copy()

df=df.replace('  ', ' ', regex = True)
df = df.applymap(lambda x: x.strip() if type(x) == str else x)


# In[53]:


df.to_csv(r"2018-oh-precinct-updated.csv",quoting=csv.QUOTE_NONNUMERIC,index=False)


# In[52]:


df.columns


# In[ ]:




