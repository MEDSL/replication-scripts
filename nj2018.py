#!/usr/bin/env python
# coding: utf-8

# - ~Add columns {'date', 'magnitude', 'readme_check', 'jurisdiction_fips', 'county_fips'}.~
# - ~Remove periods and commas from candidate names. Make sure double initial names remain separated afterwards (e.g. ASHISH ''A.J.'' JOSHI to ASHISH "A J" JOSHI)~
# - ~Replace sequences of single quotation marks surrounding candidate nicknames with a single pair of double quotation marks (e.g. see above and EVAN S. 'STEVE' GILLINGHAM to EVAN S "STEVE" GILLINGHAM).~
# - ~Move nicknames after all names (e.g. ELIZABETH 'BETSY' A. KALBER BAGLIO to ELIZABETH A KALBER "BETSY" BAGLIO).~
# - Invesitgate candidates such as 1. EMERGENCY INFORMATION AM RADIO STATION and make sure they are standardized correctly.
# - ~Make office=BALLOTS CAST have dataverse=''.~
# - Standardize local office names (only if necessary).
# - ~Zero-pad numerical districts so they have length three.~
# - ~Some candidates appear as running with multiple parties (e.g. MADELYN R. HOFFMAN appears as GREEN, OTHER, INDEPENDENT). Investigate such instances and, if not correct, make sure the candidate has the same party in all rows.~
# - ~Fix typo in party name HONESTY, INGEGRITY, COMPASSION to HONESTY, INTEGRITY, COMPASSION (if appropriate).~
# - ~Replace [WRITE-IN] with WRITEIN in the candidate column.~

# In[1]:


import pandas as pd
import numpy as np
import os
import csv
import re

official_dtypes = {'precinct':str,'office':str, 'party_detailed':str, 
'party_simplified':str,'mode':str,'votes':int, 'county_name':str, 
'county_fips':str, 'jurisdiction_name':str,'jurisdiction_fips':str, 'candidate':str, 
'district':str, 'dataverse':str,'year':int, 'stage':str, 'state':str, 'special':str, 
'writein':str, 'state_po':str, 'state_fips':str, 'state_cen':str, 'state_ic':str, 
'date':str, 'readme_check':str,'magnitude':int}
df = pd.read_csv('2018-nj-precinct-autoadapted.csv', dtype = official_dtypes)
df = df.fillna("")
df = df.replace('""',"")


### FIXES TO ADDRESS DUPLICATES, caused by missing district info, special info, or scraping errors

## Mercer

# designating unex freeholder as special (prevent duplicates)
df.loc[107584:108129,'special']='TRUE'

### Union
# missed special
df.loc[14918:16600,'special']='TRUE'

### Essex
#missed special
df.loc[154849:154884,'special'] = 'TRUE'

### Warren
#manual scraping error fix to prevent dup
df.loc[(df['county_name']=='WARREN')&
      (df['precinct']=='WHITE 6')&
      (df['office']=='US HOUSE')&
      (df['district']=='5')&
       (df['candidate']=='OVERVOTES')&
      (df['party_detailed']=='')&
      (df['votes']==27),'office'] = 'US SENATE'

df.loc[(df['county_name']=='WARREN')&
      (df['precinct']=='WHITE 6')&
      (df['office']=='US SENATE')&
      (df['district']=='5')&
       (df['candidate']=='OVERVOTES')&
      (df['party_detailed']=='')&
      (df['votes']==27),'district'] = '006'

df.loc[(df['county_name']=='WARREN')&
      (df['precinct']=='WHITE 6')&
      (df['office']=='US SENATE')&
      (df['district']=='006')&
       (df['candidate']=='OVERVOTES')&
      (df['party_detailed']=='')&
      (df['votes']==27),'votes'] = 1


# In[3]:


df['date'] = '2018-11-06'
df['readme_check'] = 'FALSE'


# In[4]:


# After county name fix, append on fips codes
fips = pd.read_csv('../../../help-files/county-fips-codes.csv')

fips = fips.applymap(str)
fips['state'] = fips['state'].str.upper()

df=df.applymap(lambda x: x.strip() if type(x)==str else x)
df = pd.merge(df, fips, on = ['state','county_name'], 
             how = 'left')


# In[5]:


df['jurisdiction_fips'] = df['county_fips']


# In[6]:


df.loc[df.office.str.contains('B.H. TOWN COUN. 3 YR TERM (2)'), 'magnitude'] = 2
df.loc[df.office.str.contains('BERKELEY HEIGHTS BOARD OF EDUCATION (2)'), 'magnitude'] = 2
df.loc[df.office.str.contains('MOUNTAINSIDE BOARD OF EDUCATION (2)'), 'magnitude'] = 2
df.loc[df.office.str.contains('NEW PROVIDENCE BOARD OF EDUCATION (3)'), 'magnitude'] = 3
df.loc[df.office.str.contains('SCOTCH PLAINS BOARD OF EDUCATION (3)'), 'magnitude'] = 3
df.loc[df.office.str.contains('SCOTCH PLAINS TOWNSHIP COUNCIL (3)'), 'magnitude'] = 3
df.loc[df.office.str.contains('SPRINGFIELD TOWNSHIP COMMITTEE (2)'), 'magnitude'] = 2
df.loc[df.office.str.contains('UNION TOWNSHIP COMMITTEE (2)'), 'magnitude'] = 2


# In[7]:


df['candidate'] = df['candidate'].str.replace("\.", " ",regex=True)
df['candidate'] = df['candidate'].str.replace(",", "",regex=True)
df['candidate'] = df['candidate'].str.replace('\s+', ' ',regex=True)


# In[8]:


def cleanCand(x):
    if "'" in x: 
        if x.count("'") >= 2:
            x = x.replace("'", '"')
            return x
        else:
            return x
    else: return x
    
df['candidate'] = df['candidate'].apply(cleanCand)


# In[9]:


df['candidate'] = df['candidate'].replace({'NGUTOR ""JUSTICE"" IFAN': 'NGUTOR "JUSTICE" IFAN',
                                           'ELIZABETH "BETSY" A KALBER BAGLIO': 'ELIZABETH A KALBER "BETSY" BAGLIO',
                                           'MINKOU ""MINKYO"" CHENETTE': 'MINKOU "MINKYO" CHENETTE',
                                           'ASHISH ""A J "" JOSHI': 'ASHISH "A J" JOSHI',
                                           '[WRITE-IN]': 'WRITEIN'
                                          })


# In[10]:


df.loc[df['office'] == 'BALLOTS CAST', 'dataverse'] = ''
df.loc[df['office'] == 'US SENATE', 'dataverse'] = 'SENATE'

# In[11]:


# In[12]:


df['party_detailed'] = df['party_detailed'].replace({'HONESTY, INGEGRITY, COMPASSION': 'HONESTY, INTEGRITY, COMPASSION'})


# In[13]:


def district(x):
    if x == '':
        return '' 
    else:
        return x.zfill(3)
df['district'] = df['district'].apply(district)


# In[14]:


df.loc[df['office'] == 'BALLOTS CAST', 'dataverse'] = ''


# In[15]:


df.loc[df['candidate'] == 'MAHMOUD MAHMOUD', 'party_detailed'] = 'DEMOCRAT'
df.loc[df['candidate'] == 'MAHMOUD MAHMOUD', 'party_simplified'] = 'DEMOCRAT'

df.loc[df['candidate'] == 'JOHN QUATTROCCHI', 'party_detailed'] = 'REPUBLICAN'
df.loc[df['candidate'] == 'JOHN QUATTROCCHI', 'party_simplified'] = 'REPUBLICAN'

df.loc[df['candidate'] == 'MADELYN R HOFFMAN', 'party_detailed'] = 'GREEN'
df.loc[df['candidate'] == 'MADELYN R HOFFMAN', 'party_simplified'] = 'OTHER'


##### DC FIXES ##########
df.loc[df['office'].str.contains('UNEX'), 'special'] = 'TRUE'
df.loc[df['district'].str.contains('UNEX'), 'special'] = 'TRUE'

df['candidate'] = df['candidate'].replace('PERSONAL CHOICE','WRITEIN',regex=False)
df.loc[df['candidate']=='WRITEIN', 'writein'] = 'TRUE'
df.loc[df['candidate']=='WRITEIN', 'party_detailed'] = ''
df.loc[df['candidate']=='WRITEIN', 'party_simplified'] = ''

def fill_missing_parties():
    #creates dictionary with keys as candidates/office pairs with multiple parties, values as the non-blank party
    df['party_detailed'] = df['party_detailed'].fillna('')
    candidate_parties = df.groupby(['candidate','office'])['party_detailed'].unique()
    correct_pairing = dict()
    for (candidate, parties) in candidate_parties.iteritems():
        if (len(parties) > 1) and (len(parties) <3):
            parties = list(parties)
            correct_pairing[candidate] = parties[0]        
    candidates=list(correct_pairing.keys())
    #loops through and assigns each candidate/office pair to nonblank party
    for candidate_office in candidates:
        df.loc[(df['candidate']==candidate_office[0])&(df['office']==candidate_office[1]),
               'party_detailed'] = correct_pairing[candidate_office]
# run, Bergen county missing all party info
fill_missing_parties()

def get_simplified(x):
    if x in ['DEMOCRAT','REPUBLICAN','LIBERTARIAN','NONPARTISAN',""]: return x
    else: return "OTHER"
df['party_simplified'] = df.party_detailed.apply(get_simplified)

# fix district
def fix_district(x):
  if "WARD" in x: return (re.findall('\d+', x)[0]).zfill(3)
  if "UNEX" in x: return ""
  else: return x
df['district'] = df.district.apply(fix_district)

# get magnitude from office field
df['get_mag'] = [int(re.findall('\d+', i)[-1]) if len(re.findall('\d+', i))>=1 else 1 for i in df['office']]
df['magnitude'] = np.where(df['office'].str.contains('\(\d+\)'), df['get_mag'], 1)
#https://ballotpedia.org/New_Jersey_state_legislative_special_elections,_2018
df.loc[(df['office']=='STATE HOUSE')&(df['special']=='TRUE')&(df['district'].isin(['015','038'])),'magnitude'] = 2
###########################

# Final step: Remove all trailing white space and put columns in correct order. 
df=df.applymap(lambda x: x.strip() if type(x)==str else x)

df=df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "county_name", "county_fips", "jurisdiction_name",
                      "jurisdiction_fips", "candidate", "district", "dataverse", "year", "stage", "state", "special", "writein", "state_po",
                      "state_fips", "state_cen", "state_ic", "date", "readme_check", "magnitude"]]

df.loc[df['office']=='US SENATE','district'] = 'STATEWIDE'
# remove 0 vote writein
df = df[~((df['votes']==0)&(df['candidate']=='WRITEIN'))].drop_duplicates().copy()
# readmecheck
df['readme_check'] = np.where(df['county_name'].isin(["ESSEX",'HUNTERDON','SALEM']), 'TRUE', df['readme_check'])

df.to_csv('2018-nj-precinct-general-updated.csv',quoting=csv.QUOTE_NONNUMERIC, index=False)



# In[ ]:




